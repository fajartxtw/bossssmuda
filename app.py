"""
🚀 bosssmuda — Dashboard Kepemilikan Saham IDX
================================================
Entry point utama (modular, high-density UI).
Jalankan: streamlit run app.py
"""

import streamlit as st

# =============================================
# KONFIGURASI HALAMAN
# =============================================
st.set_page_config(
    page_title="bosssmuda | Kepemilikan Saham IDX",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# IMPORTS
# =============================================
from ui.login_page import show_login_page
from ui.landing_page import show_landing_page
from ui.styles import inject_dashboard_css
from ui.components import render_metric_cards, render_sidebar, render_locked_page
from core.data_loader import muat_data, format_angka
from views.tab_emiten import render_tab_emiten
from views.tab_investor import render_tab_investor
from views.tab_ranking import render_tab_ranking
from views.tab_network import render_tab_network
from views.tab_market import render_tab_market
from views.tab_export import render_tab_export
from core.market_overview import render_market_overview
from views.tab_ai_chat import render_tab_ai_chat
from core.auth import is_page_allowed

# =============================================
# AUTH GATE: Landing → Login → Dashboard
# =============================================
if not st.session_state.get('authenticated', False):
    if st.session_state.get('show_login', False):
        show_login_page()
    else:
        show_landing_page()
    st.stop()

# =============================================
# DASHBOARD (authenticated users only)
# =============================================

# Inject CSS
inject_dashboard_css()

# Custom Navbar (collapsible sidebar + page selector)
selected_page = render_sidebar()

# Load data dari Google Sheets
with st.spinner("⏳ Memuat data dari Google Sheets..."):
    df = muat_data()

if df is None:
    st.stop()

# =============================================
# OVERVIEW METRICS (compact)
# =============================================
total_emiten = df['KODE'].nunique() if 'KODE' in df.columns else 0
total_investor = df['INVESTOR'].nunique() if 'INVESTOR' in df.columns else 0
total_baris = len(df)
total_lokal = df[df['L/F'].str.upper().isin(['L', 'LOKAL', 'LOCAL'])].shape[0] if 'L/F' in df.columns else 0
# Hitung Asing dari kolom ASAL (NATIONALITY): "A" = Asing, selain "INDONESIAN" = Asing
if 'ASAL' in df.columns:
    asal_upper = df['ASAL'].fillna('').astype(str).str.strip().str.upper()
    total_asing = df[
        (asal_upper == 'A') |
        ((asal_upper != '') & (~asal_upper.isin(['INDONESIAN', 'INDONESIA'])))
    ].shape[0]
else:
    total_asing = df[df['L/F'].str.upper().isin(['F', 'ASING', 'FOREIGN'])].shape[0] if 'L/F' in df.columns else 0

render_metric_cards([
    {"icon": "🏢", "value": format_angka(total_emiten), "label": "Emiten"},
    {"icon": "👤", "value": format_angka(total_investor), "label": "Investor"},
    {"icon": "📋", "value": format_angka(total_baris), "label": "Records"},
    {"icon": "🇮🇩", "value": format_angka(total_lokal), "label": "Lokal"},
    {"icon": "🌍", "value": format_angka(total_asing), "label": "Asing"},
])

# RENDER REAL-TIME MARKET OVERVIEW
render_market_overview()

st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# =============================================
# PAGE CONTENT — Role-based access control
# =============================================
daftar_kode = sorted(df['KODE'].unique().tolist()) if 'KODE' in df.columns else []
current_user = st.session_state.get('username', 'unknown')

if selected_page == "🔍 Stock Screener":
    render_tab_emiten(df, daftar_kode)
elif selected_page == "👤 Investor Screener":
    render_tab_investor(df)
elif selected_page == "🏆 Rankings":
    render_tab_ranking(df)
elif selected_page == "🕸️ Network Graph":
    render_tab_network(df, daftar_kode)
elif selected_page == "📈 Market Data":
    if is_page_allowed(current_user, selected_page):
        render_tab_market(df, daftar_kode)
    else:
        render_locked_page("Market Data")
elif selected_page == "📊 Statistik & Event":
    if is_page_allowed(current_user, selected_page):
        from views.tab_statistik import render_tab_statistik
        render_tab_statistik()
    else:
        render_locked_page("Statistik & Event")
elif selected_page == "📰 Berita Pasar":
    if is_page_allowed(current_user, selected_page):
        from views.tab_news import render_tab_news
        render_tab_news()
    else:
        render_locked_page("Berita Pasar")
elif selected_page == "📄 PDF Export":
    if is_page_allowed(current_user, selected_page):
        render_tab_export(df, daftar_kode)
    else:
        render_locked_page("PDF Export")
elif selected_page == "🤖 AI Assistant":
    if is_page_allowed(current_user, selected_page):
        render_tab_ai_chat()
    else:
        render_locked_page("AI Assistant")

# =============================================
# FOOTER (compact)
# =============================================
st.markdown("""
<div style="text-align: center; padding: 0.8rem 0 0.5rem; margin-top: 1rem; border-top: 1px solid rgba(139,92,246,0.1);">
    <p style="color: #64748b; font-size: 0.7rem; margin: 0;">
        bosssmuda &nbsp;•&nbsp; Built with Python, Streamlit & Plotly
    </p>
    <p style="color: #475569; font-size: 0.6rem; margin-top: 0.2rem;">
        Data bersumber dari KSEI & tersinkronisasi via Google Sheets
    </p>
</div>
""", unsafe_allow_html=True)
