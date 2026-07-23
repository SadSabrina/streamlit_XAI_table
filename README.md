# XAI Library Navigator

A Streamlit app for finding and filtering libraries for ML model interpretation — covering both **Classic XAI** and **Mechanistic Interpretability**.

**→ [Open the app](https://xai-table.streamlit.app)**

## What's inside

**59 libraries** across two paradigms:

- **Classic XAI** — post-hoc explanation methods: SHAP, LIME, gradients, counterfactuals, feature importance, attention visualization
- **Mechanistic Interpretability** — internal structure analysis: circuits, sparse autoencoders (SAE), activation patching, steering vectors, knowledge editing
- **Hybrid** — both approaches

## Filters

- Paradigm (Classic XAI / Mechanistic / Hybrid)
- Data modality (Tabular, Images, Text, Time Series, LLM, Multimodal, Graph)
- Method type (SHAP, LIME, Gradient, SAE, Steering Vectors, Counterfactual…)
- Text search across library names and descriptions
- Toggle inactive libraries (no commits in the last year)

## Pages

| Page | Description |
|---|---|
| Home | Main catalog — English |
| Suggest a Library | Submit a library for review (sends to author via Telegram) |
| На русском | Russian version |

## Data

All library data is stored in `data/xai_libraries.csv` with the following schema:

`library` · `url` · `paradigm` · `modality` · `framework` · `method_category` · `scope` · `model_agnostic` · `description_en` · `stars` · `last_updated` · `topics` · `note`

Metadata (stars, last updated) is fetched automatically from the GitHub API via `enrich.py`.


## Useful resources

- [Interpretable Machine Learning](https://christophm.github.io/interpretable-ml-book/) — Christoph Molnar
- [Awesome LLM Interpretability](https://github.com/JShollaj/awesome-llm-interpretability)
- [XAI tutorials](https://github.com/SadSabrina/XAI-open_materials)
- [DataBlog](https://t.me/jdata_blog)

## Contacts

- Telegram: [@sabrina_sadiekh](https://t.me/sabrina_sadiekh)
- Blog: [DataBlog](https://t.me/jdata_blog)
- Substack: [@sabrinasadiekh](https://substack.com/@sabrinasadiekh)
- LinkedIn: [Sabrina Sadiekh](https://www.linkedin.com/in/sabrina-sadiekh-35181a286)
- Email: sadsobr7@gmail.com

## License

MIT
