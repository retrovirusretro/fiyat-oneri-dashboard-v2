import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fiyat Öneri Dashboard v2", layout="wide")
st.title("📊 Fiyat Öneri Dashboard v2 - Gökhan Ustaosmanoğlu")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin (.xlsx)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Urunler")
    df.columns = df.columns.str.strip()

    col1, col2, col3, col4 = st.columns(4)

    col4.metric("Muhtemel Promosyon", (df["Promosyon Notu"] == "Muhtemel Promosyon").sum())

    st.markdown("---")
    with st.expander("🔍 Filtrele"):
        colf1, colf2 = st.columns(2)
        secim_oneri = colf1.multiselect("Öneri Türü", options=df["Açıklama"].unique(), default=df["Açıklama"].unique())
        secim_promosyon = colf2.multiselect("Promosyon Notu", options=df["Promosyon Notu"].unique(), default=df["Promosyon Notu"].unique())

        colf3, colf4 = st.columns(2)
        qty_filter = colf3.slider("TW Qty. (Son Hafta Satış)", 0, int(df["TW Qty."].max()), (0, int(df["TW Qty."].max())))
        gmroi_filter = colf4.slider("GMROI", 0.0, float(df["TW GMROI"].max()), (0.0, float(df["TW GMROI"].max())))

    # Filtre uygulanmış veri
    df_filtered = df[
        (df["Açıklama"].isin(secim_oneri)) &
        (df["Promosyon Notu"].isin(secim_promosyon)) &
        (df["TW Qty."].between(qty_filter[0], qty_filter[1])) &
        (df["TW GMROI"].between(gmroi_filter[0], gmroi_filter[1]))
    ]

    # Koşullu renk fonksiyonu
    def renk_kodla_sdh(val):
        if val < 60: return "🟢"
        elif val <= 100: return "🟡"
        else: return "🔴"

    def renk_kodla(val, low, mid, high):
        if val < low: return "🔴"
        elif val < mid: return "🟡"
        else: return "🟢"

    if not df_filtered.empty:
        renkli_df = df_filtered.copy()
        renkli_df["GMROI Renk"] = renkli_df["TW GMROI"].apply(lambda x: renk_kodla(x, 1.0, 2.5, 999))
        renkli_df["Marj Renk"] = renkli_df["Yeni Fiyat"].apply(lambda x: renk_kodla(x, 100, 200, 999))
        renkli_df["Cover Renk"] = renkli_df["TW Cover"].apply(lambda x: renk_kodla(x, 3.5, 10, 999))
        renkli_df["SDH Renk"] = renkli_df["SDH"].apply(renk_kodla_sdh)
        renkli_df["STR Renk"] = renkli_df["STR %"].apply(lambda x: renk_kodla(x, 30, 60, 999))
        renkli_df["ROS Renk"] = renkli_df["TW ROS"].apply(lambda x: renk_kodla(x, 0.5, 1.5, 999))

        st.subheader("📋 Aksiyon Ürünler (Koşullu Renkli)")
        st.dataframe(renkli_df, use_container_width=True)

        st.markdown("### 📈 Görsel Analizler")
        colg1, colg2 = st.columns(2)
        fig1 = px.pie(df_filtered, names="Açıklama", title="Öneri Dağılımı")
        colg1.plotly_chart(fig1, use_container_width=True)

        if "Yeni Fiyat" in df.columns:
            fig2 = px.histogram(df_filtered, x="Yeni Fiyat", nbins=20, title="Yeni Fiyat Dağılımı")
            colg2.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("💾 CSV İndir")
        csv = renkli_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 CSV Olarak İndir", data=csv, file_name="aksiyon_urunler.csv", mime="text/csv")
    else:
        st.warning("🔍 Filtreye uyan sonuç bulunamadı.")
else:
    st.info("Lütfen önce bir Excel dosyası yükleyin.")
