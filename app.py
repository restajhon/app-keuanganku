# --- MENGIMPOR LIBRARY ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Financely Dashboard", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- GAYA DESAIN CUSTOM (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .custom-card {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        height: 100%;
    }
    .card-title { font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; color: gray; }
    .card-value { font-size: 32px; font-weight: 900; margin-bottom: 5px; }
    .card-subtext { font-size: 12px; color: gray; }
    </style>
""", unsafe_allow_html=True)

def buat_kartu(icon, judul, nilai, warna_nilai, teks_bawah):
    html = f"""
    <div class="custom-card">
        <div class="card-title">{icon} {judul}</div>
        <div class="card-value" style="color: {warna_nilai};">{nilai}</div>
        <div class="card-subtext">{teks_bawah}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# BAGIAN 1: SIDEBAR (KONTROL & INPUT)
# ==========================================
with st.sidebar:
    # --- FITUR BARU: FILTER TANGGAL ---
    st.markdown("### 📅 Dashboard Controls")
    st.caption("Custom Date Range")
    
    # Set default bulan ini
    tanggal_hari_ini = datetime.today().date()
    tanggal_awal_bulan = tanggal_hari_ini.replace(day=1)
    
    start_date = st.date_input("Start Date", tanggal_awal_bulan)
    end_date = st.date_input("End Date", tanggal_hari_ini)
    
    st.divider()
    
    # --- FORM INPUT ---
    st.markdown("### 📝 Input Transaksi")
    input_tipe = st.radio("Fokus Tipe", ["Pengeluaran", "Pemasukan"], horizontal=True)
    
    with st.form("form_transaksi_baru", clear_on_submit=True):
        input_sumber = st.selectbox("Sumber Dana", ["MANDIRI", "JAGO"])
        
        if input_tipe == "Pemasukan":
            kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
        else:
            kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
            
        input_kategori = st.selectbox("Kategori", kategori_pilihan)
        input_tanggal = st.date_input("Tanggal Transaksi", datetime.today())
        input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=5000)
        input_catatan = st.text_input("Keterangan Tambahan")
        
        tombol_simpan = st.form_submit_button("Simpan Data", use_container_width=True)
        
        if tombol_simpan:
            if input_nominal > 0:
                tanggal_teks = input_tanggal.strftime("%Y-%m-%d")
                baris_baru = [tanggal_teks, input_tipe, input_sumber, input_kategori, input_nominal, input_catatan]
                worksheet.append_row(baris_baru)
                st.success("✅ Tersimpan!")
            else:
                st.error("Nominal 0")

# ==========================================
# BAGIAN 2: AREA UTAMA (DASHBOARD ANALISA)
# ==========================================

# --- FITUR BARU: BANNER GRADIENT ---
banner_html = """
<div style="background: linear-gradient(90deg, #1e3a8a 0%, #ea580c 100%); padding: 30px; border-radius: 12px; color: white; margin-bottom: 25px;">
    <h1 style="color: white; margin-top: 0; font-weight: 800; font-size: 36px;">📈 Financial Performance Overview</h1>
    <p style="margin-bottom: 0; font-size: 16px; opacity: 0.9;">Comprehensive view of personal financial metrics and cashflow behavior</p>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

data_semua = worksheet.get_all_records()

if len(data_semua) > 0:
    df = pd.DataFrame(data_semua)
    df['Nominal'] = pd.to_numeric(df['Nominal'])
    
    # Konversi format tanggal di pandas agar bisa difilter
    df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
    
    # --- PERHITUNGAN ALL TIME (TIDAK KENA FILTER) ---
    # Saldo harus dihitung dari awal mula agar akurat dengan sisa uang di bank
    saldo_total = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum() - df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
    saldo_mandiri = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum() - df[(df['Tipe'] == 'Pengeluaran') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
    saldo_jago = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum() - df[(df['Tipe'] == 'Pengeluaran') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()

    # --- MEMFILTER DATA BERDASARKAN TANGGAL PILIHAN ---
    mask = (df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)
    df_filtered = df.loc[mask]

    # --- PERHITUNGAN DATA TERFILTER ---
    total_masuk_filter = df_filtered[df_filtered['Tipe'] == 'Pemasukan']['Nominal'].sum()
    total_keluar_filter = df_filtered[df_filtered['Tipe'] == 'Pengeluaran']['Nominal'].sum()

    # --- KARTU METRIK UTAMA ---
    st.markdown("#### 💰 Transaction Volume & Value", unsafe_allow_html=True)
    kolom1, kolom2, kolom3, kolom4 = st.columns(4)
    with kolom1:
        buat_kartu("📦", "TOTAL AUM (SALDO ASLI)", f"Rp {saldo_total:,.0f}", "#0ea5e9", "Gabungan Mandiri & Jago (All Time)")
    with kolom2:
        buat_kartu("📥", "DEPOSITS (INCOME)", f"Rp {total_masuk_filter:,.0f}", "#22c55e", f"Pemasukan periode {start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}")
    with kolom3:
        buat_kartu("📤", "WITHDRAWALS (EXPENSE)", f"Rp {total_keluar_filter:,.0f}", "#ef4444", f"Pengeluaran periode {start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}")
    with kolom4:
        buat_kartu("🏛️", "ASSET ALLOCATION", f"Rp {saldo_mandiri:,.0f}", "#f59e0b", f"Mandiri. Jago: Rp {saldo_jago:,.0f}")

    st.divider()

    # --- GRAFIK & TABEL (HANYA MENAMPILKAN DATA TERFILTER) ---
    if not df_filtered.empty:
        st.markdown(f"#### 📉 Cashflow Trend ({start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')})")
        
        df_tren = df_filtered.groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
        grafik_garis = px.line(
            df_tren, x='Tanggal', y='Nominal', color='Tipe',
            color_discrete_map={"Pemasukan": "#0ea5e9", "Pengeluaran": "#ef4444"},
            markers=True
        )
        grafik_garis.update_layout(
            xaxis_title="", yaxis_title="", 
            legend_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=0, r=0, t=10, b=0), height=350
        )
        st.plotly_chart(grafik_garis, use_container_width=True)
        
        st.markdown("#### 📁 Filtered Raw Data")
        st.dataframe(df_filtered.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.warning(f"Tidak ada transaksi tercatat antara {start_date.strftime('%d %b %Y')} hingga {end_date.strftime('%d %b %Y')}.")

else:
    st.info("Database masih kosong. Sila gunakan menu di sebelah kiri untuk menginput data.")
