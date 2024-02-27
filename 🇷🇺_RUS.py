import streamlit as st
import pandas as pd
from xai_table_functions import plot_data_with_hyperlinks, filter_dataframe
import plotly.graph_objects as go

st.set_page_config(page_title="RUS", page_icon="🇷🇺")

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

- Электронная книга ["Interpretable Machine Learning"](https://christophm.github.io/interpretable-ml-book/), автор Кристоф Молнар
- Мой [DataBlog](https://t.me/jdata_blog), об XAI и не только =)           
''')

st.markdown('''Tg: [@sabrina_sadiekh](https://t.me/sabrina_sadiekh)''')

st.markdown('''LinkedIn: [Sabrina Sadiekh](https://www.linkedin.com/in/sabrina-sadiekh-35181a286/?trk=nav_responsive_tab_profile_pic&originalSubdomain=ru)''')


# Data
merged_table = get_data()

# Frameworks list
FRAMEWORKS = ['skorch', 'scikit-learn', 'SciPy', 'LightGBM', 'tensorflow', 'XGBoost', 'lightning', 'sklearn-crfsuite',
              'Keras',  'transformers', 'pyspark', 'pytorch', 'CatBoost', 'h2o']

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


#Libraries with metrics

st.markdown('''Бибилиотеки с **метриками** интерпретации''')
st.markdown('''
            - [Quantus](https://github.com/understandable-machine-intelligence-lab/Quantus)
            - [shapash](https://github.com/MAIF/shapash#how_shapash_works)
            - [AIX360](https://github.com/Trusted-AI/AIX360)''')