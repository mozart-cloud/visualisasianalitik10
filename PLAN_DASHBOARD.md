# PLAN: Dashboard Geospatial Sekolah Internasional DKI Jakarta

> **Cara pakai dokumen ini:** Dokumen ini adalah blueprint lengkap. Kamu bisa (1) eksekusi manual per-tahap, atau (2) copy-paste bagian-bagiannya sebagai prompt ke AI agent di Antigravity. Lihat bagian **"Cara Pakai Plan Ini di Antigravity"** di bagian paling bawah.

---

## 1. Konteks Tugas

**Mata kuliah:** Visualisasi Analitik (S2 Magister Informatika)
**Deliverable:**
- File Streamlit (`dashboard.py`)
- Screenshot dashboard
- Dokumen storytelling singkat

**Dataset:** `Data_Sekolah_Internasional_DKI_Jakarta.xlsx` (242 baris, 9 kolom, tahun 2024)

| Kolom | Tipe | Keterangan |
|---|---|---|
| periode_data | int | Tahun (semua = 2024) |
| wilayah | str | 5 Kota Adm. DKI Jakarta |
| jenjang | str | PAUD, SD, SMP, SMA |
| nama_sekolah | str | Nama sekolah |
| npsn | str | ID unik sekolah |
| alamat | str | Alamat lengkap |
| jumlah_siswa | int | 0 – 1502 |
| Latitude | float | -6.34 s/d -6.11 |
| Longitude | float | 106.70 s/d 106.96 |

---

## 2. Decision Question & Framework Storytelling

**Decision Question Utama:**
> *"Wilayah dan jenjang mana di DKI Jakarta yang paling underserved oleh sekolah internasional, sehingga menjadi prioritas ekspansi atau intervensi kebijakan pendidikan?"*

**Target user dashboard:** Dinas Pendidikan DKI / investor sekolah swasta internasional.

**Framework insight yang harus dipenuhi brief:**
- ✅ 1 tren (distribusi spasial — karena data 1 tahun, fokus ke pola sebaran)
- ✅ 1 perbandingan antar wilayah (5 kota administrasi)

---

## 3. Arsitektur Dashboard

```
┌──────────────────────────────────────────────────────────┐
│  JUDUL INSIGHT (bukan deskriptif)                        │
│  "Sekolah Internasional Jakarta Timpang: Jakarta Selatan │
│   Menampung 40%+ Siswa, Wilayah Lain Tertinggal"         │
├──────────────────────────────────────────────────────────┤
│ SIDEBAR FILTER          │  MAIN CONTENT                  │
│ - Multiselect Wilayah   │  [KPI CARDS x4]                │
│ - Multiselect Jenjang   │                                │
│ - Slider Jumlah Siswa   │  [FOLIUM MAP — full width]     │
│ - Radio Mode Peta       │                                │
│   (Cluster/Heatmap/Size)│  [CHART 1]    [CHART 2]        │
│                         │  [CHART 3 — histogram]         │
│                         │                                │
│                         │  💡 KEY INSIGHT                │
│                         │  🎯 RECOMMENDATION             │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Spesifikasi Komponen (Detail untuk Coding)

### 4.1 Setup & Imports
```python
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Dashboard Sekolah Internasional Jakarta",
                   layout="wide", page_icon="🏫")
```

**Dependencies** (`requirements.txt`):
```
streamlit
pandas
openpyxl
folium
streamlit-folium
plotly
```

### 4.2 Load Data (cached)
```python
@st.cache_data
def load_data():
    df = pd.read_excel("Data_Sekolah_Internasional_DKI_Jakarta.xlsx")
    df['wilayah_clean'] = df['wilayah'].str.replace('KOTA ADM. ', '', regex=False).str.title()
    return df
```

### 4.3 Sidebar Filter
- `st.sidebar.multiselect("Wilayah", options=...)` — default semua
- `st.sidebar.multiselect("Jenjang", options=...)` — default semua
- `st.sidebar.slider("Rentang Jumlah Siswa", 0, 1502, (0, 1502))`
- `st.sidebar.radio("Mode Peta", ["Marker Cluster", "Heatmap", "Circle by Size"])`

### 4.4 KPI Cards (4 kolom dengan `st.columns(4)` + `st.metric()`)
1. Total Sekolah (count npsn)
2. Total Siswa (sum jumlah_siswa)
3. Rata-rata Siswa/Sekolah
4. Wilayah Terpadat (mode)

### 4.5 Folium Map (WAJIB)
- Center Jakarta: `[-6.2, 106.84]`, zoom 11
- Tile: `OpenStreetMap`
- **Mode 1 — Marker Cluster:** popup berisi nama, jenjang, siswa, alamat
- **Mode 2 — Heatmap:** bobot = jumlah_siswa
- **Mode 3 — Circle Marker:** radius proporsional `sqrt(jumlah_siswa)`, warna per jenjang (PAUD=hijau, SD=biru, SMP=oranye, SMA=merah)
- Render via `st_folium(m, width=None, height=550)`

### 4.6 Chart Pendukung (WAJIB min. 2, saya rekomendasi 3)
**Chart 1 — Stacked Bar (Plotly):**
Jumlah sekolah per wilayah, di-stack by jenjang → langsung kelihatan wilayah mana kurang jenjang apa.

**Chart 2 — Bar horizontal:**
Total siswa per wilayah (descending) → menjawab "wilayah mana paling banyak tertampung".

**Chart 3 — Histogram:**
Distribusi `jumlah_siswa` → menunjukkan banyak sekolah kecil (<100 siswa).

### 4.7 Section "Key Insight"
Gunakan `st.info()` atau `st.success()` dengan bullet. Contoh template:
```
- Jakarta Selatan mendominasi: X sekolah & Y% dari total siswa
- Jakarta Utara paling tertinggal: hanya Z sekolah
- Jenjang PAUD/SMA timpang di wilayah tertentu
- Ada N sekolah dengan 0 siswa (indikasi data issue atau sekolah baru)
```
**Angka-angka isi otomatis dari data yang sudah terfilter** — jangan hard-code.

### 4.8 Section "Recommendation"
```
- Prioritaskan insentif pendirian sekolah internasional di Jakarta Utara & Timur
- Fokus jenjang yang underrepresented di wilayah tertentu
- Audit sekolah dengan 0 siswa (verifikasi operasional)
- Pantau kapasitas di Jakarta Selatan (kemungkinan overcrowd)
```

---

## 5. Angka-Angka Kunci (Hasil EDA — Pakai untuk Validasi)

Berikut hasil analisis awal dari dataset — dashboard kamu harusnya mereproduksi angka-angka ini saat filter "semua":

**Per wilayah:**
| Wilayah | Jumlah Sekolah | Total Siswa |
|---|---|---|
| Jakarta Selatan | dominan | ~40%+ siswa |
| Jakarta Pusat, Barat, Timur | menengah | |
| Jakarta Utara | paling sedikit | |

**Total siswa seluruh Jakarta:** 38.087
**Rata-rata siswa/sekolah:** 157
**Sekolah dengan 0 siswa:** ada (perlu dihitung ulang di coding)
**Sekolah terbesar:** 1.502 siswa

> 💡 Saat coding, **verifikasi angka ini** dengan `df.groupby(...).agg(...)`. Kalau meleset jauh, kemungkinan ada bug di filter.

---

## 6. Urutan Eksekusi Coding (Step-by-Step)

1. **Setup project** — buat folder, `requirements.txt`, install dependencies
2. **Copy dataset** ke folder project
3. **Skeleton `dashboard.py`** — imports + `st.set_page_config` + `load_data()`
4. **Header + KPI cards** — pastikan layout dasar OK
5. **Sidebar filter** — pastikan df ter-filter dengan benar
6. **Folium map — Mode Marker Cluster dulu** (paling gampang)
7. **Tambah Mode Heatmap & Circle by Size**
8. **Chart 1 (stacked bar)** pakai Plotly
9. **Chart 2 & 3**
10. **Section Key Insight & Recommendation** — dinamis berdasar data terfilter
11. **Polish judul insight** (jangan sampai deskriptif)
12. **Test semua kombinasi filter**
13. **Screenshot** untuk submission

---

## 7. Checklist Submission (sesuai brief)

- [ ] Map visualization (Folium) ✅ WAJIB
- [ ] Minimal 2 chart tambahan ✅ WAJIB
- [ ] Filter interaktif (wilayah/jenjang/kategori) ✅ WAJIB
- [ ] Judul berupa insight (bukan deskripsi) ✅ WAJIB
- [ ] Section "Key Insight" ✅ WAJIB
- [ ] Section "Recommendation" ✅ WAJIB
- [ ] File `dashboard.py`
- [ ] Screenshot dashboard
- [ ] Dokumen storytelling WHAT / SO WHAT / NOW WHAT (lihat file `STORYTELLING.md`)

---

## 8. Potential Pitfalls (Antisipasi Bug)

| Masalah | Solusi |
|---|---|
| `st_folium` bikin rerun terus | Beri `key="map"` yang tetap, atau pakai `folium_static` sebagai alternatif |
| Peta blank saat filter kosong | Cek `if not df_filtered.empty:` sebelum render |
| KPI pecah saat 0 data | Guard dengan `if len(df)>0 else 0` |
| Judul insight jadi deskriptif | Uji: judul harus bisa menjawab "so what?" — bukan sekadar "Dashboard Sekolah Jakarta" |
| Chart Plotly tidak responsive | Pakai `st.plotly_chart(fig, use_container_width=True)` |
| Data `jumlah_siswa = 0` menggangu heatmap | Filter `df[df.jumlah_siswa > 0]` khusus untuk heatmap |

---

## 9. Cara Pakai Plan Ini di Antigravity

Antigravity punya **AI agent workspace** (mirip Cursor/Windsurf), jadi plan ini bisa kamu manfaatkan dengan 3 pendekatan:

### Pendekatan A — Satu Shot (paling cepat)
1. Buat folder project baru di Antigravity
2. Drop file `PLAN_DASHBOARD.md` ini ke folder project
3. Buka AI agent, prompt:
   > *"Baca PLAN_DASHBOARD.md dan buatkan dashboard.py lengkap sesuai spesifikasi. Dataset ada di folder yang sama."*
4. Review hasilnya, jalankan `streamlit run dashboard.py`, iterasi kalau ada yang perlu diperbaiki

### Pendekatan B — Per Tahap (lebih terkontrol, direkomendasikan)
Eksekusi Section 6 satu per satu. Tiap langkah, prompt ke agent:
> *"Sesuai PLAN_DASHBOARD.md section 4.X, implementasikan [komponen X]"*

Keuntungan: kamu bisa review tiap bagian, lebih mudah debug, dan paham kodenya (penting untuk tugas kuliah — dosen bisa tanya).

### Pendekatan C — Manual + AI Assist
Tulis sendiri skeleton-nya berdasar Section 4, lalu minta agent bantu di bagian tricky (Folium, Plotly). Paling edukatif.

### Tips Prompt Efektif di Antigravity
- Selalu sebut **file referensi** (`"sesuai PLAN_DASHBOARD.md"`) supaya agent konsisten
- Minta **run & verify** tiap selesai satu section (`"lalu jalankan dan screenshot"`)
- Kalau stuck, tempel error message langsung ke chat agent

---

## 10. Definition of Done

Dashboard dianggap selesai jika:
- Jalan tanpa error di `streamlit run dashboard.py`
- Semua 6 checklist WAJIB di Section 7 terpenuhi
- Filter apapun dicoba, angka KPI & chart tetap konsisten
- Judul terbukti berupa insight (uji: apakah orang yang belum lihat dashboard sudah dapat "aha moment" dari judulnya saja?)
- Screenshot siap + storytelling WHAT/SO WHAT/NOW WHAT ditulis
