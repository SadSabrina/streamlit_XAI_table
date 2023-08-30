import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def get_data():
    
    path = r'./data/xai_md_agnostic_table_cleaned.csv'
    
    return pd.read_csv(path)

def filter_data(goals_choice, outputs_choice, general_data=get_data()):

    filtered_df = general_data.loc[(general_data['Goal'] == goals_choice) & (general_data['Output']==outputs_choice)]
    
    return filtered_df


def plot_data_with_hyperlinks(data):

    fig = go.Figure(
    data=[
        go.Table(
            columnwidth = [0.8, 0.8, 1, 3],
            header=dict(
                values=[f"<b>{i}</b>" for i in data.columns.to_list()],
                fill_color='pink'
                ),
            cells=dict(
                values=data.transpose(), fill_color='lavender'),
            )
        ]
    )
    return fig
    
    
    

df = get_data()

goals = df['Goal'].drop_duplicates()
goals_choice = st.sidebar.selectbox('Select your goal:', goals)

outputs = df['Output'].drop_duplicates()
outputs_choice = st.sidebar.selectbox('Select output type:', outputs)

filtered_df = filter_data(goals_choice, outputs_choice, df)

fig = plot_data_with_hyperlinks(filtered_df)

st.plotly_chart(fig, use_container_width=True)