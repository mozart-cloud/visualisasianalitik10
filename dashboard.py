"""
Dashboard Geospatial — Sekolah Internasional DKI Jakarta
Mata kuliah: Visualisasi Analitik (S2 Magister Informatika)

Decision Question:
  "Wilayah dan jenjang mana di DKI Jakarta yang paling underserved
   oleh sekolah internasional, sehingga menjadi prioritas ekspansi
   atau intervensi kebijakan pendidikan?"
"""

# ── Imports ──────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np

# ── Poverty Data (BPS Maret 2023) ───────────────────────────────────
# Sumber: https://databoks.katadata.co.id — Persentase Penduduk Miskin per Kota Adm.
POVERTY_DATA = {
    "Kepulauan Seribu": 13.13,
    "Jakarta Utara": 6.78,
    "Jakarta Pusat": 4.68,
    "Jakarta Timur": 4.20,
    "Jakarta Barat": 4.09,
    "Jakarta Selatan": 3.10,
}

# ── Batas Wilayah Kota Adm. (simplified polygons) ──────────────────
# Sumber: github.com/rifani/geojson-political-indonesia (GADM)
JAKARTA_BOUNDARIES = {
    "Jakarta Barat": [[106.7088, -6.0961], [106.7116, -6.1033], [106.7298, -6.1242], [106.74, -6.1316], [106.7638, -6.1405], [106.7747, -6.1396], [106.7774, -6.1435], [106.8011, -6.1409], [106.8027, -6.1356], [106.8156, -6.1324], [106.8195, -6.1373], [106.8268, -6.1536], [106.8276, -6.161], [106.8171, -6.159], [106.8005, -6.1618], [106.7996, -6.1677], [106.8101, -6.1836], [106.8101, -6.1881], [106.8028, -6.1988], [106.7933, -6.2089], [106.7826, -6.2083], [106.781, -6.2146], [106.7692, -6.2184], [106.7444, -6.2204], [106.7388, -6.2225], [106.7187, -6.2233], [106.7226, -6.2023], [106.7189, -6.1859], [106.6888, -6.1742], [106.6855, -6.1695], [106.6815, -6.1355], [106.6848, -6.1172], [106.6892, -6.1047], [106.6856, -6.0991], [106.7002, -6.0978], [106.7088, -6.0961]],
    "Jakarta Pusat": [[106.8793, -6.1683], [106.8762, -6.1806], [106.8751, -6.1931], [106.8692, -6.1933], [106.8541, -6.2017], [106.8563, -6.2065], [106.8516, -6.21], [106.8488, -6.2109], [106.8251, -6.2051], [106.822, -6.2144], [106.8052, -6.2295], [106.798, -6.2295], [106.7982, -6.2165], [106.7933, -6.2089], [106.8028, -6.1988], [106.8101, -6.1881], [106.8101, -6.1836], [106.7996, -6.1677], [106.8005, -6.1618], [106.8171, -6.159], [106.8276, -6.161], [106.8268, -6.1536], [106.8195, -6.1373], [106.8304, -6.1357], [106.8369, -6.1458], [106.8402, -6.1419], [106.8501, -6.144], [106.8531, -6.1531], [106.8593, -6.153], [106.8777, -6.1635], [106.8793, -6.1683]],
    "Jakarta Selatan": [[106.8516, -6.21], [106.8594, -6.2146], [106.8598, -6.2199], [106.866, -6.2239], [106.8674, -6.2352], [106.865, -6.2514], [106.8598, -6.2564], [106.8578, -6.272], [106.8502, -6.2824], [106.8506, -6.2908], [106.854, -6.2982], [106.854, -6.3062], [106.8574, -6.3059], [106.8593, -6.3148], [106.8432, -6.323], [106.8445, -6.3301], [106.8426, -6.3484], [106.837, -6.3545], [106.8197, -6.3562], [106.8121, -6.3626], [106.8016, -6.364], [106.7946, -6.3617], [106.7946, -6.3521], [106.8008, -6.3347], [106.8084, -6.3187], [106.805, -6.3145], [106.7796, -6.3173], [106.7759, -6.3167], [106.7689, -6.3005], [106.7642, -6.2946], [106.7612, -6.2831], [106.751, -6.2743], [106.7525, -6.2625], [106.7516, -6.2542], [106.7427, -6.2333], [106.7365, -6.2299], [106.7248, -6.229], [106.7187, -6.2233], [106.7388, -6.2225], [106.7444, -6.2204], [106.7692, -6.2184], [106.781, -6.2146], [106.7826, -6.2083], [106.7933, -6.2089], [106.7982, -6.2165], [106.798, -6.2295], [106.8052, -6.2295], [106.822, -6.2144], [106.8251, -6.2051], [106.8488, -6.2109], [106.8516, -6.21]],
    "Jakarta Timur": [[106.9725, -6.1477], [106.9729, -6.1742], [106.9716, -6.1943], [106.9685, -6.2034], [106.9554, -6.2227], [106.9477, -6.2403], [106.9453, -6.2554], [106.9256, -6.2589], [106.9092, -6.264], [106.9077, -6.2745], [106.912, -6.278], [106.9118, -6.2977], [106.9222, -6.3067], [106.9221, -6.3212], [106.9165, -6.3304], [106.9162, -6.359], [106.9094, -6.3755], [106.9032, -6.3767], [106.8829, -6.3661], [106.8793, -6.3617], [106.8627, -6.3575], [106.859, -6.3495], [106.8463, -6.3469], [106.8426, -6.3484], [106.8445, -6.3301], [106.8432, -6.323], [106.8593, -6.3148], [106.8574, -6.3059], [106.854, -6.3062], [106.854, -6.2982], [106.8506, -6.2908], [106.8502, -6.2824], [106.8578, -6.272], [106.8598, -6.2564], [106.865, -6.2514], [106.8674, -6.2352], [106.866, -6.2239], [106.8598, -6.2199], [106.8594, -6.2146], [106.8516, -6.21], [106.8563, -6.2065], [106.8541, -6.2017], [106.8692, -6.1933], [106.8751, -6.1931], [106.8762, -6.1806], [106.8793, -6.1683], [106.8852, -6.167], [106.8988, -6.1765], [106.9133, -6.1814], [106.9253, -6.1823], [106.9295, -6.1801], [106.9252, -6.1684], [106.9283, -6.1594], [106.9453, -6.1577], [106.9514, -6.1597], [106.9578, -6.1549], [106.9725, -6.1477]],
    "Jakarta Utara": [[106.9728, -6.0911], [106.9725, -6.1477], [106.9578, -6.1549], [106.9514, -6.1597], [106.9453, -6.1577], [106.9283, -6.1594], [106.9252, -6.1684], [106.9295, -6.1801], [106.9253, -6.1823], [106.9133, -6.1814], [106.8988, -6.1765], [106.8852, -6.167], [106.8793, -6.1683], [106.8777, -6.1635], [106.8593, -6.153], [106.8531, -6.1531], [106.8501, -6.144], [106.8402, -6.1419], [106.8369, -6.1458], [106.8304, -6.1357], [106.8195, -6.1373], [106.8156, -6.1324], [106.8027, -6.1356], [106.8011, -6.1409], [106.7774, -6.1435], [106.7747, -6.1396], [106.7638, -6.1405], [106.74, -6.1316], [106.7298, -6.1242], [106.7116, -6.1033], [106.7088, -6.0961], [106.7245, -6.0892], [106.7344, -6.0985], [106.7417, -6.1017], [106.7633, -6.1036], [106.7678, -6.1025], [106.7847, -6.1089], [106.7897, -6.1075], [106.7903, -6.1011], [106.7942, -6.1003], [106.8005, -6.1085], [106.8033, -6.0992], [106.8118, -6.1199], [106.8206, -6.1158], [106.8222, -6.1211], [106.8503, -6.1203], [106.8631, -6.1131], [106.8688, -6.1075], [106.8725, -6.1119], [106.8787, -6.097], [106.8819, -6.0939], [106.8914, -6.0979], [106.8961, -6.0961], [106.918, -6.0989], [106.9203, -6.1014], [106.9267, -6.0972], [106.9367, -6.0964], [106.9433, -6.0981], [106.9553, -6.0964], [106.9655, -6.0914], [106.9728, -6.0911]],
}

# ── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Sekolah Internasional Jakarta",
    layout="wide",
    page_icon="🏫",
)

# ── Load Data (cached) ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Data Sekolah Internasional DKI Jakarta.xlsx")
    df["wilayah_clean"] = (
        df["wilayah"]
        .str.replace("KOTA ADM. ", "", regex=False)
        .str.title()
    )
    return df


df = load_data()

# ── Sidebar Filters ─────────────────────────────────────────────────
st.sidebar.header("🔍 Filter Data")

wilayah_options = sorted(df["wilayah_clean"].unique())
sel_wilayah = st.sidebar.multiselect(
    "Wilayah",
    options=wilayah_options,
    default=wilayah_options,
)

jenjang_options = sorted(df["jenjang"].unique())
sel_jenjang = st.sidebar.multiselect(
    "Jenjang",
    options=jenjang_options,
    default=jenjang_options,
)

min_siswa = int(df["jumlah_siswa"].min())
max_siswa = int(df["jumlah_siswa"].max())
sel_siswa = st.sidebar.slider(
    "Rentang Jumlah Siswa",
    min_value=min_siswa,
    max_value=max_siswa,
    value=(min_siswa, max_siswa),
)

mode_peta = st.sidebar.radio(
    "Mode Peta",
    ["Marker Cluster", "Heatmap", "Circle by Size", "Poverty Overlay"],
)

# ── Apply Filters ────────────────────────────────────────────────────
df_filtered = df[
    (df["wilayah_clean"].isin(sel_wilayah))
    & (df["jenjang"].isin(sel_jenjang))
    & (df["jumlah_siswa"] >= sel_siswa[0])
    & (df["jumlah_siswa"] <= sel_siswa[1])
]

# ── Header — Insight-driven Title ────────────────────────────────────
# Hitung data untuk judul dinamis
_total_sekolah = df["npsn"].nunique()
_total_siswa = int(df["jumlah_siswa"].sum())
_populasi_jkt = 10_680_000  # BPS 2024
_pct_akses = round(_total_siswa / _populasi_jkt * 100, 2)

st.markdown(
    f"""
    <h1 style='text-align:center; margin-bottom:0; line-height:1.3;'>
        🏫 {_total_sekolah} Sekolah Internasional untuk Siapa? —
        Ketika Pendidikan Premium Tumbuh Subur di Tengah Kemiskinan Jakarta
    </h1>
    <p style='text-align:center; color:gray; font-size:0.95rem; margin-top:4px;'>
        Hanya {_pct_akses}% penduduk Jakarta yang mengakses pendidikan internasional —
        <a href="https://satudata.jakarta.go.id/open-data/detail?kategori=dataset&page_url=daftar-sekolah-internasional-dengan-jumlah-peserta-didik&data_no=1"
        target="_blank" style="color:gray; text-decoration:underline;">
        Sumber: Satu Data Jakarta 2024</a>
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── KPI Cards ────────────────────────────────────────────────────────
n_sekolah = df_filtered["npsn"].nunique() if not df_filtered.empty else 0
total_siswa = int(df_filtered["jumlah_siswa"].sum()) if not df_filtered.empty else 0
rata_rata = round(df_filtered["jumlah_siswa"].mean()) if not df_filtered.empty else 0
wilayah_terpadat = (
    df_filtered.groupby("wilayah_clean")["npsn"]
    .nunique()
    .idxmax()
    .replace("Jakarta ", "Jak. ")
    if not df_filtered.empty
    else "—"
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("🏫 Total Sekolah", f"{n_sekolah}")
k2.metric("👩‍🎓 Total Siswa", f"{total_siswa:,}")
k3.metric("📊 Rata-rata Siswa/Sekolah", f"{rata_rata}")
k4.metric("📍 Wilayah Terpadat", wilayah_terpadat)

st.divider()

# ── Pydeck Map ──────────────────────────────────────────────────────
st.subheader("🗺️ Peta Sebaran Sekolah Internasional")

if not df_filtered.empty:
    df_map = df_filtered.dropna(subset=["Latitude", "Longitude"]).copy()

    if df_map.empty:
        st.warning("⚠️ Semua data hasil filter memiliki koordinat kosong (NaN). Peta tidak dapat ditampilkan.")
    else:
        # Warna per jenjang (RGBA)
        COLOR_MAP = {
            "PAUD": [46, 204, 113],
            "SD": [52, 152, 219],
            "SMP": [230, 126, 34],
            "SMA": [231, 76, 60],
        }
        df_map["color"] = df_map["jenjang"].map(
            lambda j: COLOR_MAP.get(j, [149, 165, 166])
        )
        df_map["radius"] = df_map["jumlah_siswa"].apply(
            lambda s: max(np.sqrt(s) * 25, 80)
        )
        df_map["tooltip_text"] = (
            df_map["nama_sekolah"] + " | " +
            df_map["jenjang"] + " | Siswa: " +
            df_map["jumlah_siswa"].astype(str)
        )

        view_state = pdk.ViewState(
            latitude=-6.2, longitude=106.84, zoom=10.5, pitch=0
        )

        if mode_peta == "Marker Cluster":
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["Longitude", "Latitude"],
                get_color="color",
                get_radius=200,
                radius_min_pixels=5,
                radius_max_pixels=20,
                pickable=True,
                auto_highlight=True,
            )
        elif mode_peta == "Heatmap":
            df_heat = df_map[df_map["jumlah_siswa"] > 0]
            layer = pdk.Layer(
                "HeatmapLayer",
                data=df_heat,
                get_position=["Longitude", "Latitude"],
                get_weight="jumlah_siswa",
                radius_pixels=60,
            )
        elif mode_peta == "Circle by Size":
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["Longitude", "Latitude"],
                get_color="color",
                get_radius="radius",
                radius_min_pixels=3,
                radius_max_pixels=80,
                pickable=True,
                auto_highlight=True,
                opacity=0.7,
            )

        if mode_peta == "Poverty Overlay":
            # Build polygon data with poverty-based color
            sekolah_per_wil = df_filtered.groupby("wilayah_clean")["npsn"].nunique()
            siswa_per_wil = df_filtered.groupby("wilayah_clean")["jumlah_siswa"].sum()
            poverty_max = max(POVERTY_DATA.values())
            poverty_min = min(POVERTY_DATA.values())

            poly_data = []
            for wil, coords in JAKARTA_BOUNDARIES.items():
                pov = POVERTY_DATA.get(wil, 0)
                n_sekolah_wil = int(sekolah_per_wil.get(wil, 0))
                n_siswa_wil = int(siswa_per_wil.get(wil, 0))
                # Gradient: semakin miskin semakin merah gelap
                intensity = (pov - poverty_min) / (poverty_max - poverty_min) if poverty_max > poverty_min else 0
                r = int(80 + 175 * intensity)
                g = int(180 * (1 - intensity))
                b = int(80 * (1 - intensity))
                poly_data.append({
                    "polygon": coords,
                    "name": wil,
                    "poverty_pct": pov,
                    "n_sekolah": n_sekolah_wil,
                    "n_siswa": n_siswa_wil,
                    "fill_color": [r, g, b, 140],
                })

            polygon_layer = pdk.Layer(
                "PolygonLayer",
                data=poly_data,
                get_polygon="polygon",
                get_fill_color="fill_color",
                get_line_color=[60, 60, 60, 200],
                line_width_min_pixels=2,
                pickable=True,
                auto_highlight=True,
            )
            school_layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["Longitude", "Latitude"],
                get_color="color",
                get_radius=200,
                radius_min_pixels=5,
                radius_max_pixels=20,
                pickable=True,
                auto_highlight=True,
            )

            st.pydeck_chart(
                pdk.Deck(
                    layers=[polygon_layer, school_layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{name}\nKemiskinan: {poverty_pct}%\nSekolah: {n_sekolah} | Siswa: {n_siswa}"},
                    map_provider="carto",
                    map_style="light",
                ),
                use_container_width=True,
                height=550,
            )
        else:
            st.pydeck_chart(
                pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{tooltip_text}"},
                    map_provider="carto",
                    map_style="light",
                ),
                use_container_width=True,
                height=550,
            )

        # Legend
        if mode_peta in ("Marker Cluster", "Circle by Size", "Poverty Overlay"):
            st.markdown(
                """
                <div style="display:flex; gap:16px; justify-content:center;
                            font-size:14px; margin-top:4px;">
                    <span><span style="color:#2ecc71;">&#11044;</span> PAUD</span>
                    <span><span style="color:#3498db;">&#11044;</span> SD</span>
                    <span><span style="color:#e67e22;">&#11044;</span> SMP</span>
                    <span><span style="color:#e74c3c;">&#11044;</span> SMA</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if mode_peta == "Poverty Overlay":
            st.markdown(
                """
                <div style="display:flex; gap:16px; justify-content:center; align-items:center;
                            font-size:13px; margin-top:6px; color:#555;">
                    <span>Tingkat Kemiskinan:</span>
                    <span style="background:rgba(80,180,80,0.55); padding:2px 10px; border-radius:4px;">Rendah (3%)</span>
                    <span style="background:rgba(170,100,40,0.55); padding:2px 10px; border-radius:4px;">Sedang</span>
                    <span style="background:rgba(255,0,0,0.55); padding:2px 10px; border-radius:4px;">Tinggi (13%)</span>
                    <span style="margin-left:10px; font-size:0.85em;">
                        <a href="https://databoks.katadata.co.id/demografi/statistik/a850d411822b839/ini-wilayah-jakarta-dengan-angka-kemiskinan-tertinggi-pada-maret-2023" target="_blank" style="color:#666; text-decoration:underline;">Sumber: BPS Maret 2023</a>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.warning("⚠️ Tidak ada data yang sesuai filter. Ubah filter di sidebar.")

st.divider()

# ── Charts ───────────────────────────────────────────────────────────
if not df_filtered.empty:

    # -- Chart 1 & 2 side by side --
    col_c1, col_c2 = st.columns(2)

    # Chart 1 — Stacked Bar: Jumlah sekolah per wilayah, stack by jenjang
    with col_c1:
        st.subheader("📊 Jumlah Sekolah per Wilayah & Jenjang")
        chart1_data = (
            df_filtered.groupby(["wilayah_clean", "jenjang"])["npsn"]
            .nunique()
            .reset_index(name="jumlah_sekolah")
        )
        fig1 = px.bar(
            chart1_data,
            x="wilayah_clean",
            y="jumlah_sekolah",
            color="jenjang",
            barmode="stack",
            labels={
                "wilayah_clean": "Wilayah",
                "jumlah_sekolah": "Jumlah Sekolah",
                "jenjang": "Jenjang",
            },
            color_discrete_map={
                "PAUD": "#2ecc71",
                "SD": "#3498db",
                "SMP": "#e67e22",
                "SMA": "#e74c3c",
            },
        )
        fig1.update_layout(xaxis_tickangle=-30, margin=dict(t=10, b=40))
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2 — Horizontal Bar: Total siswa per wilayah
    with col_c2:
        st.subheader("👩‍🎓 Total Siswa per Wilayah")
        chart2_data = (
            df_filtered.groupby("wilayah_clean")["jumlah_siswa"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig2 = px.bar(
            chart2_data,
            x="jumlah_siswa",
            y="wilayah_clean",
            orientation="h",
            labels={
                "wilayah_clean": "Wilayah",
                "jumlah_siswa": "Total Siswa",
            },
            color="jumlah_siswa",
            color_continuous_scale="Blues",
        )
        fig2.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=10, b=40),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3 — Histogram: Distribusi jumlah siswa
    st.subheader("🏆 Top 10 Sekolah Terbesar")
    top10 = (
        df_filtered.sort_values("jumlah_siswa", ascending=False)
        .drop_duplicates(subset="npsn")
        .head(10)
    )
    fig3 = px.bar(
        top10,
        y="nama_sekolah",
        x="jumlah_siswa",
        color="wilayah_clean",
        orientation="h",
        labels={"nama_sekolah": "", "jumlah_siswa": "Jumlah Siswa", "wilayah_clean": "Wilayah"},
        text="jumlah_siswa",
    )
    fig3.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        margin=dict(t=10, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    # Chart 4 — Bubble: Sekolah Internasional vs Kemiskinan
    st.subheader("🔴 Sekolah Internasional vs Tingkat Kemiskinan")
    bubble_data = (
        df_filtered.groupby("wilayah_clean")
        .agg(jumlah_sekolah=("npsn", "nunique"), total_siswa=("jumlah_siswa", "sum"))
        .reset_index()
    )
    bubble_data["kemiskinan_pct"] = bubble_data["wilayah_clean"].map(POVERTY_DATA)
    bubble_data = bubble_data.dropna(subset=["kemiskinan_pct"])

    if not bubble_data.empty:
        fig4 = px.scatter(
            bubble_data,
            x="kemiskinan_pct",
            y="jumlah_sekolah",
            size="total_siswa",
            text="wilayah_clean",
            labels={
                "kemiskinan_pct": "Penduduk Miskin (%)",
                "jumlah_sekolah": "Jumlah Sekolah Internasional",
                "total_siswa": "Total Siswa",
                "wilayah_clean": "Wilayah",
            },
            color="kemiskinan_pct",
            color_continuous_scale="Reds",
            size_max=50,
        )
        fig4.update_traces(textposition="top center")
        fig4.update_layout(
            coloraxis_colorbar_title="Kemiskinan (%)",
            margin=dict(t=10, b=40),
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("Sumber data kemiskinan: BPS Maret 2023 via Databoks. Bubble size = total siswa.")

st.divider()

# ── Key Insight ──────────────────────────────────────────────────────
st.subheader("💡 Key Insight")

if not df_filtered.empty:
    siswa_per_wil = df_filtered.groupby("wilayah_clean")["jumlah_siswa"].sum()
    sekolah_per_wil = df_filtered.groupby("wilayah_clean")["npsn"].nunique()
    total_s = siswa_per_wil.sum()
    populasi_jkt = 10_680_000

    wil_top = siswa_per_wil.idxmax()
    wil_top_pct = round(siswa_per_wil.max() / total_s * 100) if total_s > 0 else 0

    wil_bottom = sekolah_per_wil.idxmin()
    wil_bottom_n = sekolah_per_wil.min()
    wil_bottom_pov = POVERTY_DATA.get(wil_bottom, 0)

    rata2 = round(df_filtered["jumlah_siswa"].mean()) if not df_filtered.empty else 0
    pct_akses = round(total_s / populasi_jkt * 100, 2)

    jenjang_count = df_filtered.groupby("jenjang")["npsn"].nunique()
    jenjang_min = jenjang_count.idxmin()
    jenjang_min_n = jenjang_count.min()

    with st.container(border=True):
        st.markdown(
            f"📍 **Eksklusivitas Terkonsentrasi** — **{wil_top}** menampung "
            f"**{wil_top_pct}%** total siswa sekolah internasional. "
            f"Pendidikan premium mengikuti uang, bukan kebutuhan."
        )
        st.markdown(
            f"💰 **Paradoks {wil_bottom}** — Kemiskinan **{wil_bottom_pov}%** "
            f"tapi hanya punya **{wil_bottom_n} sekolah internasional**. "
            f"Sekolah ini bukan melayani warga sekitar, melainkan enclave "
            f"eksklusif di tengah kemiskinan."
        )
        st.markdown(
            f"📊 **Hanya {pct_akses}% Penduduk Terlayani** — Rata-rata "
            f"**{rata2} siswa/sekolah**, total hanya **{total_s:,}** dari "
            f"**{populasi_jkt:,}** penduduk Jakarta. Sekolah internasional "
            f"melayani segmen sangat terbatas."
        )
        st.markdown(
            f"🏫 **Jenjang Timpang** — **{jenjang_min}** hanya tersedia di "
            f"**{jenjang_min_n} sekolah**. Bagi keluarga tidak mampu yang "
            f"berharap trickle-down effect, jalan itu tertutup sejak awal."
        )
else:
    st.warning("Tidak ada data — ubah filter.")

# ── Recommendation ───────────────────────────────────────────────────
st.subheader("🎯 Recommendation")

if not df_filtered.empty:
    _sek_wil = df_filtered.groupby("wilayah_clean")["npsn"].nunique()
    _sis_wil = df_filtered.groupby("wilayah_clean")["jumlah_siswa"].sum()
    _wil_min = _sek_wil.idxmin()
    _wil_min_n = _sek_wil.min()
    _wil_min_pov = POVERTY_DATA.get(_wil_min, 0)
    _wil_max = _sek_wil.idxmax()
    _wil_max_n = _sek_wil.max()
    _rasio = round((_sis_wil / _sek_wil).dropna().max()) if not _sek_wil.empty else 0

    st.error(
        f"🔴 **Prioritas Tinggi: Buka Akses di {_wil_min}**\n\n"
        f"Wajibkan kuota beasiswa 10–15% di {_wil_min_n} sekolah internasional "
        f"yang beroperasi di wilayah dengan kemiskinan {_wil_min_pov}%. "
        f"Infrastruktur sudah ada — akses yang harus dibuka."
    )
    st.warning(
        f"🟡 **Prioritas Sedang: Transfer Kualitas**\n\n"
        f"Dorong program *sister-school* antara sekolah internasional "
        f"({_wil_max}: {_wil_max_n} sekolah) dan sekolah negeri sekitar. "
        f"Fokus pada jenjang yang timpang — transfer kualitas, "
        f"bukan sekadar kehadiran fisik."
    )
    st.success(
        f"🟢 **Jangka Panjang: Monitoring Kesenjangan**\n\n"
        f"Integrasikan data ini dengan demografi anak usia sekolah per kelurahan. "
        f"Saat ini rasio tertinggi mencapai **{_rasio} siswa/sekolah** — "
        f"dashboard ini harus jadi alat ukur tahunan: "
        f"apakah gap menyempit atau justru melebar?"
    )
