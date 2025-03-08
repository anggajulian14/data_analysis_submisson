import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

st.title("📊 Dashboard Kualitas Udara")
st.write("Ini adalah dashboard sederhana untuk melihat kualitas udara dari berbagai lokasi.")

# Cari file CSV di dalam folder data
files = glob.glob("merged_air_quality.csv") 
pollutants = ["PM2.5", "PM10", "NO2", "SO2"]
data_stations = {} 


total_files = len(files)  
if total_files == 0:
    st.warning("⚠️ Tidak ada data ditemukan! Pastikan folder 'data' berisi file CSV.")
else:
    for file in files:
        station_name = os.path.basename(file).replace(".csv", "") 
        df = pd.read_csv(file)
        if {"year", "month"}.issubset(df.columns):
            data_stations[station_name] = df
        else:
            st.warning(f"⚠️ Data di {station_name} tidak memiliki kolom 'year' atau 'month'.")

if data_stations:
    selected_station = st.selectbox("Pilih Stasiun:", list(data_stations.keys()))
    df = data_stations[selected_station]
    
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    year_range = st.slider("Pilih Tahun:", min_year, max_year, (min_year, max_year))
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    
    if df.empty:
        st.error("❌ Tidak ada data dalam rentang tahun yang dipilih!")
    else:
        # Grafik Tren Polutan
        st.subheader(f"📈 Tren Polutan di {selected_station}")
        yearly_avg = df.groupby("year")[pollutants].mean()
        fig, ax = plt.subplots(figsize=(10, 5))
        for p in pollutants:
            ax.plot(yearly_avg.index, yearly_avg[p], marker="o", label=p)
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Konsentrasi (µg/m³)")
        ax.set_title(f"Tren Polutan di {selected_station}")
        ax.legend()
        st.pyplot(fig)
        
        # Cari bulan terbaik & terburuk
        best_month = df.groupby(["year", "month"])["PM2.5"].mean().idxmin()
        worst_month = df.groupby(["year", "month"])["PM2.5"].mean().idxmax()
        
        st.subheader("🌱 Kualitas Udara Terbaik & Terburuk")
        col1, col2 = st.columns(2)
        col1.success(f"✅ Terbaik: {best_month[0]}-{best_month[1]}")
        col2.error(f"❌ Terburuk: {worst_month[0]}-{worst_month[1]}")
        
        # Bandingkan Stasiun
        best_pm25 = {}
        worst_pm25 = {}
        for station, data in data_stations.items():
            try:
                best = data.groupby(["year", "month"])["PM2.5"].mean().idxmin()
                worst = data.groupby(["year", "month"])["PM2.5"].mean().idxmax()
                best_pm25[station] = data[(data["year"] == best[0]) & (data["month"] == best[1])]["PM2.5"].mean()
                worst_pm25[station] = data[(data["year"] == worst[0]) & (data["month"] == worst[1])]["PM2.5"].mean()
            except:
                st.warning(f"⚠️ Data di {station} mungkin tidak lengkap.")
        
        # Grafik Perbandingan
        st.subheader("📊 Perbandingan Kualitas Udara Antar Stasiun")
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.barplot(x=list(best_pm25.keys()), y=list(best_pm25.values()), palette="Blues_r", ax=ax)
        ax.set_title("✅ Kualitas Udara Terbaik")
        ax.set_ylabel("PM2.5 (µg/m³)")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
        
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.barplot(x=list(worst_pm25.keys()), y=list(worst_pm25.values()), palette="Reds_r", ax=ax)
        ax.set_title("❌ Kualitas Udara Terburuk")
        ax.set_ylabel("PM2.5 (µg/m³)")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
