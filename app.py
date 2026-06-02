# --- MENGIMPOR LIBRARY ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Financely Dashboard", page_icon="✨", layout="wide")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- GAYA DESAIN CUSTOM (CSS) ADAPTIF ---
# Warna paksaan dihapus agar font otomatis putih di mode gelap dan hitam di mode terang
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 14px; font-weight: 500; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: 600; padding: 12px 24px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER UTAMA APLIKASI ---
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>✨ Financely Workspace</h1>", unsafe_allow_html=True)

# --- PEMBAGIAN TAB UTAMA ---
tab_dashboard, tab_input = st.tabs(["📊 Dashboard Analisa", "📝 Catat Transaksi"])

# ==========================================
# BAGIAN 1: TAB DASHBOARD ANALISA
# ==========================================
with tab_dashboard:
    data_semua = worksheet.get_all_records()
    
    if len(data_semua) > 0:
        df = pd.DataFrame(data_semua)
        df['Nominal'] = pd.to_numeric(df['Nominal'])
        
        # --- PERHITUNGAN SALDO ---
        total_masuk = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_keluar = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        saldo_total = total_masuk - total_keluar
        
        masuk_mandiri = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        keluar_mandiri = df[(df['Tipe'] == 'Pengeluaran') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        saldo_mandiri = masuk_mandiri - keluar_mandiri
        
        masuk_jago = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        keluar_jago = df[(df['Tipe'] == 'Pengeluaran') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        saldo_jago = masuk_jago - keluar_jago

        # --- KARTU METRIK UTAMA ---
        k1, k2, k3 = st.columns(3)
        with k1:
            with st.container(border=True):
                st.metric(label="💰 TOTAL SALDO GABUNGAN", value=f"Rp {saldo_total:,.0f}")
        with k2:
            with st.container(border=True):
                st.metric(label="📥 TOTAL PEMASUKAN", value=f"Rp {total_masuk:,.0f}")
        with k3:
            with st.container(border=True):
                st.metric(label="📤 TOTAL PENGELUARAN", value=f"Rp {total_keluar:,.0f}")
                
        # --- SALDO PER REKENING ---
        st.write("") # Memberi sedikit jarak
        st.subheader("💳 Kondisi Kas per Rekening", divider="gray")
        
        g1, g2 = st.columns(2)
        with g1:
            with st.container(border=True):
                st.metric(label="Bank Mandiri", value=f"Rp {saldo_mandiri:,.0f}", delta="Akun Utama")
        with g2:
            with st.container(border=True):
                st.metric(label="Kantong Bank Jago", value=f"Rp {saldo_jago:,.0f}", delta="Akun Operasional")
                
        st.write("")
        
        # --- BAGIAN GRAFIK ESTETIK ---
        kolom_grafik1, kolom_grafik2 = st.columns(2)
        warna_premium = ["#818cf8", "#34d399", "#2dd4bf", "#fb7185", "#fbbf24", "#a78bfa"] # Warna pastel yang lebih terang untuk mode gelap
        
        with kolom_grafik1:
            df_pengeluaran = df[df['Tipe'] == 'Pengeluaran']
            if not df_pengeluaran.empty:
                grafik_donut = px.pie(
                    df_pengeluaran, values='Nominal', names='Kategori', 
                    title="🛒 Alokasi Dana Pengeluaran",
                    hole=0.4, color_discrete_sequence=warna_premium
                )
                grafik_donut.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(grafik_donut, use_container_width=True)
            else:
                st.info("Belum ada data pengeluaran untuk dianalisa.")
                
        with kolom_grafik2:
            if not df_pengeluaran.empty:
                ringkasan_sumber = df_pengeluaran.groupby('Sumber')['Nominal'].sum().reset_index()
                grafik_bar = px.bar(
                    ringkasan_sumber, x='Sumber', y='Nominal', 
                    title="📈 Pengeluaran Berdasarkan Rekening",
                    color='Sumber', color_discrete_map={"MANDIRI": "#818cf8", "JAGO": "#2dd4bf"},
                    text_auto='.2s'
                )
                st.plotly_chart(grafik_bar, use_container_width=True)
                
        # --- TABEL RIWAYAT TRANSAKSI ---
        st.write("")
        st.subheader("📋 Jurnal Transaksi Terbaru", divider="gray")
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
    else:
        st.info("Database masih kosong. Sila buka tab 'Catat Transaksi' untuk memulai mengisi keuangan Anda!")

# ==========================================
# BAGIAN 2: TAB INPUT TRANSAKSI
# ==========================================
with tab_input:
    st.markdown("<h3 style='text-align: center;'>📝 Form Pencatatan</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        input_tipe = st.radio("Pilih Jenis Transaksi", ["Pengeluaran", "Pemasukan"], horizontal=True)
        st.divider()
        
        with st.form("form_transaksi_baru", clear_on_submit=True):
            input_sumber = st.selectbox("Pilih Rekening / Sumber Dana", ["MANDIRI", "JAGO"])
            
            if input_tipe == "Pemasukan":
                kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
            else:
                kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
                
            input_kategori = st.selectbox("Pilih Kategori", kategori_pilihan)
            input_tanggal = st.date_input("Tanggal Transaksi", datetime.today())
            input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=5000)
            input_catatan = st.text_input("Keterangan / Catatan Tambahan")
            
            tombol_simpan = st.form_submit_button("🔥 Simpan Transaksi Ke Sistem")
            
            if tombol_simpan:
                if input_nominal > 0:
                    tanggal_teks = input_tanggal.strftime("%Y-%m-%d")
                    baris_baru = [tanggal_teks, input_tipe, input_sumber, input_kategori, input_nominal, input_catatan]
                    worksheet.append_row(baris_baru)
                    st.success(f"Berhasil mencatat {input_tipe} sebesar Rp {input_nominal:,.0f} via {input_sumber}!")
                    st.balloons()
                else:
                    st.warning("Mohon isi nominal uang terlebih dahulu sebelum menyimpan.")
