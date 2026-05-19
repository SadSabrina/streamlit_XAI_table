"""
Enrichment script: fetches GitHub metadata for all XAI libraries
and outputs data/xai_libraries.csv with the new schema.

GitHub public API: 60 req/hour unauthenticated.
Set GITHUB_TOKEN env var (free, no scopes needed) for 5000 req/hour:
  export GITHUB_TOKEN=ghp_...
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


# ── Master library list ────────────────────────────────────────────────────────
# github: "owner/repo" or None (platforms, docs-only sites)
# Fields that can't be auto-derived are filled manually here.
LIBRARIES = [
    # ── Classic XAI ─────────────────────────────────────────────────────────
    {
        "library": "SHAP",
        "url": "https://shap.readthedocs.io/en/latest/",
        "github": "shap/shap",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, SHAP",
        "modality": "Tabular, Images, Text, Genomic",
        "framework": "scikit-learn, XGBoost, LightGBM, CatBoost, Keras, tensorflow, pytorch, pyspark, transformers",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "LIME",
        "url": "https://github.com/marcotcr/lime",
        "github": "marcotcr/lime",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, LIME",
        "modality": "Tabular, Images, Text",
        "framework": "scikit-learn, Keras, tensorflow, pytorch",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "eli5",
        "url": "https://eli5.readthedocs.io/en/latest/",
        "github": "eli5-org/eli5",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Feature Importance",
        "modality": "Tabular, Images, Text, Graph",
        "framework": "scikit-learn, XGBoost, LightGBM, CatBoost, Keras, sklearn-crfsuite, lightning",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "Captum",
        "url": "https://captum.ai/",
        "github": "pytorch/captum",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient",
        "modality": "Tabular, Images, Text",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
    },
    {
        "library": "interpretML",
        "url": "https://interpret.ml/docs/intro.html",
        "github": "interpretml/interpret",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Feature Importance, Counterfactual",
        "modality": "Tabular",
        "framework": "scikit-learn",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "alibi",
        "url": "https://github.com/SeldonIO/alibi",
        "github": "SeldonIO/alibi",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Counterfactual, Anchors",
        "modality": "Tabular, Images, Text, Graph",
        "framework": "scikit-learn, Keras, tensorflow, pytorch",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "DALEX",
        "url": "https://dalex.drwhy.ai/",
        "github": "ModelOriented/DALEX",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Feature Importance",
        "modality": "Tabular",
        "framework": "scikit-learn, Keras, tensorflow, pytorch, XGBoost, LightGBM, CatBoost, H2O",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "shapash",
        "url": "https://github.com/MAIF/shapash",
        "github": "MAIF/shapash",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, SHAP",
        "modality": "Tabular",
        "framework": "scikit-learn, XGBoost, LightGBM, CatBoost",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "AIX360",
        "url": "https://github.com/Trusted-AI/AIX360",
        "github": "Trusted-AI/AIX360",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Counterfactual, Feature Importance",
        "modality": "Tabular, Images, Text",
        "framework": "scikit-learn, tensorflow",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "OmniXAI",
        "url": "https://github.com/salesforce/OmniXAI",
        "github": "salesforce/OmniXAI",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Counterfactual, SHAP, LIME",
        "modality": "Tabular, Images, Text, Time Series",
        "framework": "Keras, pytorch",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "dice-ml",
        "url": "https://interpret.ml/DiCE/",
        "github": "interpretml/DiCE",
        "paradigm": "Classic XAI",
        "method_category": "Counterfactual",
        "modality": "Tabular",
        "framework": "scikit-learn, Keras, tensorflow, pytorch",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "CARLA",
        "url": "https://github.com/carla-recourse/CARLA",
        "github": "carla-recourse/CARLA",
        "paradigm": "Classic XAI",
        "method_category": "Counterfactual",
        "modality": "Tabular",
        "framework": "scikit-learn, Keras, tensorflow, pytorch, XGBoost",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "anchors",
        "url": "https://github.com/marcotcr/anchor",
        "github": "marcotcr/anchor",
        "paradigm": "Classic XAI",
        "method_category": "Anchors",
        "modality": "Tabular, Text",
        "framework": "scikit-learn, pytorch",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "COLA",
        "url": "https://github.com/understanding-ml/COLA",
        "github": "understanding-ml/COLA",
        "paradigm": "Classic XAI",
        "method_category": "Counterfactual, SHAP",
        "modality": "Tabular",
        "framework": "scikit-learn",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "Quantus",
        "url": "https://github.com/understandable-machine-intelligence-lab/Quantus",
        "github": "understandable-machine-intelligence-lab/Quantus",
        "paradigm": "Classic XAI",
        "method_category": "Evaluation Metrics",
        "modality": "Tabular, Images",
        "framework": "Keras, tensorflow, pytorch, transformers",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "xai_evals",
        "url": "https://pypi.org/project/xai-evals/",
        "github": None,
        "paradigm": "Classic XAI",
        "method_category": "Evaluation Metrics",
        "modality": "Tabular, Images",
        "framework": "pytorch, tensorflow, scikit-learn, XGBoost",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "explabox",
        "url": "https://github.com/MarcelRobeer/explabox",
        "github": "MarcelRobeer/explabox",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Evaluation Metrics",
        "modality": "Text",
        "framework": "scikit-learn, Keras, tensorflow, pytorch",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "pdpbox",
        "url": "https://pdpbox.readthedocs.io/en/latest/",
        "github": "SauceCat/PDPbox",
        "paradigm": "Classic XAI",
        "method_category": "Feature Importance",
        "modality": "Tabular",
        "framework": "scikit-learn",
        "scope": "Global",
        "model_agnostic": "Yes",
    },
    {
        "library": "treeinterpreter",
        "url": "https://github.com/andosa/treeinterpreter",
        "github": "andosa/treeinterpreter",
        "paradigm": "Classic XAI",
        "method_category": "Feature Importance",
        "modality": "Tabular",
        "framework": "scikit-learn",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "pyXAI",
        "url": "https://github.com/crillab/pyxai",
        "github": "crillab/pyxai",
        "paradigm": "Classic XAI",
        "method_category": "Feature Importance",
        "modality": "Tabular",
        "framework": "scikit-learn, XGBoost, LightGBM",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "SALib",
        "url": "https://salib.readthedocs.io/en/latest/",
        "github": "SALib/SALib",
        "paradigm": "Classic XAI",
        "method_category": "Sensitivity Analysis",
        "modality": "Tabular",
        "framework": "framework-agnostic",
        "scope": "Global",
        "model_agnostic": "Yes",
    },
    {
        "library": "deeplift",
        "url": "https://github.com/kundajelab/deeplift",
        "github": "kundajelab/deeplift",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient",
        "modality": "Tabular, Images, Genomic",
        "framework": "Keras",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "zennit",
        "url": "https://github.com/chr5tphr/zennit",
        "github": "chr5tphr/zennit",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient, LRP",
        "modality": "Tabular, Images, Text",
        "framework": "pytorch",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "tf-explain",
        "url": "https://tf-explain.readthedocs.io/en/latest/",
        "github": "sicara/tf-explain",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient, Grad-CAM",
        "modality": "Tabular, Images, Text",
        "framework": "tensorflow",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "saliency",
        "url": "https://github.com/pair-code/saliency",
        "github": "pair-code/saliency",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient",
        "modality": "Images",
        "framework": "tensorflow, pytorch",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "xaitk-saliency",
        "url": "https://github.com/XAITK/xaitk-saliency",
        "github": "XAITK/xaitk-saliency",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient",
        "modality": "Images",
        "framework": "pytorch",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "easy_explain",
        "url": "https://github.com/stavrostheocharis/easy_explain",
        "github": "stavrostheocharis/easy_explain",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Grad-CAM",
        "modality": "Images",
        "framework": "pytorch",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "pytorch_explain",
        "url": "https://github.com/pietrobarbiero/pytorch_explain",
        "github": "pietrobarbiero/pytorch_explain",
        "paradigm": "Classic XAI",
        "method_category": "Concept-based",
        "modality": "Images",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
    },
    {
        "library": "bertviz",
        "url": "https://github.com/jessevig/bertviz",
        "github": "jessevig/bertviz",
        "paradigm": "Classic XAI",
        "method_category": "Attention Visualization",
        "modality": "Text",
        "framework": "transformers",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "transformers-interpret",
        "url": "https://github.com/cdpierse/transformers-interpret",
        "github": "cdpierse/transformers-interpret",
        "paradigm": "Classic XAI",
        "method_category": "Attribution",
        "modality": "Text, Images",
        "framework": "transformers",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "interpret-text",
        "url": "https://github.com/interpretml/interpret-text",
        "github": "interpretml/interpret-text",
        "paradigm": "Classic XAI",
        "method_category": "Attribution",
        "modality": "Text",
        "framework": "scikit-learn, pytorch",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "Explainer Dashboard",
        "url": "https://explainerdashboard.readthedocs.io/en/latest/",
        "github": "oegedijk/explainerdashboard",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, SHAP, Feature Importance",
        "modality": "Tabular, Images, Text",
        "framework": "scikit-learn, skorch",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "skater",
        "url": "https://github.com/oracle/Skater",
        "github": "oracle/Skater",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Feature Importance",
        "modality": "Tabular, Images, Text",
        "framework": "scikit-learn, XGBoost, Keras",
        "scope": "Both",
        "model_agnostic": "Yes",
        "note": "Deprecated / not maintained",
    },
    {
        "library": "graphviz-ML",
        "url": "https://github.com/MrColoratus/graphviz-ML",
        "github": "MrColoratus/graphviz-ML",
        "paradigm": "Classic XAI",
        "method_category": "Feature Importance",
        "modality": "Tabular",
        "framework": "scikit-learn, SciPy",
        "scope": "Global",
        "model_agnostic": "No",
    },
    # ── Time Series ──────────────────────────────────────────────────────────
    {
        "library": "TSInterpret",
        "url": "https://fzi-forschungszentrum-informatik.github.io/TSInterpret/",
        "github": "fzi-forschungszentrum-informatik/TSInterpret",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Counterfactual, LIME",
        "modality": "Time Series",
        "framework": "pytorch, tensorflow, sklearn",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "TimeInterpret",
        "url": "https://github.com/josephenguehard/time_interpret",
        "github": "josephenguehard/time_interpret",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient",
        "modality": "Time Series",
        "framework": "pytorch",
        "scope": "Local",
        "model_agnostic": "No",
    },
    {
        "library": "TSCaptum",
        "url": "https://github.com/mlgig/tscaptum",
        "github": "mlgig/tscaptum",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Gradient",
        "modality": "Time Series",
        "framework": "pytorch",
        "scope": "Local",
        "model_agnostic": "No",
    },
    # ── Multi-modal / Multi-purpose ──────────────────────────────────────────
    {
        "library": "PnPXAI",
        "url": "https://openxaiproject.github.io/pnpxai/",
        "github": "OpenXAIProject/PnPXAI",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, SHAP, LIME, Gradient, Evaluation Metrics",
        "modality": "Tabular, Images, Text, Time Series",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "Yes",
    },
    {
        "library": "DHook",
        "url": "https://github.com/Xmaster6y/tdhook",
        "github": "Xmaster6y/tdhook",
        "paradigm": "Hybrid",
        "method_category": "Attribution, Gradient, LRP, Grad-CAM, Probing, Activation Patching, SAE",
        "modality": "Images, Text, Multimodal",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
    },
    # ── LLM / NLP ────────────────────────────────────────────────────────────
    {
        "library": "ICX360",
        "url": "https://github.com/IBM/ICX360",
        "github": "IBM/ICX360",
        "paradigm": "Classic XAI",
        "method_category": "Attribution, Contrastive",
        "modality": "Text, LLM",
        "framework": "transformers",
        "scope": "Local",
        "model_agnostic": "Yes",
    },
    {
        "library": "Interpreto",
        "url": "https://for-sight-ai.github.io/interpreto/",
        "github": "FOR-sight-ai/interpreto",
        "paradigm": "Hybrid",
        "method_category": "Attribution, Gradient, SHAP, Concept-based, SAE",
        "modality": "Text, LLM",
        "framework": "transformers",
        "scope": "Both",
        "model_agnostic": "No",
    },
    # ── Mechanistic Interpretability ─────────────────────────────────────────
    {
        "library": "TransformerLens",
        "url": "https://transformerlensorg.github.io/TransformerLens/",
        "github": "TransformerLensOrg/TransformerLens",
        "paradigm": "Mechanistic",
        "method_category": "Circuit Analysis, Activation Patching, Logit Lens, Attention Analysis",
        "modality": "LLM",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
    },
    {
        "library": "SAELens",
        "url": "https://github.com/jbloomAus/SAELens",
        "github": "jbloomAus/SAELens",
        "paradigm": "Mechanistic",
        "method_category": "SAE",
        "modality": "LLM",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
    },
    {
        "library": "Neuronpedia",
        "url": "https://www.neuronpedia.org/",
        "github": None,
        "paradigm": "Mechanistic",
        "method_category": "SAE",
        "modality": "LLM",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
        "note": "Platform / explorer for SAE features, not a pip package",
    },
    {
        "library": "Prisma",
        "url": "https://github.com/Prisma-Multimodal/ViT-Prisma",
        "github": "Prisma-Multimodal/ViT-Prisma",
        "paradigm": "Mechanistic",
        "method_category": "Circuit Analysis, Activation Patching, SAE, Logit Lens, Attention Analysis",
        "modality": "Images, Multimodal",
        "framework": "pytorch",
        "scope": "Both",
        "model_agnostic": "No",
    },
    {
        "library": "pyvene",
        "url": "https://github.com/stanfordnlp/pyvene",
        "github": "stanfordnlp/pyvene",
        "paradigm": "Mechanistic",
        "method_category": "Activation Patching, Causal Tracing, Probing",
        "modality": "LLM, Text",
        "framework": "pytorch, transformers",
        "scope": "Both",
        "model_agnostic": "No",
    },
    {
        "library": "repeng",
        "url": "https://github.com/vgel/repeng",
        "github": "vgel/repeng",
        "paradigm": "Mechanistic",
        "method_category": "Steering Vectors",
        "modality": "LLM",
        "framework": "pytorch, transformers",
        "scope": "Global",
        "model_agnostic": "No",
    },
    {
        "library": "pyreft",
        "url": "https://github.com/stanfordnlp/pyreft",
        "github": "stanfordnlp/pyreft",
        "paradigm": "Mechanistic",
        "method_category": "Steering Vectors",
        "modality": "LLM",
        "framework": "pytorch, transformers",
        "scope": "Global",
        "model_agnostic": "No",
    },
    {
        "library": "EasyEdit",
        "url": "https://github.com/zjunlp/EasyEdit",
        "github": "zjunlp/EasyEdit",
        "paradigm": "Mechanistic",
        "method_category": "Knowledge Editing",
        "modality": "LLM",
        "framework": "pytorch, transformers",
        "scope": "Global",
        "model_agnostic": "No",
    },
    {
        "library": "EasySteer",
        "url": "https://github.com/ZJU-REAL/EasySteer",
        "github": "ZJU-REAL/EasySteer",
        "paradigm": "Mechanistic",
        "method_category": "Steering Vectors",
        "modality": "LLM",
        "framework": "pytorch, transformers",
        "scope": "Global",
        "model_agnostic": "No",
    },
    {
        "library": "NNsight",
        "url": "https://github.com/ndif-team/nnsight",
        "github": "ndif-team/nnsight",
        "paradigm": "Mechanistic",
        "method_category": "Activation Patching, Probing",
        "modality": "LLM, Images, Multimodal",
        "framework": "pytorch, transformers",
        "scope": "Both",
        "model_agnostic": "No",
    },
]


def fetch_github(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 404:
            print(f"  404: {repo}")
            return {}
        if r.status_code == 403:
            print("  Rate limit hit — set GITHUB_TOKEN env var for more requests")
            return {}
        r.raise_for_status()
        data = r.json()
        pushed = data.get("pushed_at", "")
        last_updated = pushed[:10] if pushed else ""
        return {
            "description_en": data.get("description") or "",
            "stars": data.get("stargazers_count", 0),
            "last_updated": last_updated,
            "active": _is_active(last_updated),
            "topics": ", ".join(data.get("topics", [])),
        }
    except Exception as e:
        print(f"  Error fetching {repo}: {e}")
        return {}


def _is_active(last_updated: str) -> str:
    if not last_updated:
        return "Unknown"
    try:
        delta = datetime.now(timezone.utc) - datetime.fromisoformat(
            last_updated + "T00:00:00+00:00"
        )
        return "Yes" if delta.days < 730 else "No"
    except Exception:
        return "Unknown"


def enrich():
    rows = []
    total = len(LIBRARIES)
    for i, lib in enumerate(LIBRARIES, 1):
        print(f"[{i}/{total}] {lib['library']}")
        row = {k: v for k, v in lib.items() if k != "github"}
        row.setdefault("note", "")
        row.update(
            {"description_en": "", "stars": "", "last_updated": "", "active": "", "topics": ""}
        )
        if lib.get("github"):
            gh = fetch_github(lib["github"])
            row.update(gh)
            time.sleep(0.5)  # stay within rate limits

        rows.append(row)

    df = pd.DataFrame(rows)
    # canonical column order
    cols = [
        "library", "url", "paradigm", "modality", "framework",
        "method_category", "scope", "model_agnostic",
        "description_en", "stars", "last_updated", "active", "topics", "note",
    ]
    df = df.reindex(columns=cols)
    out = "data/xai_libraries.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved {len(df)} libraries → {out}")
    print(df[["library", "paradigm", "stars", "active"]].to_string())


if __name__ == "__main__":
    enrich()
