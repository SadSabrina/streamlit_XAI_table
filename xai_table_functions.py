import re
import requests
import pandas as pd
from datetime import datetime, timezone

DATA_PATH = "data/xai_libraries.csv"

PARADIGMS = ["Classic XAI", "Mechanistic", "Hybrid"]
MODALITIES = ["Tabular", "Images", "Text", "Time Series", "LLM", "Multimodal", "Graph", "Genomic"]
FRAMEWORKS = [
    "pytorch", "tensorflow", "Keras", "scikit-learn", "transformers",
    "XGBoost", "LightGBM", "CatBoost", "H2O", "pyspark", "framework-agnostic",
]
METHOD_CATEGORIES = [
    "Attribution", "SHAP", "LIME", "Gradient", "Grad-CAM", "LRP",
    "Counterfactual", "Anchors", "Feature Importance", "Sensitivity Analysis",
    "Attention Visualization", "Concept-based", "Evaluation Metrics",
    "Circuit Analysis", "Activation Patching", "Causal Tracing", "Probing",
    "SAE", "Steering Vectors", "Knowledge Editing", "Contrastive", "Logit Lens",
]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["stars"] = pd.to_numeric(df["stars"], errors="coerce")
    df["note"] = df["note"].fillna("")
    return df


def _unique_values(df: pd.DataFrame, column: str) -> list[str]:
    return sorted({
        v.strip()
        for cell in df[column].dropna()
        for v in str(cell).split(",")
        if v.strip()
    })


def filter_data(
    df: pd.DataFrame,
    paradigms: list[str],
    modalities: list[str],
    methods: list[str],
    search: str,
    show_inactive: bool,
) -> pd.DataFrame:
    def matches(cell, selected):
        vals = {v.strip() for v in str(cell).split(",")}
        return bool(vals & set(selected))

    mask = pd.Series(True, index=df.index)

    if paradigms:
        mask &= df["paradigm"].apply(matches, selected=paradigms)
    if modalities:
        mask &= df["modality"].apply(matches, selected=modalities)
    if methods:
        mask &= df["method_category"].apply(matches, selected=methods)
    if search:
        q = search.lower()
        mask &= (
            df["library"].str.lower().str.contains(q, na=False)
            | df["description_en"].str.lower().str.contains(q, na=False)
            | df["method_category"].str.lower().str.contains(q, na=False)
        )
    if not show_inactive:
        mask &= df["active"].isin(["Yes", "Unknown"]) | df["active"].isna()

    return df[mask]


def fetch_github_meta(repo_url: str, token=None) -> dict:
    m = re.search(r"github\.com/([^/]+/[^/?#]+)", repo_url)
    if not m:
        return {"error": "Не удалось распознать GitHub URL"}
    repo = m.group(1).rstrip("/")

    headers = {"Authorization": f"token {token}"} if token else {}
    try:
        r = requests.get(
            f"https://api.github.com/repos/{repo}", headers=headers, timeout=10
        )
        if r.status_code == 404:
            return {"error": f"Репозиторий не найден: {repo}"}
        r.raise_for_status()
        data = r.json()

        pushed = (data.get("pushed_at") or "")[:10]
        if pushed:
            delta = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(pushed + "T00:00:00+00:00")
            ).days
            active = "Yes" if delta < 730 else "No"
        else:
            active = "Unknown"

        return {
            "description_en": data.get("description") or "",
            "stars": int(data.get("stargazers_count") or 0),
            "last_updated": pushed,
            "active": active,
            "topics": ", ".join(data.get("topics") or []),
        }
    except Exception as e:
        return {"error": str(e)}


def append_library(entry: dict) -> None:
    df = load_data()
    new_df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    new_df.to_csv(DATA_PATH, index=False)
