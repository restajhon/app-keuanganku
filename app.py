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

# --- TARGET TABUNGAN IMPIAN (SILAKAN UBAH ANGKA DI SINI) ---
TARGET_NIKAH = 200000000
TARGET_RUMAH = 1500000000
TARGET_MOBIL = 300000000

# --- GAYA DESAIN CUSTOM (CSS) ---
st.markdown("""
    <style>
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
# BAGIAN 1: SIDEBAR (MENU NAVIGASI & FILTER)
# ==========================================
with st.sidebar:
    st.markdown("### 🧭 Main Menu")
    # Fitur Baru: Bar Menu Navigasi
    menu_pilihan = st.radio("Pergi ke halaman:", 
        ["Dashboard", "Input Data", "Spending", "Tabungan", "Wallet"], 
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Fitur Baru: Filter Waktu Cepat (Quick Filters)
    st.markdown("### 📅 Time Filter")
    filter_waktu = st.selectbox("Pilih Periode Analisa:", 
        ["Bulan Ini", "Minggu Ini", "3 Bulan Terakhir", "6 Bulan Terakhir", "Tahun Ini", "Semua Waktu"]
    )
    
    # Logika Filter Waktu
    hari_ini = datetime.today().date()
    if filter_waktu == "Minggu Ini":
        start_date = hari_ini - timedelta(days=hari_ini.weekday())
    elif filter_waktu == "Bulan Ini":
        start_date = hari_ini.replace(day=1)
    elif filter_waktu == "3 Bulan Terakhir":
        start_date = hari_ini - timedelta(days=90)
    elif filter_waktu == "6 Bulan Terakhir":
        start_date = hari_ini - timedelta(days=180)
    elif filter_waktu == "Tahun Ini":
        start_date = hari_ini.replace(month=1, day=1)
    else: # Semua Waktu
        start_date = hari_ini - timedelta(days=3650) # Tarik mundur 10 tahun
        
    end_date = hari_ini

# ==========================================
# PROSES DATA DARI GOOGLE SHEETS
# ==========================================
data_semua = worksheet.get_all_records()
df = pd.DataFrame(data_semua) if len(data_semua) > 0 else pd.DataFrame()

if not df.empty:
    df['Nominal'] = pd.to_numeric(df['Nominal'])
    df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
    
    # Data Terfilter sesuai pilihan di sidebar
    mask = (df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)
    df_filter = df.loc[mask]

# ==========================================
# HALAMAN 1: DASHBOARD (OVERVIEW)
# ==========================================
if menu_pilihan == "Dashboard":
    st.markdown("<div style='background: linear-gradient(90deg, #1e3a8a 0%, #ea580c 100%); padding: 30px; border-radius: 12px; color: white; margin-bottom: 25px;'><h1>✨ Financely Executive Dashboard</h1></div>", unsafe_allow_html=True)
    
    if not df.empty:
        # Perhitungan All Time untuk AUM
        total_pemasukan_all = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_pengeluaran_all = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        total_tabungan_all = df[df['Tipe'] == 'Tabungan']['Nominal'].sum()
        
        # Saldo Aktif (Uang yang siap dipakai, dipotong uang yang sudah ditabung)
        saldo_aktif = total_pemasukan_all - total_pengeluaran_all - total_tabungan_all
        
        # Perhitungan Periode Terfilter
        masuk_filter = df_filter[df_filter['Tipe'] == 'Pemasukan']['Nominal'].sum()
        keluar_filter = df_filter[df_filter['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: buat_kartu("💳", "ACTIVE BALANCE", f"Rp {saldo_aktif:,.0f}", "#0ea5e9", "Sisa kas siap pakai")
        with c2: buat_kartu("💰", "TOTAL SAVINGS", f"Rp {total_tabungan_all:,.0f}", "#8b5cf6", "Total aset tabungan impian")
        with c3: buat_kartu("📥", f"INCOME ({filter_waktu})", f"Rp {masuk_filter:,.0f}", "#22c55e", "Pemasukan periode terpilih")
        with c4: buat_kartu("📤", f"SPENDING ({filter_waktu})", f"Rp {keluar_filter:,.0f}", "#ef4444", "Pengeluaran periode terpilih")
        
        st.divider()
        st.markdown(f"#### 📈 Tren Keuangan ({filter_waktu})")
        df_tren = df_filter.groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
        fig_line = px.line(df_tren, x='Tanggal', y='Nominal', color='Tipe', color_discrete_map={"Pemasukan": "#22c55e", "Pengeluaran": "#ef4444", "Tabungan": "#8b5cf6"}, markers=True)
        fig_line.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Belum ada data. Silakan ke menu 'Input Data'.")

# ==========================================
# HALAMAN 2: INPUT DATA
# ==========================================
elif menu_pilihan == "Input Data":
    st.markdown("<h2>📝 Form Input Transaksi</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        # Sekarang Tipe ada 3!
        input_tipe = st.radio("Jenis Transaksi", ["Pengeluaran", "Pemasukan", "Tabungan"], horizontal=True)
        st.divider()
        
        with st.form("form_input", clear_on_submit=True):
            input_sumber = st.selectbox("Sumber Dana", ["MANDIRI", "JAGO"])
            
            # Kategori otomatis berubah sesuai tipe
            if input_tipe == "Pemasukan":
                kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
            elif input_tipe == "Tabungan":
                kategori_pilihan = ["Biaya Nikah", "Beli Rumah", "Mobil"]
            else:
                kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
                
            input_kategori = st.selectbox("Kategori", kategori_pilihan)
            input_tanggal = st.date_input("Tanggal", datetime.today())
            input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=10000)
            input_catatan = st.text_input("Catatan")
            
            tombol_simpan = st.form_submit_button("Simpan ke Database")
            
            if tombol_simpan and input_nominal > 0:
                worksheet.append_row([input_tanggal.strftime("%Y-%m-%d"), input_tipe, input_sumber, input_kategori, input_nominal, input_catatan])
                st.success("✅ Data berhasil disimpan!")
                st.balloons()

# ==========================================
# HALAMAN 3: SPENDING (ANALISIS PENGELUARAN)
# ==========================================
elif menu_pilihan == "Spending":
    st.markdown("<h2>🛒 Spending Analysis</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        df_pengeluaran = df_filter[df_filter['Tipe'] == 'Pengeluaran']
        if not df_pengeluaran.empty:
            total_spend = df_pengeluaran['Nominal'].sum()
            st.markdown(f"**Total Pengeluaran ({filter_waktu}): Rp {total_spend:,.0f}**")
            
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.5)
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                ringkasan = df_pengeluaran.groupby('Kategori')['Nominal'].sum().reset_index()
                fig_bar = px.bar(ringkasan, x='Kategori', y='Nominal', text_auto='.2s')
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info(f"Tidak ada pengeluaran di periode {filter_waktu}.")
    else:
        st.info("Belum ada data.")

# ==========================================
# HALAMAN 4: TABUNGAN (SAVINGS TRACKER)
# ==========================================
elif menu_pilihan == "Tabungan":
    st.markdown("<h2>🎯 Savings & Goals Tracker</h2>", unsafe_allow_html=True)
    st.write("Pantau terus progres tabungan impian Anda!")
    
    if not df.empty:
        df_tabungan = df[df['Tipe'] == 'Tabungan'] # Tabungan selalu dihitung All Time
        
        # Perhitungan per kategori
        terkumpul_nikah = df_tabungan[df_tabungan['Kategori'] == 'Biaya Nikah']['Nominal'].sum()
        terkumpul_rumah = df_tabungan[df_tabungan['Kategori'] == 'Beli Rumah']['Nominal'].sum()
        terkumpul_mobil = df_tabungan[df_tabungan['Kategori'] == 'Mobil']['Nominal'].sum()
        
        # Fungsi untuk menghitung persentase dan mencegah error lebih dari 100%
        def hitung_persen(terkumpul, target):
            persen = (terkumpul / target) if target > 0 else 0
            return min(persen, 1.0) # Maksimal 100% (1.0) untuk progress bar
            
        st.divider()
        
        # 1. Goal: BIAYA NIKAH
        st.subheader("💍 Biaya Nikah")
        st.write(f"**Terkumpul: Rp {terkumpul_nikah:,.0f}** / Target: Rp {TARGET_NIKAH:,.0f}")
        st.progress(hitung_persen(terkumpul_nikah, TARGET_NIKAH))
        
        st.write("") # Jarak
        
        # 2. Goal: BELI RUMAH
        st.subheader("🏠 Beli Rumah")
        st.write(f"**Terkumpul: Rp {terkumpul_rumah:,.0f}** / Target: Rp {TARGET_RUMAH:,.0f}")
        st.progress(hitung_persen(terkumpul_rumah, TARGET_RUMAH))
        
        st.write("")
        
        # 3. Goal: MOBIL
        st.subheader("🚗 Kendaraan (Mobil)")
        st.write(f"**Terkumpul: Rp {terkumpul_mobil:,.0f}** / Target: Rp {TARGET_MOBIL:,.0f}")
        st.progress(hitung_persen(terkumpul_mobil, TARGET_MOBIL))
        
    else:
        st.info("Belum ada tabungan yang tercatat.")

# ==========================================
# HALAMAN 5: WALLET (KONDISI REKENING)
# ==========================================
elif menu_pilihan == "Wallet":
    st.markdown("<h2>🏛️ Wallet & Accounts</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        # Pemasukan = Plus, Pengeluaran & Tabungan = Minus (karena tabungan dipindah dari dompet utama)
        masuk_mandiri = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        keluar_mandiri = df[(df['Tipe'] != 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        sisa_mandiri = masuk_mandiri - keluar_mandiri
        
        masuk_jago = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        keluar_jago = df[(df['Tipe'] != 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        sisa_jago = masuk_jago - keluar_jago
        
        c1, c2 = st.columns(2)
        with c1:
            buat_kartu("🏦", "BANK MANDIRI", f"Rp {sisa_mandiri:,.0f}", "#0ea5e9", "Akun Utama")
        with c2:
            buat_kartu("🟡", "BANK JAGO", f"Rp {sisa_jago:,.0f}", "#f59e0b", "Akun Operasional")
            
        st.divider()
        st.markdown("#### 📋 History Transaksi")
        st.dataframe(df_filter.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data.")
