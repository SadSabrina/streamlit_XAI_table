import streamlit as st
import pandas as pd
from xai_table_functions import plot_data_with_hyperlinks, filter_dataframe
import plotly.graph_objects as go


@st.cache_data
def get_data():
    path = r'./data/merged_table.csv'

    return pd.read_csv(path, index_col=0)


# Title
st.title('Find a way to make your AI explainable')

# Annotation

st.markdown('''
Здесь вы можете подобрать библиотеку, предлагающую методы интерпретации моделей, под свою задачу. \

Классификация библиотек была реализована с учетом практических характеристик, влияющих на возможность и \
невозможность использовать соответствующие методы интерпретации. Было выявлено, что при практическом использовании \
 выбор конкретной библиотеки будет зависеть от:

- типа данных, на которых обучена модель
- фреймворка, с помощью которого модель была обучена
Соответственно, именно такая фильтрация реализована здесь.

**Полезные ресурсы об Explainable AI:**

Электронная книга ["Interpretable Machine Learning"](https://christophm.github.io/interpretable-ml-book/), автор Кристоф Молнар
''')


# Data
merged_table = get_data()

# Frameworks list
FRAMEWORKS = ['skorch', 'scikit-learn', 'SciPy', 'LightGBM', 'tensorflow', 'XGBoost', 'lightning', 'sklearn-crfsuite',
              'Keras',  'transformers', 'pyspark', 'pytorch', 'CatBoost']

#DTYPES
DTYPES = ['Tabular', 'Images', 'Texts', 'Graph', 'Time Series']


framework_choice = st.selectbox('Select your framework', FRAMEWORKS, index=None,
                                placeholder='Select your framework')
data_type_choice = st.selectbox('Select your data type:', DTYPES, index=None,
                                placeholder='Select your data type')
if framework_choice or data_type_choice:

    data_to_schow = filter_dataframe(merged_table, framework_choice, data_type_choice)
    fig = plot_data_with_hyperlinks(data_to_schow)
    st.plotly_chart(fig, use_container_width=True)