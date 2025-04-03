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
        st.rerun()

    except Exception as e:
        st.sidebar.error(f"❌ Hata oluştu: {e}")
        st.stop()

if not os.path.exists(DATA_FILE):
    st.warning("📄 Henüz veri yüklenmedi. Lütfen sol panelden bir Excel yükleyin.")
    st.stop()

# ---------------------- Veri Yükleme ----------------------
df = load_data()

# ---------------------- Favori ----------------------
if os.path.exists(FAV_FILE):
    fav_df = pd.read_csv(FAV_FILE)
else:
    fav_df = pd.DataFrame(columns=["ASIN", "Keyword"])

# ---------------------- Tarih Filtresi ----------------------
st.sidebar.header("🗓️ Tarih Filtresi")
min_date, max_date = df['Date'].min(), df['Date'].max()
filter_type = st.sidebar.radio("Zaman Görünümü Seç", ["Günlük", "Haftalık", "Aylık"])

if filter_type == "Günlük":
    start_date, end_date = st.sidebar.date_input(
        "Tarih Aralığı", 
        [min_date, max_date]
    )
elif filter_type == "Haftalık":
    df['YearWeek'] = df['Date'].dt.strftime('%Y-%U')
    selected_week = st.sidebar.selectbox("Hafta Seç (Yıl-Hafta)", sorted(df['YearWeek'].unique()))
    selected_dates = df[df['YearWeek'] == selected_week]['Date']
    start_date, end_date = selected_dates.min().date(), selected_dates.max().date()
else:
    df['YearMonth'] = df['Date'].dt.to_period('M')
    selected_month = st.sidebar.selectbox("Ay Seç (YYYY-MM)", sorted(df['YearMonth'].astype(str).unique()))
    selected_dates = df[df['YearMonth'].astype(str) == selected_month]['Date']
    start_date, end_date = selected_dates.min().date(), selected_dates.max().date()

start = pd.to_datetime(start_date)
end = pd.to_datetime(end_date)
filtered_df = df[(df['Date'] >= start) & (df['Date'] <= end)]

# ---------------------- ASIN ve Keyword Seçimi ----------------------
asins = filtered_df['ASIN'].unique()
selected_asin = st.selectbox("ASIN Seçin", sorted(asins))
asin_df = filtered_df[filtered_df['ASIN'] == selected_asin]
keywords = asin_df['Keyword'].unique()
selected_keyword = st.selectbox("Anahtar Kelime Seçin", sorted(keywords))
keyword_df = asin_df[asin_df['Keyword'] == selected_keyword]

# ---------------------- Favori Butonu ----------------------
is_fav = ((fav_df['ASIN'] == selected_asin) & (fav_df['Keyword'] == selected_keyword)).any()
if st.button("⭐ Favorilere Ekle" if not is_fav else "❌ Favoriden Kaldır"):
    if not is_fav:
        fav_df = pd.concat([fav_df, pd.DataFrame([[selected_asin, selected_keyword]], columns=["ASIN", "Keyword"])])
    else:
        fav_df = fav_df[~((fav_df['ASIN'] == selected_asin) & (fav_df['Keyword'] == selected_keyword))]
    fav_df.to_csv(FAV_FILE, index=False)
    st.rerun()

# ---------------------- Grafikler ----------------------
st.subheader(f"📈 '{selected_keyword}' için Sıralama Değişimi ({selected_asin})")
fig = px.line(keyword_df, x='Date', y='Position', color='Type', markers=True)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# ---------------------- Günlük Değişim ----------------------
st.subheader("📊 Günlük Sıralama Değişim Özeti")
latest_dates = sorted(asin_df['Date'].unique())[-2:]
if len(latest_dates) == 2:
    d1, d2 = latest_dates
    df_y = asin_df[asin_df['Date'] == d1]
    df_t = asin_df[asin_df['Date'] == d2]
    df_c = pd.merge(df_t, df_y, on=["ASIN", "Keyword", "Type"], suffixes=('_today', '_yesterday'), how="outer")

    def durum(row):
        if pd.isna(row['Position_yesterday']) and not pd.isna(row['Position_today']):
            return "Yeni indexlenmiş"
        elif not pd.isna(row['Position_yesterday']) and pd.isna(row['Position_today']):
            return "Kaybolmuş"
        elif row['Position_today'] < row['Position_yesterday']:
            return "Yükselmiş"
        elif row['Position_today'] > row['Position_yesterday']:
            return "Düşmüş"
        else:
            return "Aynı"

    df_c['Durum'] = df_c.apply(durum, axis=1)
    st.dataframe(df_c[['Keyword', 'Type', 'Position_yesterday', 'Position_today', 'Durum']])
else:
    st.info("Karşılaştırma için en az 2 gün verisi gerekiyor.")

# ---------------------- Haftalık Trend ----------------------
st.subheader("📆 Haftalık Ortalama Pozisyon")
df['YearWeek'] = df['Date'].dt.strftime('%Y-%U')
trend_df = df[(df['ASIN'] == selected_asin) & (df['Keyword'] == selected_keyword)]
trend = trend_df.groupby(['YearWeek', 'Type'])['Position'].mean().reset_index()
fig2 = px.line(trend, x='YearWeek', y='Position', color='Type', markers=True)
fig2.update_yaxes(autorange="reversed")
st.plotly_chart(fig2, use_container_width=True)

# ---------------------- Öne Çıkanlar ----------------------
st.subheader("🌟 Öne Çıkan Kelimeler")
most_searched = asin_df.groupby("Keyword")['SearchVolume'].mean().reset_index().sort_values(by='SearchVolume', ascending=False).head(10)
st.markdown("**🔝 En Çok Aranan 10 Kelime**")
st.dataframe(most_searched)

if 'df_c' in locals():
    st.markdown("**📉 En Fazla Düşen 10 Kelime**")
    düşen = df_c[df_c['Durum'] == 'Düşmüş'].sort_values(by='Position_today', ascending=False).head(10)
    st.dataframe(düşen[['Keyword', 'Position_yesterday', 'Position_today']])

    st.markdown("**📈 En Fazla Yükselen 10 Kelime**")
    yükselen = df_c[df_c['Durum'] == 'Yükselmiş'].sort_values(by='Position_yesterday').head(10)
    st.dataframe(yükselen[['Keyword', 'Position_yesterday', 'Position_today']])

# ---------------------- Favori Paneli ----------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Favori Anahtar Kelimeler")
if not fav_df.empty:
    for _, row in fav_df.iterrows():
        st.sidebar.write(f"🔹 {row['ASIN']} — {row['Keyword']}")
else:
    st.sidebar.info("Favori kelimeniz yok.")

