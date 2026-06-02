# --- MENGIMPOR LIBRARY YANG DIBUTUHKAN ---
import streamlit as st # Library utama untuk membuat tampilan web
import gspread # Library untuk membaca dan menulis ke Google Sheets
import pandas as pd # Library untuk mengolah data tabel
import plotly.express as px # Library untuk membuat grafik interaktif yang cantik
from datetime import datetime # Library untuk mengambil tanggal hari ini otomatis

# --- PENGATURAN HALAMAN WEB ---
# Mengatur nama tab di browser dan membuat tampilan lebar (wide) agar enak di laptop
st.set_page_config(page_title="Dashboard Keuangan", page_icon="💰", layout="wide")

# --- KONEKSI KE GOOGLE SHEETS ---
# Mengambil data kunci rahasia (JSON) dari sistem penyimpanan rahasia Streamlit
# Nanti kita akan mengatur ini di tahap Deploy (Tahap C)
kredensial = st.secrets["gcp_service_account"]

# Menghubungkan script ini ke akun Google Cloud menggunakan kredensial tadi
gc = gspread.service_account_from_dict(kredensial)

# Membuka file spreadsheet yang bernama "KeuanganKu"
sheet_file = gc.open("KeuanganKu")

# Memilih tab pertama (Sheet1) yang ada di dalam file tersebut
worksheet = sheet_file.sheet1 

# --- JUDUL APLIKASI ---
st.title("💸 Pencatatan Keuangan Pribadi")

# --- MEMBUAT DUA TAB: UNTUK INPUT (HP) & DASHBOARD (LAPTOP) ---
# Membagi halaman menjadi 2 bagian yang bisa diklik
tab_input, tab_dashboard = st.tabs(["📝 Input Pengeluaran", "📊 Dashboard Analisa"])

# --- BAGIAN 1: TAB INPUT PENGELUARAN ---
with tab_input:
    st.subheader("Catat Pengeluaran Baru")
    
    # Membuat form inputan
    with st.form("form_pengeluaran", clear_on_submit=True):
        # Input tanggal, defaultnya adalah hari ini
        input_tanggal = st.date_input("Pilih Tanggal", datetime.today())
        
        # Pilihan kategori berupa dropdown (bisa ditambah/dikurangi sesuai kebutuhan)
        kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Lain-lain"]
        input_kategori = st.selectbox("Kategori", kategori_pilihan)
        
        # Input angka untuk nominal uang, step=1000 agar naiknya per seribu perak
        input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        
        # Input teks bebas untuk catatan
        input_catatan = st.text_input("Catatan Tambahan")
        
        # Tombol untuk menyimpan data
        tombol_simpan = st.form_submit_button("Simpan Data")
        
        # Logika ketika tombol ditekan
        if tombol_simpan:
            if input_nominal > 0: # Memastikan nominal tidak nol
                # Mengubah format tanggal menjadi teks agar bisa masuk ke Excel/Sheets
                tanggal_teks = input_tanggal.strftime("%Y-%m-%d")
                
                # Menyiapkan satu baris data baru untuk dikirim ke Google Sheets
                baris_baru = [tanggal_teks, input_kategori, input_nominal, input_catatan]
                
                # Perintah untuk menulis baris baru tersebut ke posisi terbawah di Google Sheets
                worksheet.append_row(baris_baru)
                
                # Memunculkan pesan sukses berwarna hijau
                st.success("Data berhasil disimpan ke Google Sheets!")
            else:
                # Memunculkan pesan peringatan jika nominal masih 0
                st.warning("Nominal pengeluaran tidak boleh 0.")

# --- BAGIAN 2: TAB DASHBOARD ANALISA ---
with tab_dashboard:
    st.subheader("Ringkasan Keuangan Anda")
    
    # Membaca seluruh data dari Google Sheets dan merubahnya menjadi bentuk tabel (DataFrame)
    data_semua = worksheet.get_all_records()
    
    # Mengecek apakah Google Sheets sudah ada isinya atau masih kosong
    if len(data_semua) > 0:
        # Jika ada isinya, ubah data mentah menjadi tabel yang mudah diolah oleh Python (Pandas)
        df = pd.DataFrame(data_semua)
        
        # Mengubah kolom 'Nominal' menjadi tipe angka agar bisa dijumlahkan
        df['Nominal'] = pd.to_numeric(df['Nominal'])
        
        # Menghitung total semua pengeluaran dari seluruh baris
        total_pengeluaran = df['Nominal'].sum()
        
        # Menampilkan kartu informasi (Metric) yang menunjukkan total pengeluaran
        # Format {:,.0f} digunakan agar angkanya punya pemisah ribuan (contoh: 10,000)
        st.metric(label="Total Pengeluaran", value=f"Rp {total_pengeluaran:,.0f}")
        
        # Membuat garis pemisah
        st.divider()
        
        # Menyiapkan kolom agar grafik bisa bersebelahan jika layarnya lebar
        kolom1, kolom2 = st.columns(2)
        
        with kolom1:
            # Membuat Pie Chart berdasarkan Kategori dan jumlah Nominalnya
            grafik_pie = px.pie(df, values='Nominal', names='Kategori', title="Proporsi per Kategori")
            # Menampilkan grafik pie di halaman web
            st.plotly_chart(grafik_pie, use_container_width=True)
            
        with kolom2:
            # Membuat tabel ringkasan: menjumlahkan total nominal untuk masing-masing kategori
            ringkasan_kategori = df.groupby('Kategori')['Nominal'].sum().reset_index()
            # Membuat Bar Chart berdasarkan ringkasan tersebut
            grafik_bar = px.bar(ringkasan_kategori, x='Kategori', y='Nominal', title="Total per Kategori", text_auto=True)
            # Menampilkan grafik bar di halaman web
            st.plotly_chart(grafik_bar, use_container_width=True)
            
        # Menampilkan data mentahnya dalam bentuk tabel di bawah grafik
        st.write("Riwayat Transaksi Terakhir:")
        st.dataframe(df, use_container_width=True)
        
    else:
        # Jika Google Sheets masih kosong (hanya ada header), tampilkan pesan ini
        st.info("Belum ada data pengeluaran. Silakan isi di tab 'Input Pengeluaran'.")