import streamlit as st
import pandas as pd
import os

# CSS style for custom design
st.markdown("""
    <style>
    /* Sidebar */
    .css-1d391kg {
        background-color: #2A3D66;
        color: white;
    }
    .css-ffhzg2 {
        color: white;
    }
    /* Main area */
    .css-10trblm {
        background-color: #F5F5F5;
        padding: 20px;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton button:hover {
        background-color: #0061C2;
    }
    /* Add padding to the content */
    .css-ffhzg2 {
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Sayfa başlığı
st.title("🔍 Amazon ASIN Yönetim Paneli")

# Sol Menü
with st.sidebar:
    st.header("Ürün Tanımı")
    menu_option = st.radio("Seçim yapın", ("Ana Sayfa", "ASIN Ekle", "Raporlar"))

# ---------------------- ASIN Ekleme Formu ----------------------
if menu_option == "ASIN Ekle":
    st.header("ASIN Ekleme Formu")
    st.write("ASIN eklemek için gerekli formu doldurun.")
    
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
    df_existing = load_data()
    
    if len(df_existing) > 0:
        for index, row in df_existing.iterrows():
            st.subheader(f"ASIN: {row['ASIN']}")
            st.write(f"Açıklama: {row['Description']}")
            st.write("---")
    else:
        st.write("Henüz hiçbir ASIN eklenmedi.")
