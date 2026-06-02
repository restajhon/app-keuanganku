# --- MENGIMPOR LIBRARY ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Financely Dashboard", page_icon="✨", layout="wide")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- GAYA DESAIN CUSTOM (CSS) MENIRU REFERENSI ---
st.markdown("""
    <style>
    /* Desain Kartu ala referensi UI */
    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 14px; font-weight: 600; opacity: 0.7; }
    
    /* Mempercantik font judul */
    h1, h2, h3 { font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER APLIKASI (Meniru "Good morning, Jaylon") ---
st.markdown("<h1 style='margin-bottom: 0px;'>Hi, Resta ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: gray; margin-bottom: 30px;'>This is your finance report</p>", unsafe_allow_html=True)

# --- PEMBAGIAN TAB UTAMA ---
tab_dashboard, tab_input = st.tabs(["Overview", "Transaction Input"])

# ==========================================
# BAGIAN 1: TAB DASHBOARD ANALISA
# ==========================================
with tab_dashboard:
    data_semua = worksheet.get_all_records()
    
    if len(data_semua) > 0:
        df = pd.DataFrame(data_semua)
        df['Nominal'] = pd.to_numeric(df['Nominal'])
        df['Tanggal'] = pd.to_datetime(df['Tanggal']) # Format tanggal untuk grafik garis
        
        # --- PERHITUNGAN SALDO ---
        total_masuk = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_keluar = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        saldo_total = total_masuk - total_keluar

        # --- PEMBAGIAN LAYOUT (KIRI 70%, KANAN 30%) ---
        # Meniru referensi di mana bagian kanan khusus untuk detail pengeluaran
        kolom_kiri, kolom_kanan = st.columns([7, 3])
        
        with kolom_kiri:
            # --- KARTU METRIK ATAS ---
            k1, k2, k3 = st.columns([2, 1.5, 1.5])
            with k1:
                st.metric(label="My balance", value=f"Rp {saldo_total:,.0f}")
            with k2:
                st.metric(label="Total income", value=f"Rp {total_masuk:,.0f}")
            with k3:
                st.metric(label="Total expenses", value=f"Rp {total_keluar:,.0f}")
            
            st.write("") # Jarak
            st.write("")
            
            # --- GRAFIK GARIS (STATISTICS) ---
            st.subheader("Statistics")
            # Mengelompokkan data per tanggal untuk melihat tren naik turun
            df_tren = df.groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
            
            # Membuat Line Chart yang mulus (spline) meniru referensi
            grafik_garis = px.line(
                df_tren, x='Tanggal', y='Nominal', color='Tipe',
                color_discrete_map={"Pemasukan": "#16a34a", "Pengeluaran": "#ea580c"}, # Warna Hijau & Oranye sesuai gambar
                markers=True
            )
            grafik_garis.update_traces(line_shape='spline', line=dict(width=3), marker=dict(size=8))
            grafik_garis.update_layout(
                xaxis_title="", yaxis_title="", 
                legend_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(grafik_garis, use_container_width=True)

        with kolom_kanan:
            # --- GRAFIK DONUT (ALL EXPENSES) ---
            st.subheader("All expenses")
            df_pengeluaran = df[df['Tipe'] == 'Pengeluaran']
            
            if not df_pengeluaran.empty:
                # Menghitung persentase untuk ditampilkan di keterangan
                ringkasan_kategori = df_pengeluaran.groupby('Kategori')['Nominal'].sum().reset_index()
                
                # Palet warna terang meniru referensi
                warna_donut = ["#0ea5e9", "#ef4444", "#eab308", "#22c55e", "#8b5cf6"]
                
                grafik_donut = px.pie(
                    ringkasan_kategori, values='Nominal', names='Kategori', 
                    hole=0.6, color_discrete_sequence=warna_donut
                )
                grafik_donut.update_traces(textposition='inside', textinfo='percent')
                grafik_donut.update_layout(
                    legend=dict(orientation="v", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                    margin=dict(l=0, r=0, t=20, b=0)
                )
                st.plotly_chart(grafik_donut, use_container_width=True)
            else:
                st.info("No expenses yet.")

        # --- TABEL RIWAYAT TRANSAKSI (BAGIAN BAWAH) ---
        st.write("")
        st.subheader("Transaction and invoices")
        st.caption("Stay update on recent financial activities")
        # Mengembalikan format tanggal ke teks agar rapi di tabel
        df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d')
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
        
    else:
        st.info("Database masih kosong. Silakan buka tab 'Transaction Input' untuk memulai!")

# ==========================================
# BAGIAN 2: TAB INPUT TRANSAKSI (Disembunyikan di tab kedua agar dashboard utama bersih)
# ==========================================
with tab_input:
    st.markdown("<h3>Catat Transaksi Baru</h3>", unsafe_allow_html=True)
    
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
            
            tombol_simpan = st.form_submit_button("Simpan Transaksi")
            
            if tombol_simpan:
                if input_nominal > 0:
                    tanggal_teks = input_tanggal.strftime("%Y-%m-%d")
                    baris_baru = [tanggal_teks, input_tipe, input_sumber, input_kategori, input_nominal, input_catatan]
                    worksheet.append_row(baris_baru)
                    st.success(f"Berhasil mencatat {input_tipe} sebesar Rp {input_nominal:,.0f}!")
                    st.balloons()
                else:
                    st.warning("Mohon isi nominal uang terlebih dahulu.")
