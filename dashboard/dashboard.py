import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.title("📊 Dashboard Kualitas Udara")
st.write("Ini adalah dashboard sederhana untuk melihat kualitas udara dari berbagai lokasi.")

# Cek apakah file merged tersedia
file_path = "merged_air_quality.csv"
pollutants = ["PM2.5", "PM10", "NO2", "SO2"]

if not os.path.exists(file_path):
    st.warning("⚠️ Tidak ada data ditemukan! Pastikan file 'merged_air_quality.csv' tersedia.")
else:
    # Load data
    df = pd.read_csv(file_path)

    # Pastikan kolom yang diperlukan ada
    required_columns = {"year", "month", "station"}
    if not required_columns.issubset(df.columns):
        st.warning(f"⚠️ File tidak memiliki kolom yang dibutuhkan: {required_columns - set(df.columns)}")
    else:
        # Ambil daftar unik stasiun
        stations = df["station"].unique()

        if len(stations) == 0:
            st.warning("⚠️ Tidak ada data stasiun yang tersedia dalam file.")
        else:
            # Pilihan stasiun dari dropdown
            selected_station = st.selectbox("Pilih Stasiun:", stations)

            # Filter data berdasarkan stasiun yang dipilih
            station_df = df[df["station"] == selected_station]

            # Ambil rentang tahun
            min_year, max_year = int(station_df["year"].min()), int(station_df["year"].max())
            year_range = st.slider("Pilih Tahun:", min_year, max_year, (min_year, max_year))
            station_df = station_df[(station_df["year"] >= year_range[0]) & (station_df["year"] <= year_range[1])]

            if station_df.empty:
                st.error("❌ Tidak ada data dalam rentang tahun yang dipilih!")
            else:
                # Grafik Tren Polutan
                st.subheader(f"📈 Tren Polutan di {selected_station}")
                yearly_avg = station_df.groupby("year")[pollutants].mean()

                fig, ax = plt.subplots(figsize=(10, 5))
                for p in pollutants:
                    ax.plot(yearly_avg.index, yearly_avg[p], marker="o", label=p)
                ax.set_xlabel("Tahun")
                ax.set_ylabel("Konsentrasi (µg/m³)")
                ax.set_title(f"Tren Polutan di {selected_station}")
                ax.legend()
                st.pyplot(fig)

                # Cari bulan terbaik & terburuk berdasarkan PM2.5
                best_month = station_df.groupby(["year", "month"])["PM2.5"].mean().idxmin()
                worst_month = station_df.groupby(["year", "month"])["PM2.5"].mean().idxmax()

                st.subheader("🌱 Kualitas Udara Terbaik & Terburuk")
                col1, col2 = st.columns(2)
                col1.success(f"✅ Terbaik: {best_month[0]}-{best_month[1]}")
                col2.error(f"❌ Terburuk: {worst_month[0]}-{worst_month[1]}")

                # Bandingkan Stasiun (semua stasiun)
                best_pm25, worst_pm25 = {}, {}
                for station in stations:
                    station_data = df[df["station"] == station]
                    try:
                        best = station_data.groupby(["year", "month"])["PM2.5"].mean().idxmin()
                        worst = station_data.groupby(["year", "month"])["PM2.5"].mean().idxmax()
                        best_pm25[station] = station_data[(station_data["year"] == best[0]) & (station_data["month"] == best[1])]["PM2.5"].mean()
                        worst_pm25[station] = station_data[(station_data["year"] == worst[0]) & (station_data["month"] == worst[1])]["PM2.5"].mean()
                    except:
                        st.warning(f"⚠️ Data di {station} mungkin tidak lengkap.")

                # Grafik Perbandingan Stasiun
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
