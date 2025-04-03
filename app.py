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
    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
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

# Sidebar başlık ve menü
with st.sidebar:
    st.markdown("<div class='sidebar-title'>SIBESA AMAZON KEYWORD TRACKING</div>", unsafe_allow_html=True)

    tanim_ac = st.expander("Tanımlamalar")
    asin_ac = st.expander("ASIN'ler")
    rapor_ac = st.expander("Raporlar")

    with tanim_ac:
        secim = st.radio("", ["ASIN Ekle"], key="tanımlar")

    asin_list = load_data()
    asin_secim = None
    with asin_ac:
        if asin_list.empty:
            st.info("Henüz ASIN eklenmedi.")
        else:
            asin_secim = st.radio("Ekli ASIN'ler", asin_list["ASIN"].tolist(), key="asin_secim")

    with rapor_ac:
        secim2 = st.radio("", ["ASIN Listesi", "Açıklama Grafiği"], key="raporlar")

# Ana içerik alanı
if secim == "ASIN Ekle":
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
        else:
            st.error("ASIN tam olarak 10 karakter olmali ve açıklama girilmelidir.")

elif secim2 == "ASIN Listesi":
    st.subheader("📊 Eklenmiş ASIN'ler")
    df = load_data()
    if not df.empty:
        AgGrid(df)
    else:
        st.info("Henüz ASIN eklenmedi.")

elif secim2 == "Açıklama Grafiği":
    st.subheader("🌐 Açıklama Uzunluk Grafiği")
    df = load_data()
    if not df.empty:
        df['Uzunluk'] = df['Açıklama'].str.len()
        fig = px.bar(df, x="ASIN", y="Uzunluk", text="Açıklama",
                     labels={"Uzunluk": "Açıklama Uzunluğu"},
                     title="ASIN Açıklamalarının Uzunluk Dağılımı")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Görüntülenecek veri yok.")
