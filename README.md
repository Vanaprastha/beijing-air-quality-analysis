# 🌫️ Proyek Analisis Data: Beijing Air Quality Dataset

Repositori ini memuat berkas analisis data komprehensif dan dashboard interaktif untuk **Beijing Multi-Site Air Quality Data**, sebagai tugas akhir kelas **Belajar Analisis Data dengan Python / Fundamental Analisis Data** di [Dicoding Indonesia](https://www.dicoding.com/).

- **Nama Mahasiswa:** vanaprastha2256
- **Email:** vanaprastha2256@dicoding.org
- **ID Dicoding:** vanaprastha2256

---

## 📌 Deskripsi & Pertanyaan Bisnis (Metode SMART)

Proyek ini menganalisis data kualitas udara historis dari **12 stasiun pemantau di Beijing** selama 4 tahun penuh (**Maret 2013 hingga Februari 2017**, total 420.768 observasi per jam).

Analisis berfokus pada 3 pertanyaan bisnis utama yang disusun secara independen dan terukur:

1. **Pertanyaan 1 (Tren Polutan Musiman & Bulanan):**
   > *"Bagaimana tren konsentrasi polutan partikulat utama ($PM_{2.5}$ dan $PM_{10}$) di Beijing sepanjang periode Maret 2013 hingga Februari 2017, serta pada bulan dan musim apa konsentrasi polutan mencapai nilai rata-rata tertinggi dan terendah?"*
2. **Pertanyaan 2 (Pola Fluktuasi Jam Harian / Diurnal):**
   > *"Bagaimana pola fluktuasi konsentrasi polutan udara per jam ($PM_{2.5}$, $PM_{10}$, $NO_2$, dan $O_3$) dalam siklus 24 jam (pukul 00:00–23:00) di Beijing selama periode 2013–2017, dan pada jam berapa konsentrasi masing-masing polutan mencapai titik puncak serta titik terendah?"*
3. **Pertanyaan 3 (Perbandingan Spasial Antar-Stasiun):**
   > *"Bagaimana variasi konsentrasi rata-rata $PM_{2.5}$ antar-12 stasiun pemantau di Beijing selama periode 2013–2017, dan stasiun mana yang mencatat persentase jam dengan konsentrasi $PM_{2.5} > 75\ \mu g/m^3$ (kategori tidak sehat menurut standar harian Tiongkok) tertinggi serta terendah?"*
4. **Analisis Lanjutan (Geospatial & Clustering / AQI Binning):**
   > Pemetaan sebaran spasial 12 stasiun pemantau berdasarkan koordinat asli (*latitude* dan *longitude*), pengelompokan frekuensi kategori baku mutu AQI ($PM_{2.5}$), dan analisis hubungan linear parameter meteorologi.

---

## 📁 Struktur Direktori Proyek

```text
submission/
├── dashboard/
│   ├── main_data.csv          # Dataset bersih dan beranotasi untuk dashboard
│   └── dashboard.py           # Aplikasi Streamlit dengan bahasa awam dan informatif
├── data/
│   ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv
│   ├── PRSA_Data_Changping_20130301-20170228.csv
│   ├── PRSA_Data_Dingling_20130301-20170228.csv
│   ├── PRSA_Data_Dongsi_20130301-20170228.csv
│   ├── PRSA_Data_Guanyuan_20130301-20170228.csv
│   ├── PRSA_Data_Gucheng_20130301-20170228.csv
│   ├── PRSA_Data_Huairou_20130301-20170228.csv
│   ├── PRSA_Data_Nongzhanguan_20130301-20170228.csv
│   ├── PRSA_Data_Shunyi_20130301-20170228.csv
│   ├── PRSA_Data_Tiantan_20130301-20170228.csv
│   ├── PRSA_Data_Wanliu_20130301-20170228.csv
│   └── PRSA_Data_Wanshouxigong_20130301-20170228.csv
├── notebook.ipynb             # Jupyter Notebook lengkap dan telah dieksekusi
├── README.md                  # Dokumentasi proyek dan panduan eksekusi
├── requirements.txt           # Daftar pustaka dependensi Python
└── url.txt                    # Tautan dashboard di Streamlit Community Cloud
```

---

## ⚙️ Panduan Menjalankan Proyek Secara Lokal

### 1. Masuk ke Direktori Proyek
```bash
cd "/home/vanaprastha/Videos/PRODUK/DICODING ASAH/fundamental analisis data"
```

### 2. Pasang Dependensi
```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard Streamlit
```bash
streamlit run dashboard/dashboard.py
```
Aplikasi dashboard akan otomatis terbuka di peramban pada alamat `http://localhost:8501`.

---

## 🚀 Panduan Deploy ke Streamlit Community Cloud

Agar tautan pada `url.txt` aktif di akun Streamlit Cloud Anda (`vanaprastha2256`):
1. Buat repositori baru di GitHub pribadi Anda (misalnya: `beijing-air-quality-analysis`).
2. Unggah seluruh isi folder proyek ini ke repositori tersebut.
3. Masuk ke [Streamlit Community Cloud](https://share.streamlit.io/) menggunakan akun GitHub Anda.
4. Klik tombol **"Create app"** lalu pilih repositori Anda.
5. Masukkan konfigurasi:
   - **Main file path:** `dashboard/dashboard.py`
   - **App URL (Custom subdomain):** `beijing-air-quality-vanaprastha2256`
6. Klik **"Deploy"**. Aplikasi Anda akan aktif di alamat:
   👉 `https://beijing-air-quality-vanaprastha2256.streamlit.app/`

---

## 📊 Rangkuman Temuan Berdasarkan Perhitungan Data

| Parameter | Temuan Hasil Perhitungan Dataset | Keterangan Domain |
| :--- | :--- | :--- |
| **Rata-rata Keseluruhan** | $PM_{2.5} = 79,84\ \mu g/m^3$, $PM_{10} = 104,91\ \mu g/m^3$ | Melebihi standar baku mutu harian Tiongkok ($75\ \mu g/m^3$). |
| **Puncak Musiman PM2.5** | Musim Dingin ($95,74\ \mu g/m^3$); Bulan Desember ($103,68\ \mu g/m^3$) | Dipengaruhi pemanas ruangan batu bara dan inversi suhu. |
| **Titik Terendah PM2.5** | Musim Panas ($64,52\ \mu g/m^3$); Bulan Agustus ($53,47\ \mu g/m^3$) | Dipengaruhi curah hujan yang membersihkan debu atmosfer. |
| **Puncak Musiman PM10** | Musim Semi ($120,87\ \mu g/m^3$); Bulan Maret ($135,97\ \mu g/m^3$) | Dipengaruhi badai pasir dari wilayah gurun utara. |
| **Puncak Diurnal PM2.5 & NO2**| Malam hari pukul 21:00–22:00 ($PM_{2.5} = 89,03\ \mu g/m^3$) | Aktivitas truk diesel malam hari dan penurunan batas atmosfer. |
| **Puncak Diurnal Ozon (O3)** | Sore hari pukul 16:00 ($O_3 = 101,96\ \mu g/m^3$) | Reaksi fotokimia akibat paparan sinar matahari terik. |
| **Jam Relatif Aman** | Pagi menjelang siang hari (pukul 10:00–12:00) | Waktu paling seimbang sebelum lonjakan ozon sore hari. |
| **Stasiun Paling Tercemar** | Dongsi ($PM_{2.5} = 86,14\ \mu g/m^3$; $42,52\%$ jam tidak sehat) | Terletak di pusat kota yang padat gedung dan lalu lintas. |
| **Stasiun Paling Bersih** | Dingling ($PM_{2.5} = 66,85\ \mu g/m^3$; $31,77\%$ jam tidak sehat) | Terletak di kawasan utara dekat pegunungan dan hutan. |
| **Korelasi Kecepatan Angin** | $r = -0,27$ (Korelasi linear negatif relatif lemah) | Menunjukkan tren berkurangnya debu saat angin kencang, namun bukan faktor tunggal penyebab akumulasi polusi. |
