# --- MENGIMPOR LIBRARY ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu 

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Financely Dashboard", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- TARGET TABUNGAN IMPIAN ---
TARGET_NIKAH = 250000000
TARGET_RUMAH = 1500000000
TARGET_MOBIL = 300000000

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
    h1, h2, h3, h4 { font-weight: 700 !important; }
    
    [data-testid="stSidebar"] div.stForm { background-color: transparent; border: none; padding: 0;}
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
# BAGIAN 1: SIDEBAR (NAVIGASI & QUICK INPUT)
# ==========================================
with st.sidebar:
    st.markdown("### 🧭 Main Menu")
    
    menu_pilihan = option_menu(
        menu_title=None,  
        options=["Dashboard", "Spending", "Tabungan", "Wallet"], 
        icons=["house", "cart", "piggy-bank", "wallet2"], 
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"font-size": "16px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "font-weight": "600"},
            "nav-link-selected": {"background-color": "#0ea5e9", "color": "white"},
        }
    )
    
    st.divider()
    
    st.markdown("### 📅 Time Filter")
    filter_waktu = st.selectbox("Periode Analisa:", 
        ["Bulan Ini", "Minggu Ini", "3 Bulan Terakhir", "6 Bulan Terakhir", "Tahun Ini", "Semua Waktu"],
        label_visibility="collapsed"
    )
    
    hari_ini = datetime.today().date()
    if filter_waktu == "Minggu Ini": start_date = hari_ini - timedelta(days=hari_ini.weekday())
    elif filter_waktu == "Bulan Ini": start_date = hari_ini.replace(day=1)
    elif filter_waktu == "3 Bulan Terakhir": start_date = hari_ini - timedelta(days=90)
    elif filter_waktu == "6 Bulan Terakhir": start_date = hari_ini - timedelta(days=180)
    elif filter_waktu == "Tahun Ini": start_date = hari_ini.replace(month=1, day=1)
    else: start_date = hari_ini - timedelta(days=3650) 
        
    end_date = hari_ini
    
    st.divider()

    st.markdown("### ⚡ Quick Input")
    input_tipe = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan", "Tabungan"])
    
    with st.form("form_quick_input", clear_on_submit=True):
        input_sumber = st.selectbox("Sumber Dana", ["MANDIRI", "JAGO"])
        
        if input_tipe == "Pemasukan":
            kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
        elif input_tipe == "Tabungan":
            kategori_pilihan = ["Biaya Nikah", "Beli Rumah", "Mobil"]
        else:
            kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
            
        input_kategori = st.selectbox("Kategori", kategori_pilihan)
        input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=10000)
        
        col_tgl, col_cat = st.columns(2)
        with col_tgl: input_tanggal = st.date_input("Tanggal", datetime.today())
        with col_cat: input_catatan = st.text_input("Catatan")
        
        tombol_simpan = st.form_submit_button("Simpan Data", use_container_width=True)
        
        if tombol_simpan:
            if input_nominal > 0:
                worksheet.append_row([input_tanggal.strftime("%Y-%m-%d"), input_tipe, input_sumber, input_kategori, input_nominal, input_catatan])
                st.toast(f"✅ {input_tipe} Rp {input_nominal:,.0f} berhasil disimpan!", icon="💸") 
            else:
                st.error("Nominal tidak boleh 0")

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
# HALAMAN 1: DASHBOARD
# ==========================================
if menu_pilihan == "Dashboard":
    st.markdown("<h1 style='margin-bottom: 0px;'>Good morning, Difa ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; margin-bottom: 30px;'>This is your finance report</p>", unsafe_allow_html=True)
    
    if not df.empty:
        total_pemasukan_all = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_pengeluaran_all = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        total_tabungan_all = df[df['Tipe'] == 'Tabungan']['Nominal'].sum()
        saldo_aktif = total_pemasukan_all - total_pengeluaran_all - total_tabungan_all
        
        masuk_filter = df_filter[df_filter['Tipe'] == 'Pemasukan']['Nominal'].sum()
        keluar_filter = df_filter[df_filter['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        
        kolom_kiri, kolom_kanan = st.columns([7, 3])
        
        with kolom_kiri:
            k1, k2, k3 = st.columns([2, 1.5, 1.5])
            with k1: buat_kartu("💳", "MY BALANCE", f"Rp {saldo_aktif:,.0f}", "#0ea5e9", "Sisa kas siap pakai")
            with k2: buat_kartu("📥", "INCOME", f"Rp {masuk_filter:,.0f}", "#22c55e", f"{filter_waktu}")
            with k3: buat_kartu("📤", "EXPENSES", f"Rp {keluar_filter:,.0f}", "#ef4444", f"{filter_waktu}")
            
            st.write("")
            st.subheader("Statistics")
            
            df_tren = df_filter.groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
            df_tren = df_tren[df_tren['Tipe'].isin(['Pemasukan', 'Pengeluaran'])]
            
            fig_line = px.line(df_tren, x='Tanggal', y='Nominal', color='Tipe', 
                               color_discrete_map={"Pemasukan": "#22c55e", "Pengeluaran": "#ef4444"}, markers=True)
            fig_line.update_traces(line_shape='spline', line=dict(width=3))
            fig_line.update_layout(xaxis_title="", yaxis_title="", height=320,
                                   legend_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                                   margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_line, use_container_width=True)

        with kolom_kanan:
            buat_kartu("💰", "TOTAL SAVINGS", f"Rp {total_tabungan_all:,.0f}", "#8b5cf6", "Total aset tabungan")
            
            st.write("")
            st.subheader("All expenses")
            
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

        st.write("")
        st.subheader("Transaction and invoices")
        st.caption("Stay update on recent financial activities")
        st.dataframe(df_filter.iloc[::-1], use_container_width=True, hide_index=True)
        
    else:
        st.info("Belum ada data. Silakan isi form di sebelah kiri.")

# ==========================================
# HALAMAN 2: SPENDING
# ==========================================
elif menu_pilihan == "Spending":
    st.markdown("<h1 style='margin-bottom: 0px;'>🛒 Spending Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; margin-bottom: 30px;'>Detail pengeluaran Anda.</p>", unsafe_allow_html=True)
    
    if not df.empty:
        df_pengeluaran = df_filter[df_filter['Tipe'] == 'Pengeluaran']
        if not df_pengeluaran.empty:
            total_spend = df_pengeluaran['Nominal'].sum()
            buat_kartu("💸", f"TOTAL PENGELUARAN ({filter_waktu.upper()})", f"Rp {total_spend:,.0f}", "#ef4444", "Keseluruhan dana keluar")
            st.write("")
            
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                ringkasan = df_pengeluaran.groupby('Kategori')['Nominal'].sum().reset_index()
                fig_bar = px.bar(ringkasan, x='Kategori', y='Nominal', text_auto='.2s', color='Kategori', color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info(f"Tidak ada pengeluaran di periode {filter_waktu}.")
    else:
        st.info("Belum ada data.")

# ==========================================
# HALAMAN 3: TABUNGAN (UI BARU YANG LEBIH PREMIUM)
# ==========================================
elif menu_pilihan == "Tabungan":
    st.markdown("<h1 style='margin-bottom: 0px;'>🎯 Savings & Goals Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; margin-bottom: 30px;'>Pantau terus progres pencapaian impian Anda!</p>", unsafe_allow_html=True)
    
    if not df.empty:
        df_tabungan = df[df['Tipe'] == 'Tabungan'] 
        terkumpul_nikah = df_tabungan[df_tabungan['Kategori'] == 'Biaya Nikah']['Nominal'].sum()
        terkumpul_rumah = df_tabungan[df_tabungan['Kategori'] == 'Beli Rumah']['Nominal'].sum()
        terkumpul_mobil = df_tabungan[df_tabungan['Kategori'] == 'Mobil']['Nominal'].sum()
        
        total_tabungan_all = terkumpul_nikah + terkumpul_rumah + terkumpul_mobil
        total_target_all = TARGET_NIKAH + TARGET_RUMAH + TARGET_MOBIL
        
        # --- BAGIAN ATAS: RINGKASAN & GRAFIK ALOKASI ---
        kiri, kanan = st.columns([1, 2])
        with kiri:
            buat_kartu("🏆", "TOTAL ASET TABUNGAN", f"Rp {total_tabungan_all:,.0f}", "#8b5cf6", f"Dari total target Rp {total_target_all:,.0f}")
            
        with kanan:
            if total_tabungan_all > 0:
                df_tab_group = df_tabungan.groupby('Kategori')['Nominal'].sum().reset_index()
                fig_pie_tab = px.pie(df_tab_group, values='Nominal', names='Kategori', hole=0.5,
                                     color_discrete_sequence=["#ec4899", "#0ea5e9", "#eab308"])
                fig_pie_tab.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=160,
                                          legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1))
                st.plotly_chart(fig_pie_tab, use_container_width=True)
            else:
                st.info("Mulai menabung untuk melihat grafik porsi alokasi!")

        st.divider()
        st.markdown("### 🚀 Detail Target")
        
        # --- BAGIAN BAWAH: GRID KARTU TARGET (3 KOLOM SEJAJAR) ---
        c1, c2, c3 = st.columns(3)
        
        def render_goal_card(col, icon, title, terkumpul, target, color_hex):
            with col:
                with st.container(border=True):
                    persen = min((terkumpul / target) if target > 0 else 0, 1.0)
                    sisa = max(target - terkumpul, 0)
                    
                    st.markdown(f"<h4 style='margin-bottom: 0px;'>{icon} {title}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color: {color_hex}; margin-top: 5px; margin-bottom: 10px;'>Rp {terkumpul:,.0f}</h2>", unsafe_allow_html=True)
                    
                    st.progress(persen)
                    
                    st.markdown(f"""
                        <div style='display: flex; justify-content: space-between; font-size: 13px; color: gray; margin-top: 5px;'>
                            <span>🎯 Target: <b>Rp {target:,.0f}</b></span>
                            <span style='color: {color_hex}; font-weight: bold;'>{persen*100:.1f}%</span>
                        </div>
                        <div style='font-size: 13px; color: gray; margin-top: 5px;'>
                            ⏳ Kekurangan: <b>Rp {sisa:,.0f}</b>
                        </div>
                    """, unsafe_allow_html=True)

        render_goal_card(c1, "💍", "Biaya Nikah", terkumpul_nikah, TARGET_NIKAH, "#ec4899") # Warna Pink
        render_goal_card(c2, "🏠", "Beli Rumah", terkumpul_rumah, TARGET_RUMAH, "#0ea5e9") # Warna Biru
        render_goal_card(c3, "🚗", "Mobil", terkumpul_mobil, TARGET_MOBIL, "#eab308") # Warna Kuning
        
    else:
        st.info("Belum ada tabungan yang tercatat.")

# ==========================================
# HALAMAN 4: WALLET
# ==========================================
elif menu_pilihan == "Wallet":
    st.markdown("<h1 style='margin-bottom: 0px;'>🏛️ Wallet & Accounts</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; margin-bottom: 30px;'>Kondisi kas nyata di rekening Anda saat ini.</p>", unsafe_allow_html=True)
    
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
