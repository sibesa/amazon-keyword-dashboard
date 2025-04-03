import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Dosya adları
FAV_FILE = "favorites.csv"
DATA_FILE = "keyword_tracking.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
    return df

st.set_page_config(page_title="Amazon Keyword Dashboard", layout="wide")
st.title("🔍 Amazon Anahtar Kelime Sıralama Dashboard")

# ---------------------- Excel Yükleme ----------------------

st.sidebar.header("📥 Excel Dosyası Yükle")
uploaded_file = st.sidebar.file_uploader("Excel dosyasını seçin", type=["xlsx"])
if uploaded_file:
    try:
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
        df_cleaned['Date'] = input_date
        df_cleaned = df_cleaned[['Date', 'ASIN', 'Keyword', 'Type', 'Position', 'SearchVolume']]

        if os.path.exists(DATA_FILE):
            df_existing = pd.read_csv(DATA_FILE, parse_dates=['Date'])
            df_combined = pd.concat([df_existing, df_cleaned], ignore_index=True)
        else:
            df_combined = df_cleaned

        df_combined.to_csv(DATA_FILE, index=False)
        st.sidebar.success("✅ Veri başarıyla yüklendi!")
        st.experimental_rerun()

    except Exception as e:
        st.sidebar.error(f"❌ Hata oluştu: {e}")
        st.stop()

# ---------------------- Veri Kontrol ----------------------

if not os.path.exists(DATA_FILE):
    st.warning("📄 Henüz veri yüklenmedi. Lütfen sol panelden bir Excel yükleyin.")
    st.stop()

# Kalan kod (analiz, grafik, favori vs.) buraya eklenecek...

st.success("✅ Veri başarıyla yüklendi ve uygulama hazır!")
