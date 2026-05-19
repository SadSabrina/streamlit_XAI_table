import streamlit as st
from xai_table_functions import load_data, filter_data

st.set_page_config(
    page_title="XAI Library Navigator",
    page_icon="🔍",
    layout="wide",
)

st.title("XAI Library Navigator")
st.markdown(
    "Find a library for interpreting your ML model. "
    "Filter by paradigm, data modality, and method type."
)

df = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    search = st.text_input("🔍 Search", placeholder="shap, counterfactual, LLM…")

    paradigms = st.multiselect(
        "Paradigm",
        ["Classic XAI", "Mechanistic", "Hybrid"],
        help="Classic XAI — post-hoc methods. Mechanistic — analysis of model internals.",
    )

    all_modalities = sorted({
        v.strip()
        for cell in df["modality"].dropna()
        for v in str(cell).split(",")
        if v.strip()
    })
    modalities = st.multiselect("Data modality", all_modalities)

    all_methods = sorted({
        v.strip()
        for cell in df["method_category"].dropna()
        for v in str(cell).split(",")
        if v.strip()
    })
    methods = st.multiselect("Method type", all_methods)

    show_inactive = st.checkbox("Show inactive libraries", value=False)

    st.divider()
    st.caption(
        "**Classic XAI** — post-hoc explanations (SHAP, LIME, gradients, counterfactuals)\n\n"
        "**Mechanistic** — internal structure analysis (circuits, SAE, steering, activation patching)\n\n"
        "**Hybrid** — both approaches"
    )
    st.divider()
    st.markdown("Tg: [@sabrina_sadiekh](https://t.me/sabrina_sadiekh)")
    st.markdown("[DataBlog](https://t.me/jdata_blog)")

# ── Filter & sort ────────────────────────────────────────────────────────────
filtered = filter_data(df, paradigms, modalities, methods, search, show_inactive)
filtered = filtered.sort_values("stars", ascending=False, na_position="last")

# ── Stats ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", len(filtered))
c2.metric("Classic XAI", (filtered["paradigm"] == "Classic XAI").sum())
c3.metric("Mechanistic", (filtered["paradigm"] == "Mechanistic").sum())
c4.metric("Hybrid", (filtered["paradigm"] == "Hybrid").sum())

# ── Table ────────────────────────────────────────────────────────────────────
if filtered.empty:
    st.info("Nothing found — try adjusting the filters.")
else:
    display = filtered[[
        "library", "url", "paradigm", "modality",
        "method_category", "scope", "model_agnostic",
        "stars", "last_updated", "description_en",
    ]].copy()

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "library": st.column_config.TextColumn("Library", width=150),
            "url": st.column_config.LinkColumn("🔗", display_text="open", width=90),
            "paradigm": st.column_config.TextColumn("Paradigm", width=130),
            "modality": st.column_config.TextColumn("Modality", width=160),
            "method_category": st.column_config.TextColumn("Method type", width=220),
            "scope": st.column_config.TextColumn("Scope", width=80),
            "model_agnostic": st.column_config.TextColumn("Agnostic", width=85),
            "stars": st.column_config.NumberColumn("⭐", format="%d ★", width=80),
            "last_updated": st.column_config.DateColumn("Last update", format="MMM YYYY", width=100),
            "description_en": st.column_config.TextColumn("Description", width=300),
        },
    )

# ── Resources ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "**Useful resources:** "
    "[Interpretable ML Book](https://christophm.github.io/interpretable-ml-book/) · "
    "[Awesome LLM Interpretability](https://github.com/JShollaj/awesome-llm-interpretability) · "
    "[DataBlog](https://t.me/jdata_blog) · "
    "[XAI tutorials](https://github.com/SadSabrina/XAI-open_materials)"
)
