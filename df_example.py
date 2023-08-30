import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Data example with a clickable link

def create_link(url:str) -> str:
    return f'''<a href="{url}">🔗</a>'''



df = pd.DataFrame(
    {"Site": "DuckDuckGo Google Bing".split(),
     "URL": "https://duckduckgo.com/ https://www.google.com/ https://www.bing.com/".split()}
)

df['Link'] = [create_link(url) for url in df["URL"]]

test_2 = '<a href="https://shap.readthedocs.io/en/latest/index.html">🔗</a>\n<a href="https://interpret.ml/docs/shap.html">🔗</a>\n<a href="https://explainerdashboard.readthedocs.io/en/latest/dashboards.html">🔗</a>'

test_3 = '<a href="https://shap.readthedocs.io/en/latest/index.html">shap, </a>\n<a href="https://interpret.ml/docs/shap.html">interpret_ml, </a>or see <a href="https://explainerdashboard.readthedocs.io/en/latest/dashboards.html">explainerdashboard</a>'

df.loc[len(df)] = ['', '', test_2]
df.loc[len(df)] = ['', '', test_3]

"# Dataframe as a plotly table"

fig = go.Figure(
    data=[
        go.Table(
            columnwidth = [1,1, 2],
            header=dict(
                values=[f"<b>{i}</b>" for i in df.columns.to_list()],
                fill_color='pink'
                ),
            cells=dict(
                values=df.transpose()
                )
            )
        ]
    )
st.plotly_chart(fig, use_container_width=True)