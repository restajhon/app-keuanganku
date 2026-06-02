# --- MENGIMPOR LIBRARY ---
import streamlit as st # Library utama UI web
import gspread # Library integrasi Google Sheets
import pandas as pd # Library pengolahan data tabel
import plotly.express as px # Library grafik interaktif premium
import plotly.graph_objects as go # Library untuk kustomisasi grafik tingkat lanjut
from datetime import datetime # Library waktu otomatis

# --- PENGATURAN HALAMAN WEB (TEMA PREMIUM) ---
st.set_page_config(page_title="Financely Dashboard", page_icon="✨", layout="wide")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- GAYA DESAIN CUSTOM (CSS) UNTUK TAMPILAN ESTETIK ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #1e293b; }
    div[data-testid="stMetricLabel"] { font-size: 14px; font-weight: 500; color: #64748b; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: 600; padding: 12px 24px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER UTAMA APLIKASI ---
# Membuat tampilan judul yang clean dan mewah tanpa elemen bawaan yang kaku
st.markdown("<h1 style='text-align: center; color: #0f172a; margin-bottom: 30px;'>✨ Financely Workspace</h1>", unsafe_allow_html=True)

# --- PEMBAGIAN TAB UTAMA ---
tab_dashboard, tab_input = st.tabs(["📊 Dashboard Analisa", "📝 Catat Transaksi"])

# ==========================================
# BAGIAN 1: TAB DASHBOARD ANALISA (HALAMAN UTAMA LAPTOP)
# ==========================================
with tab_dashboard:
    # Mengambil seluruh data terkini dari Google Sheets
    data_semua = worksheet.get_all_records()
    
    if len(data_semua) > 0:
        # Mengubah data menjadi bentuk tabel Pandas DataFrame
        df = pd.DataFrame(data_semua)
        df['Nominal'] = pd.to_numeric(df['Nominal'])
        
        # --- PROSES PERHITUNGAN SALDO & AKUN ---
        # Menghitung total uang masuk dan keluar
        total_masuk = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_keluar = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        saldo_total = total_masuk - total_keluar
        
        # Menghitung sisa saldo spesifik di masing-masing Dompet/Rekening
        masuk_mandiri = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        keluar_mandiri = df[(df['Tipe'] == 'Pengeluaran') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        saldo_mandiri = masuk_mandiri - keluar_mandiri
        
        masuk_jago = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        keluar_jago = df[(df['Tipe'] == 'Pengeluaran') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        saldo_jago = masuk_jago - keluar_jago

        # --- TAMPILAN KARTU METRIK UTAMA (3 KOLOM) ---
        # Menggunakan wadah berbingkai (border=True) agar terlihat seperti kartu eksekutif terpisah
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
                
        # --- TAMPILAN SALDO PER REKENING ---
        st.markdown("<h4 style='color: #334155; margin-top: 20px;'>💳 Kondisi Kas per Rekening</h4>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            with st.container(border=True):
                st.metric(label="Bank Mandiri", value=f"Rp {saldo_mandiri:,.0f}", delta="Akun Utama")
        with g2:
            with st.container(border=True):
                st.metric(label="Kantong Bank Jago", value=f"Rp {saldo_jago:,.0f}", delta="Akun Operasional")
                
        st.divider()
        
        # --- BAGIAN GRAFIK ESTETIK (2 KOLOM) ---
        kolom_grafik1, kolom_grafik2 = st.columns(2)
        
        # Palet warna estetik (Kombinasi Indigo, Emerald, Teal, Rose, Amber, Purple)
        warna_premium = ["#6366f1", "#10b981", "#06b6d4", "#f43f5e", "#f59e0b", "#8b5cf6"]
        
        with kolom_grafik1:
            # Grafik 1: Proporsi Pengeluaran Berdasarkan Kategori
            df_pengeluaran = df[df['Tipe'] == 'Pengeluaran']
            if not df_pengeluaran.empty:
                # Membuat grafiknya berlubang di tengah (Donut Chart) agar lebih modern
                grafik_donut = px.pie(
                    df_pengeluaran, values='Nominal', names='Kategori', 
                    title="🛒 Alokasi Dana Pengeluaran",
                    hole=0.4, color_discrete_sequence=warna_premium
                )
                # Mempercantik posisi teks di dalam grafik donut
                grafik_donut.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(grafik_donut, use_container_width=True)
            else:
                st.info("Belum ada data pengeluaran untuk dianalisa.")
                
        with kolom_grafik2:
            # Grafik 2: Perbandingan Penggunaan Rekening (Mandiri vs Jago) untuk Pengeluaran
            if not df_pengeluaran.empty:
                ringkasan_sumber = df_pengeluaran.groupby('Sumber')['Nominal'].sum().reset_index()
                grafik_bar = px.bar(
                    ringkasan_sumber, x='Sumber', y='Nominal', 
                    title="📈 Pengeluaran Berdasarkan Rekening",
                    color='Sumber', color_discrete_map={"MANDIRI": "#6366f1", "JAGO": "#06b6d4"},
                    text_auto='.2s'
                )
                st.plotly_chart(grafik_bar, use_container_width=True)
                
        # --- TABEL RIWAYAT TRANSAKSI TERAKHIR ---
        st.markdown("<h4 style='color: #334155; margin-top: 20px;'>📋 Jurnal Transaksi Terbaru</h4>", unsafe_allow_html=True)
        # Menampilkan tabel data yang bisa diurutkan secara interaktif oleh user
        st.dataframe(df.iloc[::-1], use_container_width=True) # iloc[::-1] digunakan untuk membalik urutan agar data terbaru berada di paling atas
        
    else:
        st.info("Database masih kosong. Sila buka tab 'Catat Transaksi' untuk memulai mengisi keuangan Anda!")

# ==========================================
# BAGIAN 2: TAB INPUT TRANSAKSI (OPTIMAL UNTUK TAMPILAN HP)
# ==========================================
with tab_input:
    st.markdown("<h3 style='text-align: center; color: #1e293b;'>📝 Form Pencatatan</h3>", unsafe_allow_html=True)
    
    # Form dibungkus dalam container agar memiliki border tipis yang rapi di layar HP
    with st.container(border=True):
        with st.form("form_transaksi_baru", clear_on_submit=True):
            
            # 1. Pilihan Tipe Utama (Pemasukan atau Pengeluaran)
            input_tipe = st.radio("Pilih Jenis Transaksi", ["Pengeluaran", "Pemasukan"], horizontal=True)
            
            st.divider()
            
            # 2. Pilihan Sumber Dana (Sesuai Permintaan Anda)
            input_sumber = st.selectbox("Pilih Rekening / Sumber Dana", ["MANDIRI", "JAGO"])
            
            # 3. Logika Kategori Dinamis: Pilihan kategori akan otomatis berubah mengikuti tipe yang dipilih di atas
            if input_tipe == "Pemasukan":
                kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
            else:
                kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
                
            input_kategori = st.selectbox("Pilih Kategori", kategori_pilihan)
            
            # 4. Input Detail Lainnya (Tanggal, Nominal, Catatan)
            input_tanggal = st.date_input("Tanggal Transaksi", datetime.today())
            input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=5000)
            input_catatan = st.text_input("Keterangan / Catatan Tambahan (Misal: Bayar Netflix)")
            
            # Tombol Submit Form
            tombol_simpan = st.form_submit_button("🔥 Simpan Transaksi Ke Sistem")
            
            # Jalur Logika Eksekusi Pengiriman Data
            if tombol_simpan:
                if input_nominal > 0:
                    tanggal_teks = input_tanggal.strftime("%Y-%m-%d")
                    
                    # Menyusun baris sesuai urutan kolom baru di Google Sheets Anda
                    baris_baru = [tanggal_teks, input_tipe, input_sumber, input_kategori, input_nominal, input_catatan]
                    
                    # Menyisipkan data ke baris paling bawah di Google Sheets
                    worksheet.append_row(baris_baru)
                    st.success(f"Berhasil mencatat {input_tipe} sebesar Rp {input_nominal:,.0f} via {input_sumber}!")
                    st.balloons() # Efek animasi balon seru sebagai tanda sukses
                else:
                    st.warning("Mohon isi nominal uang terlebih dahulu sebelum menyimpan.")
