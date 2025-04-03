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
        return pd.DataFrame(columns=['ASIN', 'Description'])

# Sayfa başlığı ve ayarları
st.set_page_config(page_title="Amazon ASIN Yönetimi", layout="wide")
st.title("🔍 Amazon ASIN Yönetim Paneli")

# ---------------------- Sol Menü ----------------------
with st.sidebar:
    st.header("Ürün Tanımı")
    menu_option = st.radio("Seçim yapın", ("Ana Sayfa", "ASIN Ekle"))

# ---------------------- ASIN Eklemeyi Seçme ----------------------
if menu_option == "ASIN Ekle":
    st.header("ASIN Ekleme Formu")
    
    # ASIN girişi ve açıklama eklemek için input alanları
    asin_input = st.text_input("ASIN (10 karakter)", max_chars=10)
    
    if len(asin_input) == 10:
        description_input = st.text_area("Açıklama (Ürün hakkında açıklama ekleyin)")
        
        # Ekle butonu (mavi renk)
        if st.button("Ekle", key="add_button", help="Veriyi eklemek için tıklayın", use_container_width=True):
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
    
else:
    st.write("Ana sayfa içeriği burada yer alacak.")
    
