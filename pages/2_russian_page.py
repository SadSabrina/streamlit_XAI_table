import streamlit as st
from xai_table_functions import load_data, filter_data

st.title("XAI Library Navigator")
st.markdown(
    "Подберите библиотеку для интерпретации модели под вашу задачу. "
    "Фильтруйте по парадигме, модальности данных и типу метода."
)

df = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Фильтры")

    search = st.text_input("🔍 Поиск", placeholder="shap, counterfactual, LLM…")

    paradigms = st.multiselect(
        "Парадигма",
        ["Classic XAI", "Mechanistic", "Hybrid"],
        help="Classic XAI — post-hoc методы. Mechanistic — анализ внутренней структуры модели.",
    )

    all_modalities = sorted({
        v.strip()
        for cell in df["modality"].dropna()
        for v in str(cell).split(",")
        if v.strip()
    })
    modalities = st.multiselect("Модальность данных", all_modalities)

    all_methods = sorted({
        v.strip()
        for cell in df["method_category"].dropna()
        for v in str(cell).split(",")
        if v.strip()
    })
    methods = st.multiselect("Тип метода", all_methods)

    show_inactive = st.checkbox("Показывать неактивные", value=False)

    st.divider()
    st.caption(
        "**Classic XAI** — post-hoc объяснения (SHAP, LIME, градиенты, контрфактуалы)\n\n"
        "**Mechanistic** — анализ внутренней структуры (circuits, SAE, steering, activation patching)\n\n"
        "**Hybrid** — оба подхода"
    )
    st.divider()
    st.markdown("Tg: [@sabrina_sadiekh](https://t.me/sabrina_sadiekh)")
    st.markdown("[DataBlog](https://t.me/jdata_blog)")

# ── Filter & sort ────────────────────────────────────────────────────────────
filtered = filter_data(df, paradigms, modalities, methods, search, show_inactive)
filtered = filtered.sort_values("stars", ascending=False, na_position="last")

# ── Stats ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Всего", len(filtered))
c2.metric("Classic XAI", (filtered["paradigm"] == "Classic XAI").sum())
c3.metric("Mechanistic", (filtered["paradigm"] == "Mechanistic").sum())
c4.metric("Hybrid", (filtered["paradigm"] == "Hybrid").sum())

# ── Table ────────────────────────────────────────────────────────────────────
if filtered.empty:
    st.info("Ничего не найдено — попробуйте изменить фильтры.")
else:
    display = filtered[[
        "library", "url", "paradigm", "modality",
        "method_category", "scope", "model_agnostic",
        "stars", "active", "description_en",
    ]].copy()

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "library": st.column_config.TextColumn("Библиотека", width=150),
            "url": st.column_config.LinkColumn("🔗", display_text="открыть", width=90),
            "paradigm": st.column_config.TextColumn("Парадигма", width=130),
            "modality": st.column_config.TextColumn("Модальность", width=160),
            "method_category": st.column_config.TextColumn("Тип метода", width=220),
            "scope": st.column_config.TextColumn("Scope", width=80),
            "model_agnostic": st.column_config.TextColumn("Agnostic", width=85),
            "stars": st.column_config.NumberColumn("⭐", format="%d ★", width=80),
            "active": st.column_config.TextColumn("Активна", width=75),
            "description_en": st.column_config.TextColumn("Описание", width=300),
        },
    )

# ── Resources ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "**Полезные ресурсы:** "
    "[Interpretable ML Book](https://christophm.github.io/interpretable-ml-book/) · "
    "[Awesome LLM Interpretability](https://github.com/JShollaj/awesome-llm-interpretability) · "
    "[DataBlog](https://t.me/jdata_blog) · "
    "[Туториалы по XAI](https://github.com/SadSabrina/XAI-open_materials)"
)
