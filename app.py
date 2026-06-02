# --- MENGIMPOR LIBRARY YANG DIBUTUHKAN ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Dashboard Keuangan", page_icon="💰", layout="wide")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- JUDUL APLIKASI ---
st.title("💸 Pencatatan Keuangan Pribadi V2")

# --- MEMBUAT DUA TAB ---
tab_input, tab_dashboard = st.tabs(["📝 Input Transaksi", "📊 Dashboard Analisa"])

# --- BAGIAN 1: TAB INPUT TRANSAKSI ---
with tab_input:
    st.subheader("Catat Transaksi Baru")
    
    # KUNCI PENTING: Pilihan Tipe Transaksi diletakkan di LUAR form
    # Agar pilihan Kategori di bawahnya bisa berubah otomatis saat Tipe diklik
    input_tipe = st.radio("Pilih Jenis Transaksi:", ["Pengeluaran", "Pemasukan"], horizontal=True)
    
    # Logika untuk mengubah pilihan kategori berdasarkan Tipe Transaksi
    if input_tipe == "Pengeluaran":
        kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
    else:
        # Jika Pemasukan yang dipilih, tampilkan kategori ini
        kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
    
    # Membuat form inputan
    with st.form("form_transaksi", clear_on_submit=True):
        input_tanggal = st.date_input("Pilih Tanggal", datetime.today())
        
        # Dropdown kategori yang isinya sudah disesuaikan dengan logika di atas
        input_kategori = st.selectbox("Kategori", kategori_pilihan)
        
        input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        input_catatan = st.text_input("Catatan Tambahan")
        tombol_simpan = st.form_submit_button("Simpan Data")
        
        if tombol_simpan:
            if input_nominal > 0:
                tanggal_teks = input_tanggal.strftime("%Y-%m-%d")
                
                # Menambahkan 'input_tipe' ke dalam data yang akan dikirim ke Sheets
                # Format susunan kolom: Tanggal, Tipe, Kategori, Nominal, Catatan
                baris_baru = [tanggal_teks, input_tipe, input_kategori, input_nominal, input_catatan]
                worksheet.append_row(baris_baru)
                
                st.success(f"Data {input_tipe} berhasil disimpan ke Google Sheets!")
            else:
                st.warning("Nominal transaksi tidak boleh 0.")

# --- BAGIAN 2: TAB DASHBOARD ANALISA ---
with tab_dashboard:
    st.subheader("Ringkasan Keuangan Anda")
    
    data_semua = worksheet.get_all_records()
    
    if len(data_semua) > 0:
        df = pd.DataFrame(data_semua)
        df['Nominal'] = pd.to_numeric(df['Nominal'])
        
        # Memisahkan data Pemasukan dan Pengeluaran
        # Perhatikan: pastikan huruf besar/kecil di Google Sheets sama persis ("Pemasukan" & "Pengeluaran")
        df_pemasukan = df[df['Tipe'] == 'Pemasukan']
        df_pengeluaran = df[df['Tipe'] == 'Pengeluaran']
        
        # Menghitung total masing-masing
        total_pemasukan = df_pemasukan['Nominal'].sum()
        total_pengeluaran = df_pengeluaran['Nominal'].sum()
        
        # Menghitung sisa saldo (Uang yang dimiliki)
        sisa_saldo = total_pemasukan - total_pengeluaran
        
        # Menampilkan 3 Kartu Informasi (Metrics) berdampingan
        kolom_metrik1, kolom_metrik2, kolom_metrik3 = st.columns(3)
        kolom_metrik1.metric(label="Total Pemasukan", value=f"Rp {total_pemasukan:,.0f}")
        kolom_metrik2.metric(label="Total Pengeluaran", value=f"Rp {total_pengeluaran:,.0f}")
        kolom_metrik3.metric(label="Saldo Saat Ini", value=f"Rp {sisa_saldo:,.0f}")
        
        st.divider()
        
        # Menampilkan grafik pie berdampingan
        kolom_grafik1, kolom_grafik2 = st.columns(2)
        
        with kolom_grafik1:
            st.markdown("**Distribusi Pengeluaran**")
            if not df_pengeluaran.empty:
                grafik_pie_out = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.4)
                st.plotly_chart(grafik_pie_out, use_container_width=True)
            else:
                st.info("Belum ada data pengeluaran.")
                
        with kolom_grafik2:
            st.markdown("**Sumber Pemasukan**")
            if not df_pemasukan.empty:
                grafik_pie_in = px.pie(df_pemasukan, values='Nominal', names='Kategori', hole=0.4)
                st.plotly_chart(grafik_pie_in, use_container_width=True)
            else:
                st.info("Belum ada data pemasukan.")
        
        # Menampilkan tabel data mentah yang diurutkan dari yang terbaru
        st.write("Riwayat Transaksi Keseluruhan:")
        st.dataframe(df.sort_values(by="Tanggal", ascending=False), use_container_width=True)
        
    else:
        st.info("Belum ada data. Silakan isi di tab 'Input Transaksi'.")
