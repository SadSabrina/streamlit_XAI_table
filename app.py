import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data

def get_data():
    path = [r'./data/md_agnostic_table_cleaned.csv', r'./data/md_specific_cleaned.csv']
    
    return pd.read_csv(path[0]), pd.read_csv(path[1])

def filter_md_agnostic_data(goals_choice, outputs_choice, general_data=get_data()[0]):

    if outputs_choice != 'any':
        filtered_df = general_data.loc[(general_data['Goal'] == goals_choice) & (general_data['Output']==outputs_choice)]
    else: 
        filtered_df = general_data.loc[general_data['Goal'] == goals_choice]
    
    return filtered_df


def filter_md_specific_data(model_choice, general_data=get_data()[1]):

    filtered_df = general_data.loc[general_data['Model'] == model_choice]
    
    return filtered_df


def plot_data_with_hyperlinks(data):

    fig = go.Figure(
    data=[
        go.Table(
            columnwidth = [0.8, 0.8, 1, 3],
            header=dict(
                values=[f"<b>{i}</b>" for i in data.columns.to_list()],
                fill_color='lightskyblue', 
                font=dict(color='black', size=15)
                ),
            cells=dict(
                values=data.transpose(), 
                fill_color='rgb(239, 243, 255)',
            font=dict(color='black', size=13)),
            )
        ]
    )
    return fig

st.title('Automatic selection of the explanation method for your task.')

st.subheader('Descriptions:')
    
st.markdown('**Microscope AI** - methods that make it possible to consider the influence of specific feature values on the prediction.')
st.markdown('**Model understating** - methods that make it possible to see the decision-making process on each single sample.')
st.markdown('**Model debugging** — methods for making detail missсlassification analysis and and for the depth analysis of features.')

#get data
md_agnostic_df, md_specific_df = get_data()

#MD agnostic
st.subheader('Model agnostic methods')

goals = md_agnostic_df['Goal'].drop_duplicates()

st.sidebar.title('Select a goal and choose an output type')
goals_choice = st.sidebar.selectbox('Select your goal:', goals)

outputs = list(md_agnostic_df['Output'].drop_duplicates())
outputs.append('any')
outputs_choice = st.sidebar.selectbox('Select output type:', outputs)

filtered_md_agn_df = filter_md_agnostic_data(goals_choice, outputs_choice, md_agnostic_df)

fig_agn = plot_data_with_hyperlinks(filtered_md_agn_df)

st.plotly_chart(fig_agn, use_container_width=True)

#MD specific
st.subheader('Model specific methods')

st.sidebar.title('Select your model')

models = md_specific_df['Model'].drop_duplicates()
model_choice = st.sidebar.selectbox('Select your model:', models)

filter_md_spec_df = filter_md_specific_data(model_choice, md_specific_df)

fig_spec = plot_data_with_hyperlinks(filter_md_spec_df)

st.plotly_chart(fig_spec, use_container_width=True)
