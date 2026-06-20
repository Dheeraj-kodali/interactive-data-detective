import streamlit as st

# Configure Streamlit page layout and metadata
st.set_page_config(
    page_title="Data Detective - Explore & Analyze Datasets",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modular components
from components.sidebar import render_sidebar
from components.stats_cards import render_stats_cards
from components.dataset_preview import render_dataset_preview

# Inject unified SaaS design system
from utils.styling import inject_global_css
inject_global_css()

# Render Sidebar Module
render_sidebar()

# Page Navigation (integrated in Python sidebar)
current_page = "📊 Explorer Dashboard"
if 'df' not in st.session_state:
    st.session_state.df = None

if st.session_state.df is not None:
    st.sidebar.markdown('<hr style="border-color: rgba(255, 255, 255, 0.05); margin: 15px 0;" />', unsafe_allow_html=True)
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 5px;">🧭 Navigator</div>', unsafe_allow_html=True)
    current_page = st.sidebar.radio(
        "Navigator",
        ["🧬 Dataset DNA Profile", "📈 Executive Dashboard", "📊 Explorer Dashboard", "🗺️ Semantic Data Map", "⏳ Timeline Intelligence", "🔍 Segment Discovery", "⚠️ Anomaly Detection", "🔗 Correlation Discovery", "🕵️ Investigation Console"],
        key="navigation_radio",
        label_visibility="collapsed"
    )

# Main Application Logic
if st.session_state.df is None:
    # ------------------ LANDING PAGE VIEW ------------------
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 60px 40px;">
            <span style="display: inline-block; background: rgba(56, 189, 248, 0.1); color: #38bdf8; font-size: 0.75rem; font-weight: 700; padding: 5px 15px; border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.05em;">🕵️‍♂️ Interactive Investigation Engine</span>
            <h1 class="text-gradient-light" style="font-size: 3rem; margin: 0 0 16px 0;">Unlock Insights in Your Datasets</h1>
            <p style="font-size: 1.1rem; color: #94a3b8; max-width: 650px; margin: 0 auto; line-height: 1.6;">
                Data Detective helps you import, inspect, and analyze tabular records. 
                Explore statistical metrics, structural types, missingness reports, and correlation models instantly.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="section-title">How to Start Investigating</div>', unsafe_allow_html=True)
    
    # Grid container for features and quickstart steps
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #38bdf8;">📂</div>
            <h4 style="margin:0; font-size: 1.1rem; color: #f8fafc;">1. Upload File</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 8px 0 0 0;">Drop your CSV/Excel spreadsheet into the sidebar upload box.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #a78bfa;">🚀</div>
            <h4 style="margin:0; font-size: 1.1rem; color: #f8fafc;">2. Or Try Sample</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 8px 0 0 0;">Click 'Load Sample Dataset' to explore a generated E-commerce dataset.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #10b981;">📊</div>
            <h4 style="margin:0; font-size: 1.1rem; color: #f8fafc;">3. Audit Health</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 8px 0 0 0;">Examine row counts, duplicate entries, and completeness automatically.</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #f43f5e;">🔗</div>
            <h4 style="margin:0; font-size: 1.1rem; color: #f8fafc;">4. Find Patterns</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 8px 0 0 0;">Inspect interactive correlation networks and discover hidden segments.</p>
        </div>
        """, unsafe_allow_html=True)
    
elif current_page == "🧬 Dataset DNA Profile":
    # ------------------ DATASET DNA VIEW ------------------
    from components.dna_dashboard import show_dna_dashboard_page
    show_dna_dashboard_page(is_standalone=False)

elif current_page == "📈 Executive Dashboard":
    # ------------------ EXECUTIVE DASHBOARD VIEW ------------------
    from pages.dashboard import show_dashboard_page
    show_dashboard_page(is_standalone=False)

elif current_page == "🗺️ Semantic Data Map":
    # ------------------ SEMANTIC DATA MAP VIEW ------------------
    from pages.data_map import show_data_map_page
    show_data_map_page(is_standalone=False)
    
elif current_page == "⏳ Timeline Intelligence":
    # ------------------ TIMELINE INTELLIGENCE VIEW ------------------
    from pages.timeline_analysis import show_timeline_page
    show_timeline_page(is_standalone=False)
    
elif current_page == "🔍 Segment Discovery":
    # ------------------ SEGMENT DISCOVERY VIEW ------------------
    from pages.segments import show_segments_page
    show_segments_page(is_standalone=False)
    
elif current_page == "⚠️ Anomaly Detection":
    # ------------------ ANOMALY DETECTION VIEW ------------------
    from pages.anomalies import show_anomalies_page
    show_anomalies_page(is_standalone=False)
    
elif current_page == "🔗 Correlation Discovery":
    # ------------------ CORRELATION DISCOVERY VIEW ------------------
    from pages.correlations import show_correlations_page
    show_correlations_page(is_standalone=False)
    
elif current_page == "🕵️ Investigation Console":
    # ------------------ INVESTIGATION CONSOLE VIEW ------------------
    from pages.investigation_console import show_investigation_console_page
    show_investigation_console_page(is_standalone=False)

    
else:
    # ------------------ DASHBOARD VIEW ------------------
    # Render premium metrics cards grid at the top
    render_stats_cards(st.session_state.df)
    
    # Render dataset interactive previews and plots
    render_dataset_preview(st.session_state.df)
