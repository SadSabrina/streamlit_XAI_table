import pandas as pd
from sqlalchemy import create_engine

# Путь к файлу базы знаний, сохраненному на локальной машине
csv_file_path = '/Users/sabrinasadieh/Code/streamlit_XAI_table/data/merged_table.csv'

# Загрузка данных из CSV
data = pd.read_csv(csv_file_path)

# Создание соединения с базой данных SQLite
engine = create_engine('sqlite:///xai_data.db')

# Импорт данных в базу данных
data.to_sql('xai_data', engine, if_exists='replace', index=False)

print("Данные успешно загружены в базу данных!")