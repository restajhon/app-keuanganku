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

# --- TARGET TABUNGAN IMPIAN ---
TARGET_NIKAH = 50000000
TARGET_RUMAH = 150000000
TARGET_MOBIL = 80000000

# --- GAYA DESAIN CUSTOM (CSS) ---
st.markdown("""
    <style>
    .custom-card {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        height: 100%;
    }
    .card-title { font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; color: gray; }
    .card-value { font-size: 32px; font-weight: 900; margin-bottom: 5px; }
    .card-subtext { font-size: 12px; color: gray; }
    h1, h2, h3 { font-weight: 700 !important; }
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
    menu_pilihan = st.radio("Pergi ke halaman:", 
        ["Dashboard", "Input Data", "Spending", "Tabungan", "Wallet"], 
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("### 📅 Time Filter")
    filter_waktu = st.selectbox("Pilih Periode Analisa:", 
        ["Bulan Ini", "Minggu Ini", "3 Bulan Terakhir", "6 Bulan Terakhir", "Tahun Ini", "Semua Waktu"]
    )
    
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
    else: 
        start_date = hari_ini - timedelta(days=3650) 
        
    end_date = hari_ini

# ==========================================
# PROSES DATA DARI GOOGLE SHEETS
# ==========================================
data_semua = worksheet.get_all_records()
df = pd.DataFrame(data_semua) if len(data_semua) > 0 else pd.DataFrame()

if not df.empty:
    df['Nominal'] = pd.to_numeric(df['Nominal'])
    df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
    
    mask = (df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)
    df_filter = df.loc[mask]

# ==========================================
# HALAMAN 1: DASHBOARD (OVERVIEW)
# ==========================================
if menu_pilihan == "Dashboard":
    # Header yang meniru desain gambar referensi (Clean & Personal)
    st.markdown("<h1 style='margin-bottom: 0px;'>Good morning, Difa ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; margin-bottom: 30px;'>This is your finance report</p>", unsafe_allow_html=True)
    
    if not df.empty:
        total_pemasukan_all = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_pengeluaran_all = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        total_tabungan_all = df[df['Tipe'] == 'Tabungan']['Nominal'].sum()
        saldo_aktif = total_pemasukan_all - total_pengeluaran_all - total_tabungan_all
        
        masuk_filter = df_filter[df_filter['Tipe'] == 'Pemasukan']['Nominal'].sum()
        keluar_filter = df_filter[df_filter['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        
        # PEMBAGIAN LAYOUT ALA REFERENSI (Kiri 70%, Kanan 30%)
        kolom_kiri, kolom_kanan = st.columns([7, 3])
        
        with kolom_kiri:
            # 3 Kartu Metrik Utama
            k1, k2, k3 = st.columns([2, 1.5, 1.5])
            with k1: buat_kartu("💳", "MY BALANCE", f"Rp {saldo_aktif:,.0f}", "#0ea5e9", "Sisa kas siap pakai")
            with k2: buat_kartu("📥", "INCOME", f"Rp {masuk_filter:,.0f}", "#22c55e", f"{filter_waktu}")
            with k3: buat_kartu("📤", "EXPENSES", f"Rp {keluar_filter:,.0f}", "#ef4444", f"{filter_waktu}")
            
            st.write("")
            st.subheader("Statistics")
            
            # Grafik Garis (Trend)
            df_tren = df_filter.groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
            # Hanya menampilkan pemasukan dan pengeluaran di grafik trend agar rapi
            df_tren = df_tren[df_tren['Tipe'].isin(['Pemasukan', 'Pengeluaran'])]
            
            fig_line = px.line(df_tren, x='Tanggal', y='Nominal', color='Tipe', 
                               color_discrete_map={"Pemasukan": "#22c55e", "Pengeluaran": "#ef4444"}, markers=True)
            fig_line.update_traces(line_shape='spline', line=dict(width=3)) # Efek garis melengkung
            fig_line.update_layout(xaxis_title="", yaxis_title="", height=320,
                                   legend_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                                   margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_line, use_container_width=True)

        with kolom_kanan:
            # Kartu Tabungan diselipkan di kanan atas
            buat_kartu("💰", "TOTAL SAVINGS", f"Rp {total_tabungan_all:,.0f}", "#8b5cf6", "Total aset tabungan")
            
            st.write("")
            st.subheader("All expenses")
            
            # Donut Chart
            df_pengeluaran = df_filter[df_filter['Tipe'] == 'Pengeluaran']
            if not df_pengeluaran.empty:
                fig_pie = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.6, 
                                 color_discrete_sequence=["#0ea5e9", "#ef4444", "#eab308", "#22c55e", "#8b5cf6"])
                fig_pie.update_traces(textposition='inside', textinfo='percent')
                fig_pie.update_layout(legend=dict(orientation="v", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                                      margin=dict(l=0, r=0, t=20, b=0), height=300)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expenses in this period.")

        # Tabel Riwayat Transaksi (Lebar Penuh di Bawah)
        st.write("")
        st.subheader("Transaction and invoices")
        st.caption("Stay update on recent financial activities")
        st.dataframe(df_filter.iloc[::-1], use_container_width=True, hide_index=True)
        
    else:
        st.info("Belum ada data. Silakan ke menu 'Input Data'.")

# ==========================================
# HALAMAN 2: INPUT DATA
# ==========================================
elif menu_pilihan == "Input Data":
    st.markdown("<h2>📝 Form Input Transaksi</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        input_tipe = st.radio("Jenis Transaksi", ["Pengeluaran", "Pemasukan", "Tabungan"], horizontal=True)
        st.divider()
        with st.form("form_input", clear_on_submit=True):
            input_sumber = st.selectbox("Sumber Dana", ["MANDIRI", "JAGO"])
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
# HALAMAN 3: SPENDING
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
# HALAMAN 4: TABUNGAN
# ==========================================
elif menu_pilihan == "Tabungan":
    st.markdown("<h2>🎯 Savings & Goals Tracker</h2>", unsafe_allow_html=True)
    if not df.empty:
        df_tabungan = df[df['Tipe'] == 'Tabungan'] 
        terkumpul_nikah = df_tabungan[df_tabungan['Kategori'] == 'Biaya Nikah']['Nominal'].sum()
        terkumpul_rumah = df_tabungan[df_tabungan['Kategori'] == 'Beli Rumah']['Nominal'].sum()
        terkumpul_mobil = df_tabungan[df_tabungan['Kategori'] == 'Mobil']['Nominal'].sum()
        
        def hitung_persen(terkumpul, target):
            return min((terkumpul / target) if target > 0 else 0, 1.0)
            
        st.divider()
        st.subheader("💍 Biaya Nikah")
        st.write(f"**Terkumpul: Rp {terkumpul_nikah:,.0f}** / Target: Rp {TARGET_NIKAH:,.0f}")
        st.progress(hitung_persen(terkumpul_nikah, TARGET_NIKAH))
        st.write("") 
        
        st.subheader("🏠 Beli Rumah")
        st.write(f"**Terkumpul: Rp {terkumpul_rumah:,.0f}** / Target: Rp {TARGET_RUMAH:,.0f}")
        st.progress(hitung_persen(terkumpul_rumah, TARGET_RUMAH))
        st.write("")
        
        st.subheader("🚗 Kendaraan (Mobil)")
        st.write(f"**Terkumpul: Rp {terkumpul_mobil:,.0f}** / Target: Rp {TARGET_MOBIL:,.0f}")
        st.progress(hitung_persen(terkumpul_mobil, TARGET_MOBIL))
    else:
        st.info("Belum ada tabungan yang tercatat.")

# ==========================================
# HALAMAN 5: WALLET
# ==========================================
elif menu_pilihan == "Wallet":
    st.markdown("<h2>🏛️ Wallet & Accounts</h2>", unsafe_allow_html=True)
    if not df.empty:
        masuk_mandiri = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        keluar_mandiri = df[(df['Tipe'] != 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        sisa_mandiri = masuk_mandiri - keluar_mandiri
        
        masuk_jago = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        keluar_jago = df[(df['Tipe'] != 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        sisa_jago = masuk_jago - keluar_jago
        
        c1, c2 = st.columns(2)
        with c1: buat_kartu("🏦", "BANK MANDIRI", f"Rp {sisa_mandiri:,.0f}", "#0ea5e9", "Akun Utama")
        with c2: buat_kartu("🟡", "BANK JAGO", f"Rp {sisa_jago:,.0f}", "#f59e0b", "Akun Operasional")
            
        st.divider()
        st.markdown("#### 📋 History Transaksi")
        st.dataframe(df_filter.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data.")
