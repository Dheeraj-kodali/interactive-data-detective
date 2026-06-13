import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard_page(is_standalone=False):
    """
    Renders the Executive Insight Dashboard page.
    Displays dynamic top-level summary metrics from across the modules.
    """
    if is_standalone:
        st.set_page_config(
            page_title="Data Detective - Executive Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    # 1. State Check: Verify if dataset is loaded
    if 'df' not in st.session_state or st.session_state.df is None:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">📈</div>
                <h2 style="color: #f8fafc; font-weight: 700; margin-bottom: 10px;">Executive Dashboard</h2>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 500px; margin: 0 auto 25px auto; line-height: 1.6;">
                    Upload a dataset to view high-level statistical insights.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if is_standalone:
            st.page_link("app.py", label="Return to Case Upload", icon="🏠", use_container_width=True)
        return

    from components.insight_cards import inject_insight_css, render_metric_card, render_insight_sentence, generate_insights
    from components.investigation_timeline import render_timeline
    from components.dataset_profile_card import render_dataset_profile
    from components.recommendation_cards import render_recommendation_cards
    from components.report_download import render_report_download
    from utils.timeline_tracker import record_timeline_event
    from analytics.correlation_engine import mine_correlations
    import logging
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info(f"Dashboard loaded. Session state keys: {list(st.session_state.keys())}")
    logger.info(f"Data availability - Segments: {'segment_results' in st.session_state}, Anomalies: {'anomaly_results' in st.session_state}")
    
    df = st.session_state.df
    inject_insight_css()
    
    # Hero Header
    st.markdown(
        """
        <div class="glass-card">
            <h1 class="text-gradient-light" style="margin: 0; font-size: 2.2rem;">Executive Summary</h1>
            <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.95rem;">High-level analytical findings, statistical anomalies, and dominant clusters identified in the current case file.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render Dataset Profiler
    render_dataset_profile(df)
    
    # Render Analytical Recommendations
    render_recommendation_cards(df)
    
    # Attempt to calculate basic correlation findings on the fly for the dashboard
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    ranked_rels = []
    if len(numeric_cols) >= 2:
        # Run silently, limit to top 15 numeric columns to keep dashboard fast
        top_cols = numeric_cols[:15]
        try:
            ranked_rels, _, _ = mine_correlations(df, top_cols)
        except Exception:
            ranked_rels = []

    # ==========================
    # ROW 1: Dataset & Anomalies
    # ==========================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">🩺 Dataset Health</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card("Total Rows", f"{len(df):,}", "📋", "#38bdf8")
        with m2:
            render_metric_card("Features", f"{len(df.columns):,}", "🧬", "#a78bfa")
        with m3:
            missing_pct = (df.isna().sum().sum() / df.size) * 100
            color = "#ef4444" if missing_pct > 5 else "#10b981"
            render_metric_card("Missing Data", f"{missing_pct:.1f}%", "🧩", color)
            
    with col2:
        st.markdown('<div class="section-title">⚠️ Anomaly Summary</div>', unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        
        # Read from decoupled session state
        anomaly_res = st.session_state.get('anomaly_results')
        
        if anomaly_res:
            with a1:
                render_metric_card("Anomalies Found", f"{anomaly_res['total_anomalies']:,}", "🚨", "#ef4444")
            with a2:
                render_metric_card("Highest Score", f"{anomaly_res['max_score']:.3f}", "🎯", "#f59e0b")
        else:
            with a1:
                render_metric_card("Anomalies Found", "N/A", "🚨", "#64748b")
            with a2:
                render_metric_card("Highest Score", "N/A", "🎯", "#64748b")
            st.caption("Run Anomaly Detection on the respective page to generate scores.")

    # ==========================
    # ROW 2: Segments & Correlations
    # ==========================
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="section-title">🔍 Segment Summary</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        
        # Read from decoupled session state
        segment_res = st.session_state.get('segment_results')
        
        if segment_res:
            with s1:
                render_metric_card("Total Segments", f"{segment_res['unique_clusters']}", "🧩", "#10b981")
            with s2:
                render_metric_card("Largest Segment", f"{segment_res['largest_cluster']}", "👑", "#3b82f6")
        else:
            with s1:
                render_metric_card("Total Segments", "N/A", "🧩", "#64748b")
            with s2:
                render_metric_card("Largest Segment", "N/A", "👑", "#64748b")
            st.caption("Run Segment Discovery to assign cluster labels.")

    with col4:
        st.markdown('<div class="section-title">🔗 Correlation Summary</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        pos_linear = [r for r in ranked_rels if not pd.isna(r['pearson']) and r['pearson'] >= 0.5]
        neg_linear = [r for r in ranked_rels if not pd.isna(r['pearson']) and r['pearson'] <= -0.5]
        
        if pos_linear:
            top_pos = pos_linear[0]
            with c1:
                render_metric_card("Top Positive", f"{top_pos['var1']} / {top_pos['var2']}", "🟢", "#10b981")
        else:
            with c1:
                render_metric_card("Top Positive", "None", "🟢", "#64748b")
                
        if neg_linear:
            top_neg = sorted(neg_linear, key=lambda x: x['pearson'])[0]
            with c2:
                render_metric_card("Top Negative", f"{top_neg['var1']} / {top_neg['var2']}", "🔴", "#ef4444")
        else:
            with c2:
                render_metric_card("Top Negative", "None", "🔴", "#64748b")

    # ==========================
    # KEY FINDINGS & TIMELINE
    # ==========================
    st.markdown('<div class="section-title">💡 Automated Key Findings</div>', unsafe_allow_html=True)
    
    col_find, col_time = st.columns([2, 1])
    
    with col_find:
        insights = generate_insights(df, ranked_rels)
        record_timeline_event("Findings Generated", f"({len(insights)} insights)")
        
        for item in insights:
            render_insight_sentence(item['text'], item['icon'], item['color'])
            
    with col_time:
        st.markdown('<h4 style="color: #f8fafc; font-weight: 700; margin-top: 0;">Case Progress</h4>', unsafe_allow_html=True)
        render_timeline()
        render_report_download(df)

if __name__ == "__main__":
    show_dashboard_page(is_standalone=True)
