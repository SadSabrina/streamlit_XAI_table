import os
import streamlit as st
from xai_table_functions import (
    fetch_github_meta,
    append_library,
    PARADIGMS,
    MODALITIES,
    FRAMEWORKS,
    METHOD_CATEGORIES,
)

st.set_page_config(page_title="Добавить библиотеку", page_icon="➕", layout="centered")
st.title("Добавить библиотеку")

# ── Auto-fill from GitHub ─────────────────────────────────────────────────────
st.subheader("1. Автозаполнение из GitHub")
github_url = st.text_input(
    "GitHub URL репозитория",
    placeholder="https://github.com/owner/repo",
)

if github_url and st.button("Загрузить метаданные", type="secondary"):
    with st.spinner("Запрашиваю GitHub API…"):
        token = os.environ.get("GITHUB_TOKEN")
        result = fetch_github_meta(github_url, token)
    if "error" in result:
        st.error(result["error"])
    else:
        st.session_state["gh_meta"] = result
        st.success(
            f"Получено: {result.get('stars', 0)} ⭐ · "
            f"обновлено {result.get('last_updated', '—')} · "
            f"активна: {result.get('active', '?')}"
        )

meta = st.session_state.get("gh_meta", {})

# ── Form ──────────────────────────────────────────────────────────────────────
st.subheader("2. Заполните поля")

with st.form("add_library"):
    library = st.text_input("Название *", placeholder="SHAP")
    url = st.text_input(
        "Основная ссылка (docs / GitHub) *",
        value=github_url or "",
    )

    paradigm = st.selectbox("Парадигма *", PARADIGMS)

    modality = st.multiselect("Модальность *", MODALITIES)
    framework = st.multiselect("Фреймворк", FRAMEWORKS)
    method_category = st.multiselect("Тип метода *", METHOD_CATEGORIES)

    col1, col2 = st.columns(2)
    with col1:
        scope = st.selectbox("Scope", ["Both", "Local", "Global"])
    with col2:
        model_agnostic = st.selectbox("Model agnostic", ["Yes", "No"])

    description_en = st.text_area(
        "Описание (EN)",
        value=meta.get("description_en", ""),
        height=80,
        placeholder="Short description from GitHub or your own",
    )

    col3, col4, col5 = st.columns(3)
    with col3:
        stars = st.number_input("Stars", value=int(meta.get("stars") or 0), min_value=0)
    with col4:
        last_updated = st.text_input("Last updated", value=meta.get("last_updated", ""))
    with col5:
        active_opts = ["Yes", "No", "Unknown"]
        active = st.selectbox(
            "Активна",
            active_opts,
            index=active_opts.index(meta.get("active", "Unknown")),
        )

    note = st.text_input("Примечание", placeholder="Deprecated, platform only, etc.")

    submitted = st.form_submit_button("Сохранить", type="primary")

if submitted:
    missing = [f for f, v in [("Название", library), ("Ссылка", url),
                               ("Модальность", modality), ("Тип метода", method_category)]
               if not v]
    if missing:
        st.error(f"Заполните обязательные поля: {', '.join(missing)}")
    else:
        entry = {
            "library": library.strip(),
            "url": url.strip(),
            "paradigm": paradigm,
            "modality": ", ".join(modality),
            "framework": ", ".join(framework),
            "method_category": ", ".join(method_category),
            "scope": scope,
            "model_agnostic": model_agnostic,
            "description_en": description_en.strip(),
            "stars": stars,
            "last_updated": last_updated.strip(),
            "active": active,
            "topics": meta.get("topics", ""),
            "note": note.strip(),
        }
        append_library(entry)
        st.success(f"✓ Библиотека «{library}» добавлена!")
        st.session_state.pop("gh_meta", None)
        st.rerun()
