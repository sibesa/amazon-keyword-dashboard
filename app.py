import streamlit as st
import pandas as pd
import os

# Veritabanı dosyası (ASIN'leri ve açıklamaları kaydedeceğiz)
DATA_FILE = "asin_data.csv"

# Veriyi yükle (asın ve açıklamalar)
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return df
    else:
        # Veritabanı dosyası yoksa yeni bir dosya oluşturulacak
        return pd.DataFrame(columns=['ASIN', 'Description'])

# Sayfa başlığı ve ayarları
st.set_page_config(page_title="Amazon ASIN Yönetimi", layout="wide")
st.title("🔍 Amazon ASIN Yönetim Paneli")

# ---------------------- Sol Menü ----------------------
with st.sidebar:
    st.header("Ürün Tanımı")
    menu_option = st.radio("Seçim yapın", ("Ana Sayfa", "ASIN Ekle", "Raporlar"))

# ---------------------- ASIN Ekleme Formu ----------------------
if menu_option == "ASIN Ekle":
    st.header("ASIN Ekleme Formu")
    
    # ASIN girişi için güzel bir tasarım
    asin_input = st.text_input("ASIN (10 karakterli bir ASIN girin)", value="", max_chars=10)
    
    # Eğer ASIN girildiyse ve 10 karakterse
    if len(asin_input) == 10:
        description_input = st.text_area("Açıklama (Ürün hakkında açıklama ekleyin)", height=150)
        
        # ASIN ve açıklama kaydetmek için buton
        if st.button("Kaydet", key="add_button", help="Veriyi kaydetmek için tıklayın", use_container_width=True):
            if description_input:
                # Veritabanına kaydetme
                df_existing = load_data()
                new_data = pd.DataFrame({'ASIN': [asin_input], 'Description': [description_input]})
                df_combined = pd.concat([df_existing, new_data], ignore_index=True)
                df_combined.to_csv(DATA_FILE, index=False)
                
                st.success(f"✅ '{asin_input}' ASIN başarıyla eklendi!")
            else:
                st.warning("Açıklama alanını boş bırakmayın!")
    elif asin_input:
        st.error("❌ ASIN 10 karakter olmalıdır. Lütfen geçerli bir ASIN girin.")
    
# ---------------------- Raporlar ----------------------
elif menu_option == "Raporlar":
    st.header("Eklenmiş ASIN'ler")
    
    # Daha önce eklenmiş ASIN'leri gösterme
    df_existing = load_data()
    
    if len(df_existing) > 0:
        for index, row in df_existing.iterrows():
            st.subheader(f"ASIN: {row['ASIN']}")
            st.write(f"Açıklama: {row['Description']}")
            st.write("---")
    else:
        st.write("Henüz hiçbir ASIN eklenmedi.")

# ---------------------- Ana Sayfa ----------------------
else:
    st.write("Ana sayfa içeriği burada yer alacak.")
