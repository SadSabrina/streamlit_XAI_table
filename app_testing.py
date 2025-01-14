from xai_table_functions import plot_data_with_hyperlinks, filter_dataframe
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Функция для загрузки данных из базы данных
@st.cache_data
def load_data_from_db():
    engine = create_engine('sqlite:///xai_data.db')
    query = "SELECT * FROM xai_data"
    data = pd.read_sql(query, engine, index_col=['Unnamed: 0'])
    return data


# Data
merged_table = load_data_from_db()

# Frameworks list
FRAMEWORKS = ['skorch', 'scikit-learn', 'SciPy', 'LightGBM', 'tensorflow', 
              'XGBoost', 'lightning', 'sklearn-crfsuite', 'Keras',  'transformers', 
              'pyspark', 'pytorch', 'CatBoost', 'h2o']

#DTYPES
DTYPES = ['Tabular', 'Images', 'Texts', 'Graph', 'Time Series', 'Genomic']


framework_choice = st.selectbox('Select your framework', FRAMEWORKS, index=None,
                                placeholder='Select your framework')
data_type_choice = st.selectbox('Select your data type:', DTYPES, index=None,
                                placeholder='Select your data type')
if framework_choice or data_type_choice:

    data_to_schow = filter_dataframe(merged_table, framework_choice, data_type_choice)
    fig = plot_data_with_hyperlinks(data_to_schow)
    st.plotly_chart(fig, use_container_width=True)






