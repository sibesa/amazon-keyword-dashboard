import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
import os

# Sayfa ayarları
st.set_page_config(page_title="Amazon ASIN Dashboard", layout="wide")
st.title("🔍 Amazon ASIN Dashboard")

# CSS ile stil güzelleştirme
st.markdown("""
    <style>
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 10px 20px;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #125a8f;
    }
    .stTextInput>div>input {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Veri dosyası
DATA_FILE = "asin_data.csv"

# Veriyi yükleme fonksiyonu
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["ASIN", "Açıklama"])

# ASIN ekleme formu
st.sidebar.subheader("📅 ASIN Ekle")
asin = st.sidebar.text_input("ASIN (10 karakter)", max_chars=10)
aciklama = st.sidebar.text_area("Üürün Açıklaması")
if st.sidebar.button("Kaydet"):
    if len(asin) == 10 and aciklama:
        df = load_data()
        yeni = pd.DataFrame({"ASIN": [asin], "Açıklama": [aciklama]})
        df = pd.concat([df, yeni], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("ASIN eklendi!")
    else:
        st.sidebar.error("ASIN 10 karakter olmalı ve açıklama boş bırakılamaz.")

# Seçim menüsü
secim = st.sidebar.radio("🔍 Görüntüleme Seçimi", ("Raporlar", "Grafikler"))

# Raporlar Tablosu
if secim == "Raporlar":
    st.subheader("📊 Eklenmiş ASIN'ler")
    df = load_data()
    if not df.empty:
        AgGrid(df)
    else:
        st.info("Henüz ASIN eklenmedi.")

# Plotly ile grafik gösterimi
elif secim == "Grafikler":
    st.subheader("🌐 ASIN Dağılım Grafiği")
    df = load_data()
    if not df.empty:
        df['Uzunluk'] = df['Açıklama'].str.len()
        fig = px.bar(df, x="ASIN", y="Uzunluk", text="Açıklama",
                     labels={"Uzunluk": "Açıklama Uzunluğu"},
                     title="ASIN Açıklamalarının Uzunluk Dağılımı")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Görüntülenecek veri yok.")
