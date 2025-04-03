import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Favori dosyası
FAV_FILE = "favorites.csv"
DATA_FILE = "keyword_tracking.csv"

# Ana veri yükleyici
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
    return df

# Başlık
st.set_page_config(page_title="Amazon Keyword Dashboard", layout="wide")
st.title("🔍 Amazon Anahtar Kelime Sıralama Dashboard")

# Excel yükleme
st.sidebar.header("📥 Excel Dosyası Yükle")
uploaded_file = st.sidebar.file_uploader("Excel dosyasını seçin", type=["xlsx"])
if uploaded_file:
    excel_data = pd.ExcelFile(uploaded_file)
    df_new = excel_data.parse('B0CHJF8YM6')
    input_date = st.sidebar.date_input("Veri Tarihi", datetime.today().date())

    df_cleaned = df_new[['Keywords', 'Child ASIN', 'Badge', 'Position', 'Searches/M']].copy()
    df_cleaned.rename(columns={
        'Keywords': 'Keyword',
        'Child ASIN': 'ASIN',
        'Badge': 'Badge',
        'Position': 'Position',
        'Searches/M': 'SearchVolume'
    }, inplace=True)
  df_cleaned['Type'] = df_cleaned['Badge'].apply(lambda x: 'Reklamlı' if x == 'SP' else 'Organik')

