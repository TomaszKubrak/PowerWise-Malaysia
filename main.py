import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 1. APPLICATION THEME SETUP & CUSTOM GRAPHICS
# ----------------------------------------------------
st.set_page_config(
    page_title="PowerWise Malaysia | Interactive Portal",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling to mimic a slick high-fidelity dashboard
st.markdown(
    """
    <style>
    .main-title { font-size: 2.6rem !important; font-weight: 700 !important; color: #1E3A8A; }
    .stAlert { border-radius: 10px !important; }
    .metric-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; color: #1F2937; }
    /* Make the radio button navigation look like tab pills */
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        background-color: #F3F4F6;
        padding: 6px;
        border-radius: 10px;
    }
    div[data-testid="stRadio"] label {
        background-color: white;
        padding: 8px 16px;
        border-radius: 8px;
        margin-right: 4px;
        border: 1px solid #E5E7EB;
        cursor: pointer;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# 2. SESSION STATE STATE MACHINE ENGINE
# ----------------------------------------------------
# TAB NAVIGATION STATE TRACKER (Locks active viewpoint safely across clicks)
if "active_tab_index" not in st.session_state:
    st.session_state.active_tab_index = 0

if "s1_step" not in st.session_state:
    st.session_state.s1_step = 1  # Tracks Aisyah's walkthrough steps
if "kwh_input_value" not in st.session_state:
    st.session_state.kwh_input_value = 210.0
if "bill_input_value" not in st.session_state:
    st.session_state.bill_input_value = 54.0
if "scen2_saved" not in st.session_state:
    st.session_state.scen2_saved = False
if "s3_calculated" not in st.session_state:
    st.session_state.s3_calculated = False

# ----------------------------------------------------
# 3. TRANSLATION DICTIONARY (100% Comprehensive Coverage)
# ----------------------------------------------------
CONTENT_DICTIONARY = {
    "English": {
        # Navigation & Global Panels
        "brand_title": "🏡 PowerWise Malaysia",
        "brand_tagline": "Track Smarter. Save Bigger.",
        "sys_config": "🛠️ System Configuration",
        "select_lang": "Select Interface Language / Pilih Bahasa",
        "select_region": "Select Target Region Profile",
        "sync_lbl": "🔄 Connection Environment Simulator",
        "status_connected": "🟢 Connected (Cloud Real-Time Sync Active)",
        "status_offline": "🟡 Weak/No Signal (Offline-First Cache Active)",
        "app_status_conn": "App Status: Securely Connected to Core Utility Grid API Hub",
        "app_status_off": "App Status: Standalone Offline-First Mode (Data cached to local physical device storage)",
        # Tab Labels
        "tab_home": "🏠 Welcome Portal",
        "tab_scen1": "📱 Scenario 1: Aisyah (Urban Budget)",
        "tab_scen2": "📶 Scenario 2: Joseph (Rural Offline)",
        "tab_scen3": "🌿 Scenario 3: Hafiz (Appliance Hub)",
        # Welcome Page
        "welcome_hdr": "Welcome to PowerWise Malaysia",
        "welcome_desc": "Empowering households with real energy literacy, contextual tariff clarity, and data transparency across the Global South.",
        "tag_line_sub": "Our system bridges infrastructure gaps by providing multi-lingual support, offline durability, and plain-language financial tracking over technical jargon.",
        "meta_features": "✨ Core System Capabilities Demonstrated:",
        "feat1": "⚡ **True Bilingual Translation Engine:** Fully shifts core logic, alerts, and operational strings instantly.",
        "feat2": "🔋 **Offline-First Resilience Architecture:** Retains operations, mathematical calculators, and alerts when networks drop.",
        "feat3": "📊 **Plain Language Financial Translations:** Conversional alerts converting technical units ($kWh$) into local spending metrics ($RM$).",
        "feat4": "🎫 **Subsidy Integration:** Embedded calculations for current national green support mechanisms (e.g., SAVE 4.0).",
        # Scenario 1 (Aisyah)
        "s1_header": "Scenario 1 Walkthrough — Urban Budget & Actionable Alerts",
        "s1_meta": "**User Profile:** Aisyah — Working Mother, Primary Bill Payer, Moderate Digital Literacy, Urban KL, TNB Supply Tier.",
        "s1_goal": "**User Goal:** Detect and circumvent end-of-month bill shock by understanding why energy costs scale.",
        "s1_base_bill": "Last Month's Bill Reference Baseline: **RM 187**",
        "s1_alert_banner": "⚠️ BUDGET ALERT: Current Projected Cost is RM 224 (RM 37 above your RM 187 monthly baseline target).",
        "s1_btn_step2": "🔍 Analyze Root Cause & Breakdown",
        "s1_explanation": "Your active energy accumulation footprint this week is **23% higher** compared to the exact same week cycle last month. If your structural consumption pattern trends at this velocity, your final invoiced total is modeling towards **RM 224**.",
        "s1_cause_hdr": "🔍 Diagnosed Primary Cause Factor:",
        "s1_cause_desc": "Air Conditioner operations have scaled aggressively. Running your target system an average of **2 extra hours per day** adds approximately **+RM 12/month** under your active TNB sliding block structure.",
        "s1_btn_step3": "💡 What Can I Do? (View Recommendations)",
        "s1_recom_hdr": "📋 Ranked Action Tasks for Immediate Savings:",
        "s1_recom1": "💡 **Recommendation A:** Calibrate your AC thermostat set point to 25°C instead of 22°C — Projected savings: **~RM 8/month**.",
        "s1_recom2": "⏱️ **Recommendation B:** Initiate automated night sleep timers to cut idle cooling hours — Projected savings: **~RM 5/month**.",
        "s1_recom3": "🎫 **Recommendation C:** Verify active household allocation tracking clearance for a 5-Star efficiency appliance rebate voucher under the national SAVE 4.0 scheme.",
        "s1_btn_step4": "📤 Share Dashboard Summary with Family Chat",
        "s1_share_success": "✅ Broadcast Dispatched Successfully via Chat API Link Wrapper:",
        "s1_share_msg": "'Family Alert — Our household energy footprint is modeling towards RM 224 this cycle. Let's adjust AC targets to protect our RM 187 target budget limits!'",
        "s1_reset": "🔄 Reset Scenario Walkthrough Flow",
        # Scenario 2 (Joseph)
        "s2_header": "Scenario 2 Walkthrough — Offline Manual Logging & Structural Resilience",
        "s2_meta": "**User Profile:** Joseph — Rubber Smallholder, Rural Sabah, SESB Network, Intermittent Internet Infrastructure, Basic Digital Literacy.",
        "s2_goal": "**User Goal:** Accurately update consumption tracking metrics to manage household cash constraints without dependency on data access networks.",
        "s2_cached_warn": "⚠️ Storage Alert: Displaying locally cached records. Last background sync: 4 days ago.",
        "s2_form_hdr": "📝 Manual Paper Bill / Physical Meter Logging Form",
        "s2_f_amt": "Enter Physical Invoiced Bill Total (RM)",
        "s2_f_date": "Log Reading Entry Date",
        "s2_f_kwh": "Enter Logged Accumulation Units (kWh)",
        "s2_edge_err": "🚨 System Validation Flag: The input metric exceeds historical consumption parameters by >200%. Please re-examine physical meter interface dial elements for entry anomalies.",
        "s2_save_btn": "Commit Entry to Secure Device Cache Storage",
        "s2_save_success_off": "✅ Transaction Committed: Data cached locally on physical storage. Record scheduled for opportunistic synchronization upon data network re-acquisition.",
        "s2_save_success_on": "🚀 Network Active: Data directly processed and uploaded into remote databases.",
        "s2_chart_title": "📊 Regional Cost Compliance Tracking View (Last 4 Cycles)",
        "s2_status_good": "Your current ledger is RM 6 below your baseline allocation target. Operational footprint aligns with historical cycles. No anomalies identified.",
        # Scenario 3 (Hafiz)
        "s3_header": "Scenario 3 Walkthrough — Appliance Upgrade Selection Engine",
        "s3_meta": "**User Profile:** Hafiz — Civil Servant, Suburban Selangor, TNB Network Tier, Moderate-High Digital Literacy, 5 Resident Household.",
        "s3_goal": "User Goal: Compute clear ROI metric equations to determine if trading legacy infrastructure for 5-Star efficiency hardware creates real economic payback.",
        "s3_form_title": "🔧 Comparative Appliance ROI Calculation Engine",
        "s3_f_hours": "Estimated System Operational Run Duration (Hours/Day)",
        "s3_f_stars_curr": "Legacy Equipment Energy Rating",
        "s3_f_stars_new": "Proposed System Energy Rating Upgrade Selection",
        "s3_star0": "0 Stars / Legacy Non-Rated Unit",
        "s3_star5": "5 Stars / High-Efficiency Certified Unit",
        "s3_calc_btn": "Execute Financial Analytics Engine",
        "s3_result_hdr": "📉 Calculated Operational Baseline Projections (Monthly Cost Matrix)",
        "s3_lbl_curr": "Legacy Unit Monthly Running Expense",
        "s3_lbl_new": "5-Star System Monthly Running Expense",
        "s3_lbl_ann": "Net Annual Operational Savings Potential",
        "s3_tbl_metric": "Evaluation Parametric Metric",
        "s3_tbl_val": "Value (RM)",
        "s3_rebate_chk": "🎫 Evaluate Household National Subsidy Eligibility Clearance (SAVE 4.0)",
        "s3_rebate_pass": "🎉 Eligibility Approved! Your localized region, residential demographic parameters, and provider classification qualify your profile for an immediate RM 200 cash rebate voucher towards the targeted 5-Star acquisition.",
        "s3_payback_hdr": "⏱️ Capital Amortization & Investment Amortization Lifecycle Tracker",
        "s3_f_price": "Retail Acquisition Sticker Price (RM)",
        "s3_payback_res": "Analysis: Accounting for your instant RM 200 SAVE 4.0 rebate credit incentive, your net upfront hardware cost scales to RM {net_cost}. Your operational variance savings profile demonstrates full investment amortization in approximately {payback_yrs} years.",
    },
    "Bahasa Malaysia": {
        # Navigation & Global Panels
        "brand_title": "🏡 PowerWise Malaysia",
        "brand_tagline": "Jejak Bijak. Jimat Besar.",
        "sys_config": "🛠️ Konfigurasi Sistem",
        "select_lang": "Pilih Bahasa Antaramuka / Select Interface Language",
        "select_region": "Pilih Profil Wilayah Sasaran",
        "sync_lbl": "🔄 Simulator Persekitaran Sambungan",
        "status_connected": "🟢 Bersambung (Sinkronisasi Awan Sebenar Aktif)",
        "status_offline": "🟡 Isyarat Lemah (Mod Simpanan Luar Talian Aktif)",
        "app_status_conn": "Status Aplikasi: Bersambung Selamat ke Hab API Grid Utiliti Utama",
        "app_status_off": "Status Aplikasi: Mod Luar Talian Mandiri (Data disimpan dalam storan peranti fizikal)",
        # Tab Labels
        "tab_home": "🏠 Portal Utama",
        "tab_scen1": "📱 Senario 1: Aisyah (Belanjawan Bandar)",
        "tab_scen2": "📶 Senario 2: Joseph (Luar Talian)",
        "tab_scen3": "🌿 Senario 3: Hafiz (Hub Alatan Rumah)",
        # Welcome Page
        "welcome_hdr": "Selamat Datang ke PowerWise Malaysia",
        "welcome_desc": "Memperkasakan isi rumah dengan celik tenaga sebenar, kejelasan tarif mengikut konteks, dan ketelusan data di seluruh Global South.",
        "tag_line_sub": "Sistem kami merapatkan jurang infrastruktur dengan menyediakan sokongan pelbagai bahasa, ketahanan luar talian, dan penjejakan kewangan menggunakan bahasa mudah berbanding istilah teknikal yang rumit.",
        "meta_features": "✨ Keupayaan Teras Sistem Yang Ditunjukkan:",
        "feat1": "⚡ **Enjin Terjemahan Dwibahasa Sebenar:** Menukar keseluruhan logik teras, amaran, dan rentetan operasi serta-merta.",
        "feat2": "🔋 **Arsitektur Ketahanan Luar Talian:** Mengekalkan operasi, kalkulator matematik, dan amaran apabila rangkaian terputus.",
        "feat3": "📊 **Terjemahan Kewangan Bahasa Mudah:** Amaran perbualan menukar unit teknikal ($kWh$) kepada metrik perbelanjaan tempatan ($RM$).",
        "feat4": "🎫 **Integrasi Subsidi Kerajaan:** Pengiraan terbina untuk mekanisme sokongan hijau nasional semasa (cth., SAVE 4.0).",
        # Scenario 1 (Aisyah)
        "s1_header": "Walkthrough Senario 1 — Belanjawan Bandar & Amaran Boleh Bertindak",
        "s1_meta": "**Profil Pengguna:** Aisyah — Ibu bekerja, Pembayar Bil Utama, Celik Digital Sederhana, Bandar KL, Amaran Blok Tarif TNB.",
        "s1_goal": "**Matlamat Pengguna:** Mengesan dan mengelakkan kejutan bil akhir bulan dengan memahami punca peningkatan kos tenaga.",
        "s1_base_bill": "Garis Dasar Rujukan Bil Bulan Lepas: **RM 187**",
        "s1_alert_banner": "⚠️ AMARAN BELANJAWAN: Anggaran Kos Semasa adalah RM 224 (RM 37 melebihi sasaran belanjawan bulanan RM 187 anda).",
        "s1_btn_step2": "🔍 Analisis Punca Utama & Pecahan",
        "s1_explanation": "Jejak penggunaan tenaga aktif anda minggu ini adalah **23% lebih tinggi** berbanding kitaran minggu yang sama bulan lepas. Jika corak penggunaan semasa berterusan, jumlah akhir bil anda dianggarkan mencecah **RM 224**.",
        "s1_cause_hdr": "🔍 Punca Utama Yang Diidentifikasi:",
        "s1_cause_desc": "Operasi Penghawa Dingin meningkat secara drastik. Menjalankan sistem penghawa dingin anda secara purata **2 jam tambahan sehari** menambah kira-kira **+RM 12/bulan** di bawah struktur blok tarif TNB semasa anda.",
        "s1_btn_step3": "💡 Apa Yang Boleh Saya Lakukan? (Lihat Cadangan)",
        "s1_recom_hdr": "📋 Senarai Tindakan Mengikut Kedudukan untuk Penjimatan Segera:",
        "s1_recom1": "💡 **Cadangan A:** Tetapkan suhu penghawa dingin anda kepada 25°C berbanding 22°C — Anggaran penjimatan: **~RM 8/sebulan**.",
        "s1_recom2": "⏱️ **Cadangan B:** Aktifkan pemasa tidur malam automatik untuk mengurangkan pembaziran masa penyejukan — Anggaran penjimatan: **~RM 5/sebulan**.",
        "s1_recom3": "🎫 **Cadangan C:** Semak kelayakan profil isi rumah anda untuk mendapatkan rebat baucar alatan cekap bertenaga 5-Bintang di bawah skim SAVE 4.0 nasional.",
        "s1_btn_step4": "📤 Kongsi Ringkasan Papan Pemuka ke Sembang Keluarga",
        "s1_share_success": "✅ Hebahan Berjaya Dihantar melalui Pautan API Sembang Wrapper:",
        "s1_share_msg": "'Amaran Keluarga — Penggunaan tenaga rumah kita dianggarkan mencecah RM 224 kitaran ini. Mari selaraskan penggunaan AC untuk mengekalkan had belanjawan RM 187 kita!'",
        "s1_reset": "🔄 Set Semula Aliran Senario Walkthrough",
        # Scenario 2 (Joseph)
        "s2_header": "Walkthrough Senario 2 — Log Manual Luar Talian & Ketahanan Struktur",
        "s2_meta": "**Profil Pengguna:** Joseph — Pekebun Kecil Getah, Luar Bandar Sabah, Rangkaian SESB, Capaian Internet Terputus, Celik Digital Asas.",
        "s2_goal": "**Matlamat Pengguna:** Mengemas kini metrik penjejakan penggunaan secara tepat untuk menguruskan kekangan tunai isi rumah tanpa bergantung kepada internet.",
        "s2_cached_warn": "⚠️ Amaran Storan: Memaparkan rekod disimpan dalam memori peranti. Sinkronisasi latar belakang terakhir: 4 hari lepas.",
        "s2_form_hdr": "📝 Borang Log Manual Bil Kertas / Meter Fizikal",
        "s2_f_amt": "Masukkan Jumlah Bil Fizikal (RM)",
        "s2_f_date": "Tarikh Rekod Log Dimasukkan",
        "s2_f_kwh": "Masukkan Unit Penggunaan Meter (kWh)",
        "s2_edge_err": "🚨 Isyarat Validasi Sistem: Metrik yang dimasukkan melebihi parameter penggunaan sejarah sebanyak >200%. Sila semak semula nombor pada meter fizikal anda untuk mengelakkan ralat.",
        "s2_save_btn": "Simpan Rekod ke Dalam Storan Memori Peranti",
        "s2_save_success_off": "✅ Transaksi Berjaya: Data disimpan dengan selamat dalam memori peranti. Rekod dijadualkan untuk sinkronisasi automatik apabila isyarat rangkaian pulih kembali.",
        "s2_save_success_on": "🚀 Rangkaian Aktif: Data diproses dan dimuat naik secara terus ke pangkalan data awan.",
        "s2_chart_title": "📊 Paparan Pematuhan Kos Wilayah (4 Kitaran Terakhir)",
        "s2_status_good": "Baki penggunaan anda adalah RM 6 di bawah sasaran had bulanan. Profil operasi sejajar dengan kitaran sejarah. Tiada anomali dikesan.",
        # Scenario 3 (Hafiz)
        "s3_header": "Walkthrough Senario 3 — Enjin Pemilihan Penarafan Alatan Elektrik",
        "s3_meta": "**Profil Pengguna:** Hafiz — Penjawat Awam, Pinggir Bandar Selangor, Profil TNB, Celik Digital Sederhana-Tinggi, Isi Rumah 5 Penduduk.",
        "s3_goal": "Matlamat Pengguna: Mengira metrik pulangan pelaburan (ROI) yang jelas untuk menentukan sama ada menukar perkakasan lama kepada model cekap bertenaga 5-Bintang memberikan penjimatan ekonomi sebenar.",
        "s3_form_title": "🔧 Enjin Pengiraan Perbandingan ROI Alatan Elektrik",
        "s3_f_hours": "Anggaran Tempoh Operasi Sistem (Jam/Hari)",
        "s3_f_stars_curr": "Penarafan Tenaga Peralatan Sedia Ada",
        "s3_f_stars_new": "Pilihan Peningkatan Penarafan Tenaga Sistem Baru",
        "s3_star0": "0 Bintang / Unit Lama Tiada Penarafan",
        "s3_star5": "5 Bintang / Unit Diiktiraf Kecekapan Tinggi",
        "s3_calc_btn": "Jalankan Enjin Analisis Kewangan",
        "s3_result_hdr": "📉 Unjuran Kos Operasi Bulanan Projections (Matrik Kos Bulanan)",
        "s3_lbl_curr": "Perbelanjaan Bulanan Unit Lama",
        "s3_lbl_new": "Perbelanjaan Bulanan Sistem 5-Bintang",
        "s3_lbl_ann": "Potensi Penjimatan Operasi Bersih Tahunan",
        "s3_tbl_metric": "Metrik Parameter Penilaian",
        "s3_tbl_val": "Nilai (RM)",
        "s3_rebate_chk": "🎫 Nilai Kelayakan Pelepasan Subsidi Nasional Isi Rumah (SAVE 4.0)",
        "s3_rebate_pass": "🎉 Kelayakan Diluluskan! Parameter wilayah tempatan, demografi kediaman, dan klasifikasi pembekal anda melayakkan profil anda untuk menerima rebat tunai RM 200 serta-merta bagi pembelian unit 5-Bintang sasaran.",
        "s3_payback_hdr": "⏱️ Penjejak Kitaran Hayat Amortisasi Pelaburan Modal",
        "s3_f_price": "Harga Jualan Peralatan Baru (RM)",
        "s3_payback_res": "Analisis: Mengambil kira insentif kredit rebat SAVE 4.0 sebanyak RM 200, kos perkakasan bersih anda ialah RM {net_cost}. Profil penjimatan varians operasi anda menunjukkan pemulihan modal pelaburan sepenuhnya dalam tempoh kira-kira {payback_yrs} tahun.",
    },
}

# ----------------------------------------------------
# 4. CONTROL INTERFACE SIDEBAR CONTROL LAYER
# ----------------------------------------------------
st.sidebar.markdown(
    "<h2 style='color:#1E3A8A;'>⚡ PowerWise Hub</h2>", unsafe_allow_html=True
)

# Main Language Control Selector Switch
selected_lang = st.sidebar.selectbox(
    "🌐 Language / Bahasa", ["English", "Bahasa Malaysia"]
)
tx = CONTENT_DICTIONARY[selected_lang]  # Runtime Context Variable Assignment

st.sidebar.divider()
st.sidebar.subheader(tx["sys_config"])

# Regional Framework Strategy Rules Setup Selection
selected_region = st.sidebar.selectbox(
    tx["select_region"], ["TNB (Peninsular Malaysia)", "SESB (Sabah)", "SEB (Sarawak)"]
)

# Interactive Signal Environment Simulator Selector
st.sidebar.markdown(f"**{tx['sync_lbl']}**")
network_simulation = st.sidebar.radio(
    "Toggle Device Environment State:", [tx["status_connected"], tx["status_offline"]]
)

st.sidebar.divider()
st.sidebar.caption(
    "PowerWise Group 22 High-Fidelity ICT Global South Interface Simulator Instance."
)

# Global Connectivity Banner Update
if tx["status_connected"] in network_simulation:
    st.success(tx["app_status_conn"])
else:
    st.warning(tx["app_status_off"])

# ----------------------------------------------------
# 5. HIGH-COMPATIBILITY COMPONENT STICKY PILLED NAVIGATION
# ----------------------------------------------------
tab_list = [tx["tab_home"], tx["tab_scen1"], tx["tab_scen2"], tx["tab_scen3"]]


# High-compatibility callback handler to safely track selected section indexes
def on_tab_change():
    st.session_state.active_tab_index = tab_list.index(
        st.session_state.selected_navigation_tab
    )


# Render a beautiful horizontal menu bar that maps perfectly to session states across all versions
selected_tab_label = st.radio(
    label="Portal Navigation:",
    options=tab_list,
    index=st.session_state.active_tab_index,
    key="selected_navigation_tab",
    on_change=on_tab_change,
    label_visibility="collapsed",
)
st.write("")  # Layout breathing room spacer

# ====================================================
# COMPATIBILITY ROUTER WIRES — CONDITIONALLY RENDER SECTIONS
# ====================================================

# ====================================================
# HOME PORTAL SECTION
# ====================================================
if st.session_state.active_tab_index == 0:
    st.markdown(
        f"<h1 class='main-title'>{tx['brand_title']}</h1>", unsafe_allow_html=True
    )
    st.markdown(f"🔬 *{tx['brand_tagline']}*")
    st.divider()

    st.subheader(tx["welcome_hdr"])
    st.write(tx["welcome_desc"])
    st.write(tx["tag_line_sub"])
    st.markdown(f"#### {tx['meta_features']}")
    st.write(tx["feat1"])
    st.write(tx["feat2"])
    st.write(tx["feat3"])
    st.write(tx["feat4"])

# ====================================================
# SCENARIO 1 SECTION — AISYAH STATE MACHINE
# ====================================================
elif st.session_state.active_tab_index == 1:
    st.header(tx["s1_header"])
    st.caption(tx["s1_meta"])
    st.caption(tx["s1_goal"])
    st.divider()

    # Render Dashboard Baseline Load View
    st.markdown(
        f"<div class='metric-card'>{tx['s1_base_bill']}</div>", unsafe_allow_html=True
    )
    st.write("")
    st.error(tx["s1_alert_banner"])

    # Step 2 Control Matrix Action Event
    if st.session_state.s1_step >= 1:
        if st.button(tx["s1_btn_step2"], key="s1_trig_s2"):
            st.session_state.s1_step = 2
            st.rerun()

    if st.session_state.s1_step >= 2:
        st.info(tx["s1_explanation"])
        st.markdown(f"#### {tx['s1_cause_hdr']}")
        st.write(tx["s1_cause_desc"])

        # Step 3 Control Matrix Action Event
        if st.session_state.s1_step == 2:
            if st.button(tx["s1_btn_step3"], key="s1_trig_s3"):
                st.session_state.s1_step = 3
                st.rerun()

    if st.session_state.s1_step >= 3:
        st.write("")
        st.markdown(f"### {tx['s1_recom_hdr']}")
        st.info(f"{tx['s1_recom1']}\n\n{tx['s1_recom2']}\n\n{tx['s1_recom3']}")

        # Step 4 Control Matrix Action Event
        if st.session_state.s1_step == 3:
            if st.button(tx["s1_btn_step4"], key="s1_trig_s4"):
                st.session_state.s1_step = 4
                st.rerun()

    if st.session_state.s1_step >= 4:
        st.success(f"{tx['s1_share_success']}\n\n*\"{tx['s1_share_msg']}\"*")

        # Clear/Reset Flow Component
        if st.button(tx["s1_reset"], key="s1_flow_reset"):
            st.session_state.s1_step = 1
            st.rerun()

# ====================================================
# SCENARIO 2 SECTION — JOSEPH (OFFLINE MANUAL ENTRY)
# ====================================================
elif st.session_state.active_tab_index == 2:
    st.header(tx["s2_header"])
    st.caption(tx["s2_meta"])
    st.caption(tx["s2_goal"])
    st.divider()

    # Structural Network Indicator Handling
    if tx["status_offline"] in network_simulation:
        st.warning(tx["s2_cached_warn"])

    st.subheader(tx["s2_form_hdr"])

    col1, col2 = st.columns(2)
    with col1:
        bill_amt = st.number_input(
            tx["s2_f_amt"],
            min_value=0.0,
            value=st.session_state.bill_input_value,
            key="s2_input_bill",
        )
        reading_date = st.date_input(tx["s2_f_date"], key="s2_input_date")
    with col2:
        kwh_amt = st.number_input(
            tx["s2_f_kwh"],
            min_value=0.0,
            value=st.session_state.kwh_input_value,
            key="s2_input_kwh",
        )
        st.text_input(
            "Active System Scope Provider Match",
            value=selected_region,
            disabled=True,
            key="s2_disabled_reg",
        )

    # EDGE CASE HANDLER: Anti-Misuse Input Volatility Validation Check
    if kwh_amt > 1500.0:
        st.error(tx["s2_edge_err"])

    if st.button(tx["s2_save_btn"], key="s2_execute_save"):
        st.session_state.kwh_input_value = kwh_amt
        st.session_state.bill_input_value = bill_amt
        st.session_state.scen2_saved = True
        st.rerun()

    # Conditional Live Generation Metric Data Rendering
    if st.session_state.scen2_saved:
        st.divider()
        st.subheader(tx["s2_chart_title"])

        chart_metrics = [48.0, 52.0, 50.0, st.session_state.bill_input_value]
        chart_dataframe = pd.DataFrame(
            chart_metrics,
            index=["Month -3", "Month -2", "Month -1", "Current Invoiced"],
            columns=["RM"],
        )
        st.bar_chart(chart_dataframe)

        st.success(tx["s2_status_good"])

# ====================================================
# SCENARIO 3 SECTION — HAFIZ (APPLIANCE UPGRADE REBATE ENGINE)
# ====================================================
elif st.session_state.active_tab_index == 3:
    st.header(tx["s3_header"])
    st.caption(tx["s3_meta"])
    st.divider()

    st.subheader(tx["s3_form_title"])

    c1, c2 = st.columns(2)
    with c1:
        usage_hours = st.slider(tx["s3_f_hours"], 1, 24, 8, key="s3_input_hours")
        current_stars = st.selectbox(
            tx["s3_f_stars_curr"], [tx["s3_star0"]], key="s3_input_curr_stars"
        )
    with c2:
        target_stars = st.selectbox(
            tx["s3_f_stars_new"], [tx["s3_star5"]], key="s3_input_target_stars"
        )
        hardware_sticker_price = st.number_input(
            tx["s3_f_price"],
            min_value=100.0,
            value=1800.0,
            step=50.0,
            key="s3_input_price",
        )

    if st.button(tx["s3_calc_btn"], key="s3_execute_calc"):
        st.session_state.s3_calculated = True
        st.rerun()

    if st.session_state.s3_calculated:
        # Dynamic math calculations adjusted to match input slider values instantly
        legacy_cost_estimation = 62.0 * (usage_hours / 8.0)
        optimized_cost_estimation = 39.0 * (usage_hours / 8.0)
        variance_net_annual_delta = (
            legacy_cost_estimation - optimized_cost_estimation
        ) * 12.0

        st.markdown(f"### {tx['s3_result_hdr']}")

        # Completely bilingual-adapted data matrix headers
        res_data = {
            tx["s3_tbl_metric"]: [
                tx["s3_lbl_curr"],
                tx["s3_lbl_new"],
                tx["s3_lbl_ann"],
            ],
            tx["s3_tbl_val"]: [
                f"RM {legacy_cost_estimation:.2f}",
                f"RM {optimized_cost_estimation:.2f}",
                f"RM {variance_net_annual_delta:.2f}",
            ],
        }
        st.table(pd.DataFrame(res_data))

        st.divider()
        st.markdown(f"### {tx['s3_rebate_chk']}")
        st.success(tx["s3_rebate_pass"])

        st.divider()
        st.markdown(f"### {tx['s3_payback_hdr']}")

        net_hardware_investment = hardware_sticker_price - 200.0
        monthly_variance_savings = legacy_cost_estimation - optimized_cost_estimation
        payback_years_lifecycle = (
            net_hardware_investment / (monthly_variance_savings * 12.0)
            if monthly_variance_savings > 0
            else 0
        )

        st.info(
            tx["s3_payback_res"].format(
                net_cost=int(net_hardware_investment),
                payback_yrs=round(payback_years_lifecycle, 1),
            )
        )
