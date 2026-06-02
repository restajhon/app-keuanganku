# --- MENGIMPOR LIBRARY ---
import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu 

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Financely Workspace", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KeuanganKu")
worksheet = sheet_file.sheet1 

# --- TARGET TABUNGAN IMPIAN (UBAH ANGKA DI SINI) ---
TARGET_NIKAH = 250000000
TARGET_RUMAH = 1500000000
TARGET_MOBIL = 400000000
TARGET_JALAN = 20000000
TARGET_UMROH = 35000000

# --- GAYA DESAIN CUSTOM (CSS) SUPER PREMIUM ---
st.markdown("""
    <style>
    /* Memaksimalkan lebar layar dan membuang ruang kosong di atas/bawah */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    
    /* MENARIK SIDEBAR KE ATAS AGAR TIDAK KOSONG */
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Efek Glassmorphism Modern untuk Kartu */
    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(14, 165, 233, 0.5); /* Efek glow biru saat dihover */
        box-shadow: 0 12px 40px 0 rgba(14, 165, 233, 0.15);
    }
    
    /* Tipografi Kekinian */
    .card-title { font-size: 14px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; color: #888; letter-spacing: 1px;}
    .card-value { font-size: 36px; font-weight: 900; margin-bottom: 5px; line-height: 1.1;}
    .card-subtext { font-size: 13px; color: #888; font-weight: 500;}
    h1, h2, h3, h4 { font-weight: 800 !important; letter-spacing: -0.5px; }
    
    /* Merapikan Form di Sidebar */
    [data-testid="stSidebar"] div.stForm { background-color: transparent; border: none; padding: 0;}
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.2); }
    </style>
""", unsafe_allow_html=True)

# Fungsi Pembuat Kartu Modern
def buat_kartu(icon, judul, nilai, warna_nilai, teks_bawah):
    html = f"""
    <div class="glass-card">
        <div class="card-title">{icon} {judul}</div>
        <div class="card-value" style="color: {warna_nilai};">{nilai}</div>
        <div class="card-subtext">{teks_bawah}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Fungsi Pembuat Banner Header
def buat_banner(judul, subjudul, gradient="linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%)"):
    html = f"""
    <div style='background: {gradient}; padding: 30px 40px; border-radius: 16px; color: white; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
        <h1 style='color: white; margin-top: 0; font-size: 38px; font-weight: 900; letter-spacing: -1px;'>{judul}</h1>
        <p style='margin-bottom: 0; font-size: 16px; opacity: 0.85; font-weight: 500;'>{subjudul}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# BAGIAN 1: SIDEBAR (NAVIGASI & QUICK INPUT)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>⚡ Financely</h3>", unsafe_allow_html=True)
    
    menu_pilihan = option_menu(
        menu_title=None,  
        options=["Dashboard", "Spending", "Tabungan", "Wallet"], 
        icons=["grid-1x2-fill", "bag-dash-fill", "piggy-bank-fill", "wallet-fill"], 
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"8px 0px", "font-weight": "600", "border-radius": "10px"},
            "nav-link-selected": {"background-color": "#0ea5e9", "color": "white", "box-shadow": "0 4px 12px rgba(14,165,233,0.3)"},
        }
    )
    
    st.write("")
    st.markdown("### 📅 Time Filter")
    filter_waktu = st.selectbox("Periode Analisa:", 
        ["Hari Ini", "Bulan Ini", "Minggu Ini", "3 Bulan Terakhir", "6 Bulan Terakhir", "Tahun Ini", "Semua Waktu"],
        label_visibility="collapsed", index=1
    )
    
    hari_ini = datetime.today().date()
    if filter_waktu == "Hari Ini": start_date = hari_ini
    elif filter_waktu == "Minggu Ini": start_date = hari_ini - timedelta(days=hari_ini.weekday())
    elif filter_waktu == "Bulan Ini": start_date = hari_ini.replace(day=1)
    elif filter_waktu == "3 Bulan Terakhir": start_date = hari_ini - timedelta(days=90)
    elif filter_waktu == "6 Bulan Terakhir": start_date = hari_ini - timedelta(days=180)
    elif filter_waktu == "Tahun Ini": start_date = hari_ini.replace(month=1, day=1)
    else: start_date = hari_ini - timedelta(days=3650) 
    end_date = hari_ini
    
    st.divider()

    st.markdown("### ✨ Quick Action")
    input_tipe = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan", "Tabungan"])
    
    with st.form("form_quick_input", clear_on_submit=True):
        input_sumber = st.selectbox("Sumber Dana", ["MANDIRI", "JAGO"])
        
        if input_tipe == "Pemasukan":
            kategori_pilihan = ["GITS", "WO", "Freelance", "Lain-lain"]
        elif input_tipe == "Tabungan":
            kategori_pilihan = ["Biaya Nikah", "Beli Rumah", "Mobil", "Jalan-jalan", "Umroh"]
        else:
            kategori_pilihan = ["Makanan", "Transportasi", "Belanja", "Tagihan", "Subscription", "Lain-lain"]
            
        input_kategori = st.selectbox("Kategori", kategori_pilihan)
        input_nominal = st.number_input("Nominal (Rp)", min_value=0, step=10000)
        
        col_tgl, col_cat = st.columns(2)
        with col_tgl: input_tanggal = st.date_input("Tanggal", datetime.today())
        with col_cat: input_catatan = st.text_input("Catatan")
        
        tombol_simpan = st.form_submit_button("Simpan Data", use_container_width=True)
        
        if tombol_simpan and input_nominal > 0:
            worksheet.append_row([input_tanggal.strftime("%Y-%m-%d"), input_tipe, input_sumber, input_kategori, input_nominal, input_catatan])
            st.toast(f"✅ {input_tipe} Rp {input_nominal:,.0f} berhasil disimpan!", icon="🔥") 

# ==========================================
# PROSES DATA GOOGLE SHEETS
# ==========================================
data_semua = worksheet.get_all_records()
df = pd.DataFrame(data_semua) if len(data_semua) > 0 else pd.DataFrame()

if not df.empty:
    df['Nominal'] = pd.to_numeric(df['Nominal'])
    df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
    df_filter = df.loc[(df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)]

# Palet Warna Keren untuk Grafik
CHART_COLORS = ["#0ea5e9", "#f43f5e", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#14b8a6"]

# ==========================================
# HALAMAN 1: DASHBOARD
# ==========================================
if menu_pilihan == "Dashboard":
    buat_banner("Good morning, Difa ✨", "Corporate & MUA Financial Hub — Your daily cashflow overview.")
    
    if not df.empty:
        total_pemasukan_all = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_pengeluaran_all = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        total_tabungan_all = df[df['Tipe'] == 'Tabungan']['Nominal'].sum()
        saldo_aktif = total_pemasukan_all - total_pengeluaran_all - total_tabungan_all
        
        masuk_filter = df_filter[df_filter['Tipe'] == 'Pemasukan']['Nominal'].sum()
        keluar_filter = df_filter[df_filter['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        
        k1, k2, k3, k4 = st.columns(4)
        with k1: buat_kartu("💳", "NET LIQUIDITY", f"Rp {saldo_aktif:,.0f}", "#0ea5e9", "Total kas aktif siap pakai")
        with k2: buat_kartu("💰", "TOTAL ASSETS", f"Rp {total_tabungan_all:,.0f}", "#8b5cf6", "Akumulasi seluruh tabungan")
        with k3: buat_kartu("📥", "CASH IN", f"Rp {masuk_filter:,.0f}", "#10b981", f"Pemasukan {filter_waktu.lower()}")
        with k4: buat_kartu("📤", "CASH OUT", f"Rp {keluar_filter:,.0f}", "#f43f5e", f"Pengeluaran {filter_waktu.lower()}")
        
        st.write("")
        g1, g2 = st.columns([7, 3])
        with g1:
            with st.container():
                st.markdown("#### 📈 Cashflow Velocity")
                df_tren = df_filter[df_filter['Tipe'].isin(['Pemasukan', 'Pengeluaran'])].groupby(['Tanggal', 'Tipe'])['Nominal'].sum().reset_index()
                if not df_tren.empty:
                    fig_line = px.line(df_tren, x='Tanggal', y='Nominal', color='Tipe', color_discrete_map={"Pemasukan": "#10b981", "Pengeluaran": "#f43f5e"}, markers=True)
                    fig_line.update_traces(line_shape='spline', line=dict(width=3, shape='spline'), marker=dict(size=6))
                    fig_line.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                    st.plotly_chart(fig_line, use_container_width=True)
                else: st.info("Area grafik trend.")
                
        with g2:
            with st.container():
                st.markdown("#### 🛒 Top Expenses")
                df_pengeluaran = df_filter[df_filter['Tipe'] == 'Pengeluaran']
                if not df_pengeluaran.empty:
                    fig_pie = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.65, color_discrete_sequence=CHART_COLORS)
                    fig_pie.update_traces(textposition='inside', textinfo='percent')
                    fig_pie.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1))
                    st.plotly_chart(fig_pie, use_container_width=True)
                else: st.info("Area grafik proporsi.")

        st.write("---")
        
        # --- FITUR BARU: TOTAL MONTHLY SUMMARY ---
        st.markdown("#### 📅 Total Monthly Summary")
        df_monthly = df.copy()
        if not df_monthly.empty:
            df_monthly['Tanggal'] = pd.to_datetime(df_monthly['Tanggal'])
            df_monthly['Bulan'] = df_monthly['Tanggal'].dt.strftime('%B %Y')
            
            df_summary = df_monthly[df_monthly['Tipe'].isin(['Pemasukan', 'Pengeluaran'])].groupby(['Bulan', 'Tipe'])['Nominal'].sum().unstack(fill_value=0).reset_index()
            
            for col in ['Pemasukan', 'Pengeluaran']:
                if col not in df_summary.columns:
                    df_summary[col] = 0
                    
            df_summary['Sisa'] = df_summary['Pemasukan'] - df_summary['Pengeluaran']
            
            st.dataframe(
                df_summary.style.format({
                    "Pemasukan": "Rp {:,.0f}", 
                    "Pengeluaran": "Rp {:,.0f}", 
                    "Sisa": "Rp {:,.0f}"
                }).map(lambda x: 'color: #10b981' if x > 0 else ('color: #f43f5e' if x < 0 else ''), subset=['Sisa']), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Belum ada data transaksi bulanan.")

        st.write("")
        st.markdown("#### 📋 Transaction Ledger")
        col_f1, col_f2 = st.columns(2)
        with col_f1: pil_tipe = st.multiselect("Filter Tipe:", ["Pemasukan", "Pengeluaran", "Tabungan"], default=["Pemasukan", "Pengeluaran", "Tabungan"])
        with col_f2: pil_sumber = st.multiselect("Filter Sumber:", ["MANDIRI", "JAGO"], default=["MANDIRI", "JAGO"])
        
        df_tabel = df_filter[(df_filter['Tipe'].isin(pil_tipe)) & (df_filter['Sumber'].isin(pil_sumber))]
        st.dataframe(df_tabel.iloc[::-1], use_container_width=True, hide_index=True, height=250)
    else: st.info("Belum ada data.")

# ==========================================
# HALAMAN 2: SPENDING
# ==========================================
elif menu_pilihan == "Spending":
    buat_banner("🛒 Spending Intelligence", "Analisis mendalam mengenai arus kas keluar Anda.", "linear-gradient(90deg, #4c0519 0%, #be123c 100%)")
    
    if not df.empty:
        df_pengeluaran = df_filter[df_filter['Tipe'] == 'Pengeluaran']
        if not df_pengeluaran.empty:
            total_spend = df_pengeluaran['Nominal'].sum()
            avg_spend = df_pengeluaran.groupby('Tanggal')['Nominal'].sum().mean()
            top_category = df_pengeluaran.groupby('Kategori')['Nominal'].sum().idxmax()
            
            k1, k2, k3 = st.columns(3)
            with k1: buat_kartu("💸", "TOTAL SPENDING", f"Rp {total_spend:,.0f}", "#f43f5e", f"Periode: {filter_waktu}")
            with k2: buat_kartu("📊", "DAILY AVERAGE", f"Rp {avg_spend:,.0f}", "#f59e0b", "Rata-rata pengeluaran per hari")
            with k3: buat_kartu("🔥", "TOP BURNER", f"{top_category}", "#8b5cf6", "Kategori paling banyak menguras dana")
            
            st.write("")
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown("#### 🍩 Proporsi Kategori")
                fig_pie = px.pie(df_pengeluaran, values='Nominal', names='Kategori', hole=0.5, color_discrete_sequence=CHART_COLORS)
                fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                # --- FITUR BARU: TOP 5 SPENDING ---
                st.markdown("#### 🚨 Top 5 Spending Categories")
                top_5 = df_pengeluaran.groupby('Kategori')['Nominal'].sum().nlargest(5).reset_index()
                
                fig_top5 = px.bar(
                    top_5, x='Nominal', y='Kategori', orientation='h', 
                    text_auto='.2s', color='Nominal', color_continuous_scale='Reds'
                )
                fig_top5.update_layout(
                    yaxis={'categoryorder':'total ascending'}, 
                    xaxis_title="", yaxis_title="", showlegend=False, 
                    height=350, margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_top5, use_container_width=True)
            
            st.write("---")
            
            # --- FITUR BARU: CATEGORIZATION HEATMAP ---
            st.markdown("### 🗓️ Daily Spending Heatmap")
            df_heat = df[df['Tipe'] == 'Pengeluaran'].copy()
            if not df_heat.empty:
                df_heat['Tanggal'] = pd.to_datetime(df_heat['Tanggal'])
                df_heat['Bulan'] = df_heat['Tanggal'].dt.strftime('%Y-%m')
                df_heat['Hari'] = df_heat['Tanggal'].dt.day
                
                heat_data = df_heat.groupby(['Bulan', 'Hari'])['Nominal'].sum().reset_index()
                pivot_heat = heat_data.pivot(index="Bulan", columns="Hari", values="Nominal").fillna(0)
                pivot_heat = pivot_heat.reindex(columns=range(1, 32), fill_value=0)
                
                fig_heat = px.imshow(
                    pivot_heat, 
                    labels=dict(x="Tanggal", y="Bulan", color="Pengeluaran (Rp)"),
                    x=pivot_heat.columns, y=pivot_heat.index,
                    color_continuous_scale="RdYlGn_r", aspect="auto"
                )
                fig_heat.update_xaxes(side="top", tickmode="linear", dtick=1)
                fig_heat.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("Belum ada data pengeluaran untuk menampilkan heatmap kalender.")

        else: st.info(f"Tidak ada pengeluaran di periode {filter_waktu}.")
    else: st.info("Belum ada data.")

# ==========================================
# HALAMAN 3: TABUNGAN
# ==========================================
elif menu_pilihan == "Tabungan":
    buat_banner("🎯 Goal & Wealth Tracker", "Visualisasi progres portofolio tabungan masa depan.", "linear-gradient(90deg, #2e1065 0%, #6d28d9 100%)")
    
    if not df.empty:
        df_tabungan = df[df['Tipe'] == 'Tabungan'] 
        
        terkumpul_nikah = df_tabungan[df_tabungan['Kategori'] == 'Biaya Nikah']['Nominal'].sum()
        terkumpul_rumah = df_tabungan[df_tabungan['Kategori'] == 'Beli Rumah']['Nominal'].sum()
        terkumpul_mobil = df_tabungan[df_tabungan['Kategori'] == 'Mobil']['Nominal'].sum()
        terkumpul_jalan = df_tabungan[df_tabungan['Kategori'] == 'Jalan-jalan']['Nominal'].sum()
        terkumpul_umroh = df_tabungan[df_tabungan['Kategori'] == 'Umroh']['Nominal'].sum()
        
        total_tabungan_all = terkumpul_nikah + terkumpul_rumah + terkumpul_mobil + terkumpul_jalan + terkumpul_umroh
        total_target_all = TARGET_NIKAH + TARGET_RUMAH + TARGET_MOBIL + TARGET_JALAN + TARGET_UMROH
        
        kiri, kanan = st.columns([1.5, 1])
        with kiri:
            buat_kartu("🏆", "TOTAL WEALTH ACCUMULATED", f"Rp {total_tabungan_all:,.0f}", "#8b5cf6", f"Mencapai {min((total_tabungan_all/total_target_all)*100, 100):,.1f}% dari total Grand Target Rp {total_target_all:,.0f}")
        with kanan:
            if total_tabungan_all > 0:
                df_tab_group = df_tabungan.groupby('Kategori')['Nominal'].sum().reset_index()
                fig_pie_tab = px.pie(df_tab_group, values='Nominal', names='Kategori', hole=0.6, color_discrete_sequence=["#ec4899", "#0ea5e9", "#eab308", "#10b981", "#8b5cf6"])
                fig_pie_tab.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=140, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1))
                st.plotly_chart(fig_pie_tab, use_container_width=True)
            else: st.write("")

        st.write("")
        st.markdown("### 🚀 Portfolio Blueprint")
        
        def render_goal_card(col, icon, title, terkumpul, target, color_hex):
            with col:
                with st.container():
                    persen = min((terkumpul / target) if target > 0 else 0, 1.0)
                    sisa = max(target - terkumpul, 0)
                    html = f"""
                    <div class="glass-card" style="border-top: 4px solid {color_hex}; margin-bottom: 15px;">
                        <h3 style='margin-bottom: 0px; color: #888;'>{icon} {title}</h3>
                        <h2 style='color: {color_hex}; margin-top: 10px; margin-bottom: 15px; font-size: 30px;'>Rp {terkumpul:,.0f}</h2>
                    """
                    st.markdown(html, unsafe_allow_html=True)
                    st.progress(persen)
                    st.markdown(f"""
                        <div style='display: flex; justify-content: space-between; font-size: 14px; color: gray; margin-top: 8px;'>
                            <span>Target: <b>Rp {target:,.0f}</b></span>
                            <span style='color: {color_hex}; font-weight: 800;'>{persen*100:.1f}%</span>
                        </div>
                        <div style='font-size: 14px; color: gray; margin-top: 4px;'>
                            Kekurangan: <b>Rp {sisa:,.0f}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        render_goal_card(c1, "💍", "Biaya Nikah", terkumpul_nikah, TARGET_NIKAH, "#ec4899")
        render_goal_card(c2, "🏠", "Beli Rumah", terkumpul_rumah, TARGET_RUMAH, "#0ea5e9")
        render_goal_card(c3, "🚗", "Mobil", terkumpul_mobil, TARGET_MOBIL, "#eab308")
        
        c4, c5, c6 = st.columns(3)
        render_goal_card(c4, "✈️", "Jalan-jalan", terkumpul_jalan, TARGET_JALAN, "#10b981")
        render_goal_card(c5, "🕋", "Umroh", terkumpul_umroh, TARGET_UMROH, "#8b5cf6")
        
    else: st.info("Belum ada tabungan.")

# ==========================================
# HALAMAN 4: WALLET & ACCOUNTS
# ==========================================
elif menu_pilihan == "Wallet":
    buat_banner("🏛️ Wallet & Accounts", "Status likuiditas dan pemetaan aliran dana masuk.", "linear-gradient(90deg, #064e3b 0%, #047857 100%)")
    
    if not df.empty:
        masuk_mandiri = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        keluar_mandiri = df[(df['Tipe'] != 'Pemasukan') & (df['Sumber'] == 'MANDIRI')]['Nominal'].sum()
        sisa_mandiri = masuk_mandiri - keluar_mandiri
        
        masuk_jago = df[(df['Tipe'] == 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        keluar_jago = df[(df['Tipe'] != 'Pemasukan') & (df['Sumber'] == 'JAGO')]['Nominal'].sum()
        sisa_jago = masuk_jago - keluar_jago
        
        c1, c2 = st.columns(2)
        with c1: buat_kartu("🏦", "BANK MANDIRI (UTAMA)", f"Rp {sisa_mandiri:,.0f}", "#0ea5e9", "Akun Penampungan & Transaksi Utama")
        with c2: buat_kartu("🟡", "BANK JAGO (OPERASIONAL)", f"Rp {sisa_jago:,.0f}", "#f59e0b", "Kantong Operasional Harian")
            
        st.write("")
        st.markdown(f"### 💼 Income Streams ({filter_waktu})")
        masuk_gits = df_filter[(df_filter['Tipe'] == 'Pemasukan') & (df_filter['Kategori'] == 'GITS')]['Nominal'].sum()
        masuk_wo = df_filter[(df_filter['Tipe'] == 'Pemasukan') & (df_filter['Kategori'] == 'WO')]['Nominal'].sum()
        masuk_freelance = df_filter[(df_filter['Tipe'] == 'Pemasukan') & (df_filter['Kategori'] == 'Freelance')]['Nominal'].sum()
        
        k1, k2, k3 = st.columns(3)
        with k1: buat_kartu("🏢", "CORPORATE (GITS)", f"Rp {masuk_gits:,.0f}", "#10b981", "Pendapatan Profesional Utama")
        with k2: buat_kartu("💍", "WEDDING ORGANIZER", f"Rp {masuk_wo:,.0f}", "#ec4899", "Pendapatan MUA & Project")
        with k3: buat_kartu("💻", "FREELANCE", f"Rp {masuk_freelance:,.0f}", "#8b5cf6", "Pendapatan Sampingan")
            
        st.write("")
        st.markdown("#### 📋 History Transaksi")
        col_w1, col_w2 = st.columns(2)
        with col_w1: pil_tipe = st.multiselect("Filter Tipe:", ["Pemasukan", "Pengeluaran", "Tabungan"], default=["Pemasukan", "Pengeluaran", "Tabungan"], key="w_tipe")
        with col_w2: pil_sumber = st.multiselect("Filter Sumber:", ["MANDIRI", "JAGO"], default=["MANDIRI", "JAGO"], key="w_sumber")
            
        df_tabel_wallet = df_filter[(df_filter['Tipe'].isin(pil_tipe)) & (df_filter['Sumber'].isin(pil_sumber))]
        st.dataframe(df_tabel_wallet.iloc[::-1], use_container_width=True, hide_index=True)
    else: st.info("Belum ada data.")
