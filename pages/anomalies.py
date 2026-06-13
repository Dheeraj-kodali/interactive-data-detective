import streamlit as st
import pandas as pd
import numpy as np

def show_anomalies_page(is_standalone=False):
    """
    Renders the Anomaly Detection page.
    Manages parameters, triggers Isolation Forest, and displays dashboards.
    """
    if is_standalone:
        st.set_page_config(
            page_title="Data Detective - Anomaly Detection",
            page_icon="🕵️‍♂️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        # CSS Styling matching global dark slate look
        st.markdown(
            """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
                html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                    background-color: #0b0f19 !important;
                    color: #e2e8f0 !important;
                }
                [data-testid="stSidebar"] {
                    background-color: #0f172a !important;
                    border-right: 1px solid rgba(255, 255, 255, 0.05);
                }
                .glass-card {
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.75) 100%);
                    border: 1px solid rgba(56, 189, 248, 0.12);
                    border-radius: 16px;
                    padding: 24px;
                    margin-bottom: 25px;
                    backdrop-filter: blur(15px);
                    -webkit-backdrop-filter: blur(15px);
                }
                .text-gradient-primary {
                    background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800;
                }
                .section-title {
                    font-size: 1.25rem;
                    font-weight: 700;
                    color: #f8fafc;
                    margin-top: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #38bdf8;
                    padding-left: 12px;
                    letter-spacing: -0.01em;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

    # 1. State Check: Verify if dataset is loaded
    if 'df' not in st.session_state or st.session_state.df is None:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; margin-top: 50px; border-color: rgba(244, 63, 94, 0.2);">
                <div style="font-size: 3rem; margin-bottom: 15px;">🕵️‍♂️</div>
                <h2 style="color: #f8fafc; font-weight: 700; margin-bottom: 10px;">Case File Unassigned</h2>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 500px; margin: 0 auto 25px auto; line-height: 1.6;">
                    Anomaly Detection requires an active dataset. 
                    Please return to the homepage to upload a CSV/Excel file or load the simulation dataset.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if is_standalone:
            st.page_link("app.py", label="Return to Case Upload", icon="🏠", use_container_width=True)
        return

    # Import analytical engine and dashboard module
    from analytics.anomaly_detection import calculate_anomalies
    from components.anomaly_dashboard import render_anomaly_dashboard
    
    df = st.session_state.df
    
    # 2. Sidebar Parameters
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
            <div style="font-size: 1.8rem; margin-bottom: 3px;">⚠️</div>
            <h2 class="text-gradient-primary" style="margin: 0; font-size: 1.25rem;">ANOMALIES</h2>
        </div>
        <hr style="border-color: rgba(255, 255, 255, 0.05); margin-top: 0; margin-bottom: 15px;" />
        """,
        unsafe_allow_html=True
    )
    
    # Contamination Slider (Expected ratio of outliers)
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 2px;">📈 Contamination Rate</div>', unsafe_allow_html=True)
    contamination = st.sidebar.slider(
        "Contamination Rate",
        min_value=0.01,
        max_value=0.20,
        value=0.05,
        step=0.01,
        key="anomaly_contamination_slider",
        label_visibility="collapsed"
    )
    
    # Feature selector multiselect
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 5px;">🧬 Columns to Analyze</div>', unsafe_allow_html=True)
    selected_cols = st.sidebar.multiselect(
        "Columns to Analyze",
        options=df.columns.tolist(),
        default=numeric_cols,
        key="anomaly_features_multiselect",
        label_visibility="collapsed"
    )
    
    # Anomaly Filtering Control
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 5px;">🧹 Filter Dataset View</div>', unsafe_allow_html=True)
    filter_mode = st.sidebar.selectbox(
        "Filter Dataset View",
        options=["Show All Records", "Show Anomalies Only", "Show Normal Records Only"],
        key="anomaly_filter_selectbox",
        label_visibility="collapsed"
    )
    
    # 3. Main Header
    st.markdown(
        """
        <div class="glass-card">
            <h2 class="text-gradient-primary" style="margin-top: 0;">Outlier & Anomaly Detection</h2>
            <p style="color: #94a3b8; line-height: 1.5; margin: 0;">
                This module uses machine learning to identify data points that deviate significantly from the norm.
                These "anomalies" could be errors, fraud, or highly unique events requiring the detective's attention.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 4. Trigger calculations
    if not selected_cols:
        st.warning("⚠️ Please select at least one feature in the sidebar to run the anomaly detection.")
    else:
        labels, scores, error_msg = calculate_anomalies(df, selected_cols, contamination)
        
        if error_msg:
            st.error(error_msg)
        else:
            # Save anomaly properties into session state DataFrame
            st.session_state.df['Is_Anomaly'] = labels
            st.session_state.df['Anomaly_Score'] = scores
            
            from utils.timeline_tracker import record_timeline_event
            anomaly_count = (pd.Series(labels) == "Anomaly").sum()
            record_timeline_event("Anomalies Found", f"({anomaly_count} outliers)")
            
            # Explicitly store aggregated results to decouple from fragile df reloading
            max_score = np.max(scores) if len(scores) > 0 else 0.0
            st.session_state["anomaly_results"] = {
                "total_anomalies": anomaly_count,
                "max_score": float(max_score)
            }
            
            # 5. Render dashboard panel
            render_anomaly_dashboard(df, labels, scores, selected_cols)
            
            # 6. Display filtered grid
            st.markdown('<div class="section-title">🗂️ Audit Records View</div>', unsafe_allow_html=True)
            df_preview = df.copy()
            df_preview['Is_Anomaly'] = labels
            df_preview['Anomaly_Score'] = scores
            
            if filter_mode == "Show Anomalies Only":
                df_filtered = df_preview[df_preview['Is_Anomaly'] == "Anomaly"]
            elif filter_mode == "Show Normal Records Only":
                df_filtered = df_preview[df_preview['Is_Anomaly'] == "Normal"]
            else:
                df_filtered = df_preview
                
            st.markdown(f"Displaying **{len(df_filtered):,}** records matching filter:")
            st.dataframe(df_filtered, use_container_width=True)

# Execution block for standalone mode
if __name__ == "__main__":
    show_anomalies_page(is_standalone=True)
