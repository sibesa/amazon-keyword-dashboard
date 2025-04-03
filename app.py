import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

FAV_FILE = "favorites.csv"
DATA_FILE = "keyword_tracking.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
    return df

st.set_page_config(page_title="Amazon Keyword Dashboard", layout="wide")
st.title("🔍 Amazon Anahtar Kelime Sıralama Dashboard")

# ---------------------- ASIN Tanımlama ----------------------
asin_input = st.sidebar.text_input("Yeni ASIN Tanımla (10 karakterli bir ASIN girin)", value="")

# ASIN'in 10 karakterli olup olmadığını kontrol et
if asin_input:
    if len(asin_input) == 10:
        asin_list = [asin_input]  # Tek bir ASIN listesi
        st.sidebar.write("ASIN Listesi:", asin_list)
    else:
        st.sidebar.error("❌ ASIN 10 karakterden oluşmalı!")
        asin_list = []
else:
    asin_list = []

# ---------------------- Excel Yükleme ----------------------
st.sidebar.header("📥 Excel Dosyası Yükle")
uploaded_file = st.sidebar.file_uploader("Excel dosyasını seçin", type=["xlsx"])

if uploaded_file:
    try:
        excel_data = pd.ExcelFile(uploaded_file)
        df_new = excel_data.parse('B0CHJF8YM6')
        
        input_date = st.sidebar.date_input("Veri Tarihi Seç", datetime.today().date())

        # Veriyi temizleme
        df_cleaned = df_new[['Keywords', 'Child ASIN', 'Badge', 'Position', 'Searches/M']].copy()
        df_cleaned.rename(columns={
            'Keywords': 'Keyword',
            'Child ASIN': 'ASIN',
            'Badge': 'Badge',
            'Position': 'Position',
            'Searches/M': 'SearchVolume'
        }, inplace=True)

        df_cleaned['Type'] = df_cleaned['Badge'].apply(lambda x: 'Reklamlı' if x == 'SP' else 'Organik')
        df_cleaned['Date'] = pd.to_datetime(input_date)
        df_cleaned = df_cleaned[['Date', 'ASIN', 'Keyword', 'Type', 'Position', 'SearchVolume']]

        # Yüklenmiş veriyi dosyaya ekleme
        if os.path.exists(DATA_FILE):
            df_existing = pd.read_csv(DATA_FILE, parse_dates=['Date'])
            df_combined = pd.concat([df_existing, df_cleaned], ignore_index=True)
        else:
            df_combined = df_cleaned

        df_combined.to_csv(DATA_FILE, index=False)
        st.sidebar.success("✅ Veri başarıyla yüklendi!")
        st.rerun()

    except Exception as e:
        st.sidebar.error(f"❌ Hata oluştu: {e}")
        st.stop()

if not os.path.exists(DATA_FILE):
    st.warning("📄 Henüz veri yüklenmedi. Lütfen sol panelden bir Excel yükleyin.")
    st.stop()

# ---------------------- Veri Yükleme ----------------------
df = load_data()

# ---------------------- Tarih Filtresi ----------------------
st.sidebar.header("🗓️ Veri Yükleme Takvimi")
# Tarihleri gruplama
unique_dates = pd.to_datetime(df['Date'], errors='coerce').dt.date.unique()
all_dates = pd.date_range(min(unique_dates), max(unique_dates)).date

# Kırmızı ve yeşil renklerde tarih işaretleme
date_status = []
for day in all_dates:
    if day in unique_dates:
        date_status.append((day, 'green'))
    else:
        date_status.append((day, 'red'))

date_to_upload = [date for date, status in date_status if status == 'green']

# ---------------------- ASIN ve Keyword Seçimi ----------------------
if asin_list:  # Eğer bir ASIN varsa seçme işlemi yapılır
    selected_asin = st.selectbox("ASIN Seçin", asin_list)
    selected_date = st.selectbox("Veri Yükleme Tarihi Seçin", date_to_upload)

    # ---------------------- Grafikler ----------------------
    st.subheader(f"📈 '{selected_asin}' için Sıralama Değişimi")
    selected_data = df[(df['ASIN'] == selected_asin) & (df['Date'].dt.date == selected_date)]

    fig = px.line(selected_data, x='Date', y='Position', color='Type', markers=True)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------- Ekle Butonu ----------------------
    if st.button("Ekle"):
        # Burada ASIN ve tarih bilgileriyle birlikte veri işlemi yapılabilir
        st.success(f"ASIN: {selected_asin} için tarih {selected_date} yüklendi.")
else:
    st.sidebar.warning("📄 Henüz bir ASIN tanımlanmadı. Lütfen bir ASIN girin.")
