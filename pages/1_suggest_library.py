import os
import requests
import streamlit as st
from xai_table_functions import (
    fetch_github_meta,
    PARADIGMS,
    MODALITIES,
    FRAMEWORKS,
    METHOD_CATEGORIES,
)

st.set_page_config(
    page_title="Suggest a Library",
    page_icon="➕",
    layout="centered",
)


def send_telegram(suggestion: dict) -> bool:
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    except Exception:
        return False

    stars = suggestion.get("stars", "—") or "—"
    text = (
        f"📬 *New library suggestion*\n\n"
        f"*Library:* {suggestion['library']}\n"
        f"*URL:* {suggestion['url']}\n"
        f"*Paradigm:* {suggestion['paradigm']}\n"
        f"*Modality:* {suggestion['modality']}\n"
        f"*Method type:* {suggestion['method_category']}\n"
        f"*Framework:* {suggestion.get('framework') or '—'}\n"
        f"*Scope:* {suggestion['scope']} · "
        f"*Agnostic:* {suggestion['model_agnostic']}\n"
        f"*Stars:* {stars} ⭐ · *Last push:* {suggestion.get('last_updated') or '—'}\n"
        f"*Description:* {suggestion.get('description_en') or '—'}\n"
        f"*Note:* {suggestion.get('note') or '—'}"
    )
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )
    return r.ok


# ── Auto-fill from GitHub ─────────────────────────────────────────────────────
st.title("Suggest a Library / Предложить библиотеку")

st.info(
    "**EN:** Know a library that's missing? Fill in the form below — "
    "I'll review suggestions and add them manually.\n\n"
    "**RU:** Знаете библиотеку, которой нет в списке? Заполните форму — "
    "я просмотрю предложения и добавлю вручную."
)

st.subheader("1. Auto-fill from GitHub / Автозаполнение из GitHub")

github_url = st.text_input(
    "GitHub URL",
    placeholder="https://github.com/owner/repo",
)

if github_url and st.button("Fetch metadata / Загрузить метаданные", type="secondary"):
    with st.spinner("Fetching GitHub API…"):
        token = os.environ.get("GITHUB_TOKEN")
        result = fetch_github_meta(github_url, token)
    if "error" in result:
        st.error(result["error"])
    else:
        st.session_state["gh_meta"] = result
        st.success(
            f"{result.get('stars', 0)} ⭐ · "
            f"last push: {result.get('last_updated', '—')}"
        )

meta = st.session_state.get("gh_meta", {})

# ── Form ──────────────────────────────────────────────────────────────────────
st.subheader("2. Fill in the fields / Заполните поля")

with st.form("suggest_library"):
    library = st.text_input(
        "Library name / Название *",
        placeholder="e.g. SHAP",
    )
    url = st.text_input(
        "Main link (docs or GitHub) / Основная ссылка *",
        value=github_url or "",
    )

    paradigm = st.selectbox("Paradigm / Парадигма *", PARADIGMS)

    modality = st.multiselect("Modality / Модальность *", MODALITIES)
    framework = st.multiselect("Framework / Фреймворк", FRAMEWORKS)
    method_category = st.multiselect("Method type / Тип метода *", METHOD_CATEGORIES)

    col1, col2 = st.columns(2)
    with col1:
        scope = st.selectbox("Scope", ["Both", "Local", "Global"])
    with col2:
        model_agnostic = st.selectbox("Model agnostic", ["Yes", "No"])

    description_en = st.text_area(
        "Description (EN) / Описание",
        value=meta.get("description_en", ""),
        height=80,
        placeholder="Short description — from GitHub or your own words",
    )

    note = st.text_input(
        "Notes / Примечание",
        placeholder="e.g. platform only, niche use case…",
    )

    submitted = st.form_submit_button("Submit suggestion / Отправить", type="primary")

if submitted:
    missing = [
        name for name, val in [
            ("Library name", library),
            ("Link", url),
            ("Modality", modality),
            ("Method type", method_category),
        ]
        if not val
    ]
    if missing:
        st.error(f"Please fill in: {', '.join(missing)}")
    else:
        suggestion = {
            "library": library.strip(),
            "url": url.strip(),
            "paradigm": paradigm,
            "modality": ", ".join(modality),
            "framework": ", ".join(framework),
            "method_category": ", ".join(method_category),
            "scope": scope,
            "model_agnostic": model_agnostic,
            "description_en": description_en.strip(),
            "stars": meta.get("stars", ""),
            "last_updated": meta.get("last_updated", ""),
            "topics": meta.get("topics", ""),
            "note": note.strip(),
        }

        send_telegram(suggestion)

        suggestions = st.session_state.get("suggestions", [])
        suggestions.append(suggestion)
        st.session_state["suggestions"] = suggestions
        st.session_state.pop("gh_meta", None)

        st.success(
            f"✓ Thank you! «{library}» submitted for review. / "
            f"Спасибо! «{library}» отправлена на проверку."
        )
        st.rerun()

if st.session_state.get("suggestions"):
    st.divider()
    st.caption(
        "Submitted this session / Отправлено за эту сессию: "
        + ", ".join(s["library"] for s in st.session_state["suggestions"])
    )
