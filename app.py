# --- MENGIMPOR LIBRARY ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime

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
    st.markdown("### 📅 Dashboard Controls")
    tanggal_hari_ini = datetime.today().date()
    tanggal_awal_bulan = tanggal_hari_ini.replace(day=1)
    
    start_date = st.date_input("Start Date", tanggal_awal_bulan)
    end_date = st.date_input("End Date", tanggal_hari_ini)
    
    st.divider()
    
    st.markdown("### 📝 Input Transaksi")
    input_tipe = st.radio("Fokus Tipe", ["Pengeluaran", "Pemasukan"], horizontal=True)
    
    with st.form("form_transaksi_baru", clear_on_submit=True):
        input_sumber = st.selectbox("Sumber Dana", ["MANDIRI", "JAGO"])
        kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"] if input_tipe == "Pemasukan" else ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
        input_kategori = st.selectbox("Kategori", kategori_pilihan)
        input_tanggal = st.date_input("Tanggal Transaksi", datetime.today())
        input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=5000)
        input_catatan = st.text_input("Keterangan Tambahan")
        tombol_simpan = st.form_submit_button("Simpan Data", use_container_width=True)
        
        if tombol_simpan and input_nominal > 0:
            worksheet.append_row([input_tanggal.strftime("%Y-%m-%d"), input_tipe, input_sumber, input_kategori, input_nominal, input_catatan])
            st.success("✅ Tersimpan!")

# ==========================================
# BAGIAN 2: AREA UTAMA
# ==========================================
st.markdown("<div style='background: linear-gradient(90deg, #1e3a8a 0%, #ea580c 100%); padding: 30px; border-radius: 12px; color: white; margin-bottom: 25px;'><h1>📈 Financial Performance Overview</h1></div>", unsafe_allow_html=True)

data_semua = worksheet.get_all_records()
if len(data_semua) > 0:
    df = pd.DataFrame(data_semua)
    df['Nominal'] = pd.to_numeric(df['Nominal'])
    df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
    
    # Filter & Metrik
    mask = (df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)
    df_filtered = df.loc[mask]
    
    # Kartu Metrik
    c1, c2, c3 = st.columns(3)
    with c1: buat_kartu("📦", "TOTAL AUM (SALDO)", f"Rp {df[df['Tipe']=='Pemasukan']['Nominal'].sum() - df[df['Tipe']=='Pengeluaran']['Nominal'].sum():,.0f}", "#0ea5e9", "All time balance")
    with c2: buat_kartu("📥", "DEPOSITS", f"Rp {df_filtered[df_filtered['Tipe']=='Pemasukan']['Nominal'].sum():,.0f}", "#22c55e", "Income selected period")
    with c3: buat_kartu("📤", "WITHDRAWALS", f"Rp {df_filtered[df_filtered['Tipe']=='Pengeluaran']['Nominal'].sum():,.0f}", "#ef4444", "Expenses selected period")

    st.divider()

    # Grafik Garis & Pie Chart
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.markdown("#### 📉 Cashflow Trend")
        df_tren = df_filtered.groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
        fig_line = px.line(df_tren, x='Tanggal', y='Nominal', color='Tipe', color_discrete_map={"Pemasukan": "#0ea5e9", "Pengeluaran": "#ef4444"}, markers=True)
        fig_line.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_chart2:
        st.markdown("#### 🛒 Expense Allocation")
        df_pengeluaran = df_filtered[df_filtered['Tipe'] == 'Pengeluaran']
        if not df_pengeluaran.empty:
            fig_pie = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data.")

    st.markdown("#### 📁 Raw Data")
    st.dataframe(df_filtered.iloc[::-1], use_container_width=True, hide_index=True)
