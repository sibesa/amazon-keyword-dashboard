import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
import os

# Veri dosyası yolu
DATA_FILE = "asin_data.csv"

# Dosya yoksa oluştur ve yazma izni kontrol et
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["ASIN", "Açıklama"])
    df_init.to_csv(DATA_FILE, index=False)

try:
    with open(DATA_FILE, "a") as f:
        pass
except PermissionError:
    st.error("❌ 'asin_data.csv' dosyası yazılamıyor. Lütfen yazma izni verin.")

# Sayfa ayarı
st.set_page_config(page_title="Amazon ASIN Dashboard", layout="wide")
st.title("🔍 Amazon ASIN Dashboard")

# CSS stil
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
    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Veri yükleme fonksiyonu
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["ASIN", "Açıklama"])

# Sidebar menü
with st.sidebar:
    st.markdown("<div class='sidebar-title'>SIBESA AMAZON KEYWORD TRACKING</div>", unsafe_allow_html=True)
    secim_kategori = st.selectbox("📂 Kategori Seçin", ["ASIN Ekle", "ASIN Listesi", "Açıklama Grafiği"])

# Ana içerik
if secim_kategori == "ASIN Ekle":
    st.subheader("📅 ASIN Ekle")
    asin = st.text_input("ASIN (Tam olarak 10 karakter girin)", max_chars=10)
    aciklama = st.text_area("Üürün Açıklaması")

    if st.button("Kaydet"):
        if len(asin) == 10 and aciklama:
            df = load_data()
            if asin in df["ASIN"].values:
                st.warning("Bu ASIN zaten mevcut.")
            else:
                yeni = pd.DataFrame({"ASIN": [asin], "Açıklama": [aciklama]})
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("ASIN başarıyla kaydedildi!")
                st.rerun()
        else:
            st.error("ASIN tam olarak 10 karakter olmali ve açıklama girilmelidir.")

elif secim_kategori == "ASIN Listesi":
    st.subheader("📊 Eklenmiş ASIN'ler")
    df = load_data()
    if not df.empty:
        AgGrid(df)
    else:
        st.info("Henüz ASIN eklenmedi.")

elif secim_kategori == "Açıklama Grafiği":
    st.subheader("🌐 Açıklama Uzunluk Grafiği")
    df = load_data()
    if not df.empty:
        df['Uzunluk'] = df['Açıklama'].astype(str).str.len()
        fig = px.bar(df, x="ASIN", y="Uzunluk", text="Açıklama",
                     labels={"Uzunluk": "Açıklama Uzunluğu"},
                     title="ASIN Açıklamalarının Uzunluk Dağılımı")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Görüntülenecek veri yok.")
