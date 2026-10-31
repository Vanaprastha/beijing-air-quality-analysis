import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk

# ==========================================
# PENGATURAN HALAMAN
# ==========================================
st.set_page_config(
    page_title="Informasi Kualitas Udara Beijing",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gaya Tampilan CSS Bersih dan Mudah Dibaca
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1.1rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0.1rem 0;
    }
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    .delta-bad {
        color: #DC2626;
    }
    .delta-good {
        color: #16A34A;
    }
    .explanation-box {
        background-color: #F1F5F9;
        border-left: 4px solid #3B82F6;
        padding: 0.9rem 1.1rem;
        border-radius: 0 6px 6px 0;
        margin: 0.8rem 0;
        color: #1E293B;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .alert-box {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 0.9rem 1.1rem;
        border-radius: 0 6px 6px 0;
        margin: 0.8rem 0;
        color: #991B1B;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .success-box {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 0.9rem 1.1rem;
        border-radius: 0 6px 6px 0;
        margin: 0.8rem 0;
        color: #166534;
        font-size: 0.92rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MEMUAT DATA
# ==========================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    
    if not os.path.exists(file_path):
        file_path = "dashboard/main_data.csv"
        
    df = pd.read_csv(file_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = df["datetime"].dt.date
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# ==========================================
# MENU SAMPING (SIDEBAR)
# ==========================================
st.sidebar.title("Pilihan Data")

min_date = df["date"].min()
max_date = df["date"].max()

# Pilihan Tanggal
date_range = st.sidebar.date_input(
    "Rentang Waktu",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Pilihan Stasiun / Lokasi
all_stations = sorted(df["station"].unique().tolist())
select_all = st.sidebar.checkbox("Pilih Semua Lokasi", value=True)

if select_all:
    selected_stations = st.sidebar.multiselect(
        "Lokasi Pemantauan",
        options=all_stations,
        default=all_stations
    )
else:
    selected_stations = st.sidebar.multiselect(
        "Lokasi Pemantauan",
        options=all_stations,
        default=["Dongsi", "Dingling", "Aotizhongxin", "Wanliu"]
    )

if not selected_stations:
    st.sidebar.warning("Silakan pilih minimal satu lokasi pemantauan.")
    st.stop()

# Pilihan Jenis Polutan dengan Nama Awam
pollutant_options = {
    "PM2.5 (Debu Sangat Halus)": "PM2.5",
    "PM10 (Debu Kasar / Pasir)": "PM10",
    "SO2 (Gas Asap Pabrik / Batu Bara)": "SO2",
    "NO2 (Gas Asap Kendaraan)": "NO2",
    "CO (Gas Karbon Monoksida)": "CO",
    "O3 (Gas Ozon di Udara)": "O3"
}

selected_pollutant_label = st.sidebar.selectbox(
    "Jenis Zat Pencemar yang Dilihat",
    options=list(pollutant_options.keys()),
    index=0
)
selected_pollutant = pollutant_options[selected_pollutant_label]

# Penjelasan Singkat Jenis Polutan
with st.sidebar.expander("Bantuan: Apa itu Zat Pencemar Udara?"):
    st.markdown("""
    - **PM2.5**: Debu super halus yang tidak terlihat mata. Bisa masuk langsung ke paru-paru dan pembuluh darah. Batas aman: **75 μg/m³**.
    - **PM10**: Debu kasar seperti debu jalanan atau pasir tertiup angin. Batas aman: **150 μg/m³**.
    - **SO2**: Gas bau menyengat dari pembakaran batu bara di pabrik dan pemanas rumah.
    - **NO2**: Gas cokelat kemerahan dari asap knalpot kendaraan bermotor.
    - **CO**: Gas beracun tak berwarna akibat pembakaran mesin yang tidak sempurna.
    - **O3 (Ozon)**: Gas yang terbentuk saat terik matahari memanaskan asap knalpot, berbahaya bagi mata dan paru-paru.
    """)

# ==========================================
# MENYARING DATA
# ==========================================
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date) &
    (df["station"].isin(selected_stations))
]

if filtered_df.empty:
    st.warning("Tidak ada data pada rentang waktu dan lokasi yang dipilih.")
    st.stop()

# ==========================================
# TAMPILAN UTAMA & RINGKASAN ANGKA PENTING
# ==========================================
st.markdown('<div class="main-header">Informasi Kualitas Udara Beijing (2013–2017)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Panduan praktis kondisi udara harian, waktu aman beraktivitas di luar ruangan, dan wilayah dengan udara paling bersih.</div>', unsafe_allow_html=True)

# 5 Kartu Angka Penting
col1, col2, col3, col4, col5 = st.columns(5)

avg_pm25 = filtered_df["PM2.5"].mean()
avg_pm10 = filtered_df["PM10"].mean()
pct_unhealthy = (filtered_df["PM2.5"] > 75).mean() * 100

st_pm25 = filtered_df.groupby("station")["PM2.5"].mean().sort_values(ascending=False)
worst_station = st_pm25.index[0]
worst_val = st_pm25.iloc[0]
best_station = st_pm25.index[-1]
best_val = st_pm25.iloc[-1]

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Debu Halus (PM2.5)</div>
        <div class="metric-value">{avg_pm25:.1f} <span style="font-size:0.8rem; font-weight:normal;">μg/m³</span></div>
        <div class="metric-delta {'delta-bad' if avg_pm25 > 75 else 'delta-good'}">
            {'Tidak Aman (>75)' if avg_pm25 > 75 else 'Aman Di Bawah 75'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Debu Kasar (PM10)</div>
        <div class="metric-value">{avg_pm10:.1f} <span style="font-size:0.8rem; font-weight:normal;">μg/m³</span></div>
        <div class="metric-delta {'delta-bad' if avg_pm10 > 150 else 'delta-good'}">
            {'Melebihi Batas Aman' if avg_pm10 > 150 else 'Dalam Batas Aman'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Frekuensi Udara Kotor</div>
        <div class="metric-value">{pct_unhealthy:.0f}%</div>
        <div class="metric-delta delta-bad">Waktu bernapas udara kotor</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Lokasi Paling Kotor</div>
        <div class="metric-value" style="font-size:1.25rem;">{worst_station}</div>
        <div class="metric-delta delta-bad">Rata-rata {worst_val:.0f} μg/m³</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Lokasi Paling Bersih</div>
        <div class="metric-value" style="font-size:1.25rem;">{best_station}</div>
        <div class="metric-delta delta-good">Rata-rata {best_val:.0f} μg/m³</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MENU HALAMAN (TABS)
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Kapan Udara Kotor Terjadi? (Musim & Bulan)",
    "Jam Berbahaya vs Jam Aman (Harian)",
    "Peta Lokasi: Mana yang Paling Bersih?",
    "Tingkat Bahaya Udara & Efek Cuaca",
    "Saran Praktis untuk Warga & Kebijakan"
])

# ------------------------------------------
# TAB 1: MUSIM & BULAN
# ------------------------------------------
with tab1:
    st.subheader(f"Perkembangan {selected_pollutant_label} dari Waktu ke Waktu")
    
    tampilan_tren = st.radio("Pilih Tampilan Grafik:", ["Rata-rata Bulanan", "Rata-rata Harian"], horizontal=True)
    
    if "Bulanan" in tampilan_tren:
        filtered_df["year_month"] = filtered_df["datetime"].dt.to_period("M").dt.to_timestamp()
        ts_data = filtered_df.groupby("year_month")[selected_pollutant].mean().reset_index()
        x_col = "year_month"
    else:
        ts_data = filtered_df.groupby("date")[selected_pollutant].mean().reset_index()
        x_col = "date"
        
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=130)
    ax.plot(ts_data[x_col], ts_data[selected_pollutant], color="#2563EB", lw=2, label=f"Tingkat {selected_pollutant}")
    
    if selected_pollutant == "PM2.5":
        ax.axhline(75, color="#EF4444", linestyle="--", lw=1.5, label="Batas Maksimal Udara Aman (75 μg/m³)")
    elif selected_pollutant == "PM10":
        ax.axhline(150, color="#EF4444", linestyle="--", lw=1.5, label="Batas Maksimal Udara Aman (150 μg/m³)")
        
    ax.set_title(f"Grafik Perubahan {selected_pollutant_label}", fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("Waktu", fontsize=9, fontweight="bold")
    ax.set_ylabel("Jumlah Zat Pencemar (μg/m³)", fontsize=9, fontweight="bold")
    ax.legend(frameon=True, facecolor="white", loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("---")
    
    st.subheader(f"Perbandingan Berdasarkan 4 Musim")
    col_m1, col_m2 = st.columns([1.5, 1])
    
    nama_musim = {
        "Spring": "Musim Semi (Maret-Mei)",
        "Summer": "Musim Panas (Juni-Agustus)",
        "Autumn": "Musim Gugur (Sept-Nov)",
        "Winter": "Musim Dingin (Des-Feb)"
    }
    season_order = ["Spring", "Summer", "Autumn", "Winter"]
    musim_df = filtered_df.groupby("season")[selected_pollutant].mean().reindex(season_order).reset_index()
    musim_df["label_musim"] = musim_df["season"].map(nama_musim)
    
    with col_m1:
        fig_m, ax_m = plt.subplots(figsize=(7, 3.8), dpi=130)
        warna = ["#10B981", "#F59E0B", "#F97316", "#EF4444"]
        bars = ax_m.bar(musim_df["label_musim"], musim_df[selected_pollutant], color=warna, edgecolor="#1E293B", alpha=0.85)
        
        for bar in bars:
            h = bar.get_height()
            ax_m.annotate(f"{h:.1f}",
                          xy=(bar.get_x() + bar.get_width() / 2, h),
                          xytext=(0, 3), textcoords="offset points",
                          ha="center", va="bottom", fontsize=9, fontweight="bold")
                          
        ax_m.set_title("Tingkat Polutan Rata-rata per Musim", fontsize=10, fontweight="bold")
        ax_m.set_ylabel("Rata-rata (μg/m³)", fontsize=9, fontweight="bold")
        ax_m.set_xticklabels(["Semi", "Panas", "Gugur", "Dingin"], fontweight="bold")
        ax_m.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_m)
        plt.close()
        
    with col_m2:
        st.markdown("""
        <div class="explanation-box">
            <b>Penjelasan Sederhana Mengenai Musim:</b><br><br>
            • <b>Musim Dingin Paling Berbahaya:</b> Polusi udara selalu melonjak tajam di bulan Desember dan Januari. Hal ini terjadi karena rumah dan gedung di seluruh kota menyalakan pemanas ruangan berbahan batu bara. Ditambah lagi, udara dingin di dekat tanah menahan asap agar tidak bisa terbang ke langit.<br><br>
            • <b>Musim Panas Paling Sedikit Debu:</b> Di musim panas, udara terasa lebih bersih dari debu karena sering turun hujan lebat yang mencuci kotoran di udara.<br><br>
            • <b>Musim Semi Banyak Debu Pasir:</b> Angin kencang dari gurun pasir di utara membawa banyak debu kasar (PM10) ke dalam kota.
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: JAM HARIAN (PAGI - MALAM)
# ------------------------------------------
with tab2:
    st.subheader("Kondisi Udara dari Pagi sampai Malam: Kapan Waktu Paling Aman?")
    st.write("Grafik ini menunjukkan perubahan kualitas udara setiap jam dalam sehari (dari pukul 00.00 malam sampai 23.00 malam).")
    
    jam_df = filtered_df.groupby("hour")[["PM2.5", "PM10", "NO2", "O3"]].mean().reset_index()
    
    col_j1, col_j2 = st.columns([1.6, 1])
    
    with col_j1:
        fig_j, ax_j1 = plt.subplots(figsize=(9, 4.5), dpi=130)
        
        ax_j1.plot(jam_df["hour"], jam_df["PM2.5"], marker="o", color="#DC2626", lw=2, label="Debu Halus (PM2.5)")
        ax_j1.plot(jam_df["hour"], jam_df["NO2"], marker="^", color="#2563EB", lw=2, label="Asap Kendaraan (NO2)")
        ax_j1.set_xlabel("Jam (00.00 Malam - 23.00 Malam)", fontsize=9, fontweight="bold")
        ax_j1.set_ylabel("Debu & Asap Kendaraan (μg/m³)", fontsize=9, fontweight="bold")
        ax_j1.set_xticks(range(0, 24, 2))
        ax_j1.grid(True, linestyle="--", alpha=0.5)
        
        ax_j2 = ax_j1.twinx()
        ax_j2.plot(jam_df["hour"], jam_df["O3"], marker="d", color="#059669", lw=2.2, linestyle="-.", label="Gas Ozon (O3)")
        ax_j2.set_ylabel("Gas Ozon (μg/m³)", fontsize=9, fontweight="bold", color="#059669")
        ax_j2.grid(False)
        
        lines1, labels1 = ax_j1.get_legend_handles_labels()
        lines2, labels2 = ax_j2.get_legend_handles_labels()
        ax_j1.legend(lines1 + lines2, labels1 + labels2, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=True)
        
        plt.title("Perubahan Kualitas Udara Selama 24 Jam", fontsize=11, fontweight="bold", pad=10)
        plt.tight_layout()
        st.pyplot(fig_j)
        plt.close()
        
    with col_j2:
        st.markdown("""
        <div class="alert-box">
            <b>Jam Paling Berbahaya (20.00 Malam – 02.00 Dini Hari):</b><br>
            Tingkat debu halus dan asap kendaraan mencapai puncak tertingginya pada malam hari. Hal ini disebabkan oleh armada truk-truk besar bermesin diesel yang baru diizinkan melintasi jalan kota pada malam hari, ditambah suhu malam yang memerangkap asap di permukaan tanah.
        </div>
        <div class="success-box">
            <b>Jam Paling Aman Beraktivitas (10.00 Pagi – 12.00 Siang):</b><br>
            Jika Anda ingin berolahraga, menjemur pakaian, atau mengajak anak bermain di luar rumah, waktu terbaik adalah sekitar jam 10 hingga 12 siang. Pada jam ini, debu malam sudah buyar dan gas ozon matahari belum memuncak.
        </div>
        <div class="explanation-box">
            <b>Waspada Siang Terik (14.00 – 16.00 Sore):</b><br>
            Meskipun debu sedikit, sinar matahari yang terik memanaskan sisa gas knalpot menjadi gas ozon. Gas ini dapat membuat mata perih dan tenggorokan gatal.
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: PETA LOKASI
# ------------------------------------------
with tab3:
    st.subheader("Peta Lokasi: Wilayah Mana yang Paling Bersih dan Paling Tercemar?")
    st.write("Titik lingkaran pada peta menunjukkan 12 stasiun pemantau di Beijing. Semakin merah dan besar lingkarannya, semakin kotor udaranya.")
    
    col_p1, col_p2 = st.columns([1.2, 1])
    
    st_agg = filtered_df.groupby("station").agg({
        "PM2.5": "mean",
        "latitude": "first",
        "longitude": "first",
        "zone": "first",
        "is_unhealthy": lambda x: (x.mean() * 100)
    }).reset_index().rename(columns={"is_unhealthy": "pct_unhealthy"})
    
    with col_p1:
        st.markdown("##### Peta Sebaran Lokasi Pemantauan")
        min_p = st_agg["PM2.5"].min()
        max_p = st_agg["PM2.5"].max()
        
        def ambil_warna(val):
            rasio = (val - min_p) / (max_p - min_p + 1e-5)
            r = int(50 + 205 * rasio)
            g = int(200 * (1 - rasio))
            b = 50
            return [r, g, b, 200]
            
        st_agg["color"] = st_agg["PM2.5"].apply(ambil_warna)
        st_agg["radius"] = st_agg["PM2.5"].apply(lambda x: x * 35)
        
        view_state = pdk.ViewState(
            latitude=40.05,
            longitude=116.40,
            zoom=8.8,
            pitch=20
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=st_agg,
            get_position=["longitude", "latitude"],
            get_color="color",
            get_radius="radius",
            pickable=True,
            auto_highlight=True
        )
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{station} ({zone})\nRata-rata PM2.5: {PM2.5:.1f} μg/m³\nPersentase Udara Kotor: {pct_unhealthy:.0f}%"}
        )
        st.pydeck_chart(deck)
        
    with col_p2:
        st.markdown("##### Urutan Lokasi (Dari Paling Bersih ke Paling Kotor)")
        sorted_st = st_agg.sort_values(by="PM2.5", ascending=True)
        
        fig_bar, ax_bar = plt.subplots(figsize=(6, 4.8), dpi=130)
        warna_batang = ["#16A34A" if x < 75 else "#DC2626" for x in sorted_st["PM2.5"]]
        bars = ax_bar.barh(sorted_st["station"], sorted_st["PM2.5"], color=warna_batang, edgecolor="#1E293B", alpha=0.85)
        
        for bar in bars:
            w = bar.get_width()
            ax_bar.annotate(f"{w:.0f}",
                            xy=(w, bar.get_y() + bar.get_height() / 2),
                            xytext=(3, 0), textcoords="offset points",
                            ha="left", va="center", fontsize=8, fontweight="bold")
                            
        ax_bar.set_xlim(0, sorted_st["PM2.5"].max() * 1.15)
        ax_bar.set_xlabel("Rata-rata Debu Halus PM2.5 (μg/m³)", fontsize=8.5, fontweight="bold")
        ax_bar.set_title("Hijau: Lebih Bersih | Merah: Terlalu Kotor", fontsize=9.5, fontweight="bold")
        ax_bar.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_bar)
        plt.close()

    st.markdown("""
    <div class="explanation-box">
        <b>Mengapa Lokasi Berbeda-beda?</b><br>
        • <b>Pusat Kota & Kawasan Barat Paling Tercemar (Dongsi, Wanshouxigong, Gucheng):</b> Banyak gedung tinggi yang menghalangi angin, kemacetan kendaraan padat, dan dekat dengan kawasan industri.<br>
        • <b>Wilayah Utara Paling Bersih (Dingling & Huairou):</b> Dekat dengan area pegunungan dan hutan yang banyak menghasilkan udara segar alami, serta jauh dari pabrik.
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: TINGKAT BAHAYA & CUACA
# ------------------------------------------
with tab4:
    st.subheader("Seberapa Sering Udara Berbahaya & Bagaimana Pengaruh Cuaca?")
    
    col_k1, col_k2 = st.columns(2)
    
    with col_k1:
        st.markdown("##### Pembagian Kualitas Udara yang Dihirup Warga")
        
        label_terjemahan = {
            "Good": "Baik (Aman)",
            "Moderate": "Sedang",
            "Unhealthy for Sensitive": "Kurang Sehat (Bagi yang Sensitif)",
            "Unhealthy": "Tidak Sehat",
            "Very Unhealthy": "Sangat Tidak Sehat",
            "Hazardous": "Berbahaya"
        }
        
        kategori_counts = filtered_df["PM2.5_category"].value_counts(normalize=True).reindex([
            "Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"
        ]) * 100
        
        labels_indo = [label_terjemahan[k] for k in kategori_counts.index]
        warna_kategori = ["#10B981", "#FBBF24", "#F97316", "#EF4444", "#9333EA", "#7F1D1D"]
        
        fig_donut, ax_donut = plt.subplots(figsize=(6, 4.2), dpi=130)
        wedges, texts, autotexts = ax_donut.pie(
            kategori_counts.values,
            labels=labels_indo,
            autopct="%1.0f%%",
            colors=warna_kategori,
            startangle=140,
            textprops={"fontsize": 7.5},
            pctdistance=0.78
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")
            
        lingkaran_tengah = plt.Circle((0,0), 0.55, fc="white")
        fig_donut.gca().add_artist(lingkaran_tengah)
        ax_donut.axis("equal")
        plt.title("Persentase Waktu Berdasarkan Kategori Udara", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig_donut)
        plt.close()
        
    with col_k2:
        st.markdown("##### Pengaruh Cuaca terhadap Debu PM2.5")
        st.markdown("""
        Cuaca sangat menentukan apakah asap polusi akan cepat hilang atau justru menumpuk menjadi kabut asap tebal:
        <br><br>
        1. <b>Kecepatan Angin (Hubungan Linear Negatif Relatif Lemah, r = -0.27):</b><br>
        Secara statistik, kecepatan angin memiliki korelasi negatif yang relatif lemah dengan PM2.5 (r = -0.27). Hal ini menunjukkan adanya kecenderungan debu berkurang ketika angin bertiup lebih kencang. Namun, nilai korelasi ini tidak membuktikan hubungan sebab-akibat langsung karena penumpukan polusi juga dipengaruhi oleh suhu dingin, kelembapan, dan asap yang terus diproduksi.<br><br>
        2. <b>Suhu Udara Dingin:</b><br>
        Suhu dingin sering kali menciptakan "tutup udara" (inversi suhu) di mana udara hangat di atas menahan udara dingin di bawah, mengurung asap polusi tepat di dekat hidung warga.<br><br>
        3. <b>Curah Hujan:</b><br>
        Tetesan air hujan menyerap dan menjatuhkan partikel debu halus ke tanah, membuat udara terasa lebih segar setelah hujan turun.
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: SARAN PRAKTIS & KEBIJAKAN
# ------------------------------------------
with tab5:
    st.subheader("Panduan Praktis untuk Warga & Rekomendasi Kebijakan")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("### Panduan untuk Masyarakat Sehari-hari")
        st.markdown("""
        1. **Pilih Jam yang Tepat untuk Berolahraga:**
           - Jangan berolahraga di luar ruangan pada malam hari atau subuh hari karena konsentrasi debu halus sedang berada di puncaknya.
           - Waktu paling ideal untuk jalan pagi atau berolahraga di luar adalah antara pukul **10.00 hingga 12.00 siang**.
        
        2. **Gunakan Masker Standar di Musim Dingin:**
           - Pada bulan Desember hingga Februari, gunakan masker penyaring partikel (seperti masker N95 atau KN95) saat beraktivitas di luar rumah.
        
        3. **Gunakan Penyaring Udara (Air Purifier) di Rumah:**
           - Bagi warga yang tinggal di pusat kota (seperti kawasan Dongsi dan Wanshouxigong), penggunaan alat penyaring udara di kamar tidur sangat membantu menjaga kesehatan pernapasan keluarga.
        
        4. **Batasi Aktivitas Siang Terik di Musim Panas:**
           - Hindari berada di bawah terik matahari pada pukul 14.00 - 16.00 saat musim panas untuk menghindari paparan gas ozon yang dapat mengiritasi mata dan saluran napas.
        """)
        
    with col_s2:
        st.markdown("### Rekomendasi Kebijakan untuk Pemerintah Daerah")
        st.markdown("""
        1. **Percepat Penggantian Pemanas Batu Bara:**
           - Mengganti sistem pemanas rumah dan gedung dari batu bara ke gas alam atau listrik ramah lingkungan sebelum memasuki musim dingin.
        
        2. **Atur Ulang Jam Masuk Truk Diesel:**
           - Membatasi truk diesel berat yang melintasi jalan lingkar dalam kota pada malam hari, dan memberikan insentif untuk peralihan ke truk listrik.
        
        3. **Peringatan Dini untuk Sekolah:**
           - Mewajibkan sekolah dan fasilitas umum untuk membatasi aktivitas fisik murid di lapangan saat angka pemantauan PM2.5 melebihi batas 75 μg/m³.
        
        4. **Jaga Wilayah Hijau di Pegunungan Utara:**
           - Melindungi hutan dan perbukitan di kawasan Dingling dan Huairou sebagai paru-paru kota alami yang mengalirkan udara bersih ke pusat kota.
        """)

# ==========================================
# BAGIAN BAWAH (FOOTER BERSIH)
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.85rem;">
    Informasi Kualitas Udara Beijing (2013–2017) | Sumber Data: PRSA Beijing Air Quality
</div>
""", unsafe_allow_html=True)
