import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from analytics.anomaly_detection import explain_anomaly_record
from typing import List, Dict, Any

def render_anomaly_dashboard(
    df: pd.DataFrame, 
    labels: List[str], 
    scores: List[float], 
    selected_cols: List[str]
):
    """
    Renders the Anomaly Analysis dashboard showing summaries, Plotly charts,
    top anomalous records table, record explanations, and CSV downloader.
    """
    st.markdown('<div class="section-title">📊 Anomaly Analysis Dashboard</div>', unsafe_allow_html=True)
    
    total_rows = len(df)
    
    # Calculate statistics
    label_series = pd.Series(labels)
    anomaly_count = int((label_series == "Anomaly").sum())
    anomaly_pct = (anomaly_count / total_rows * 100) if total_rows > 0 else 0.0
    
    # Render stats summary
    st.markdown(
        f"""
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        ">
            <div class="stat-card" style="min-height: 90px; border-left: 4px solid {'#ef4444' if anomaly_count > 0 else '#10b981'};">
                <div class="stat-header">
                    <span class="stat-title">Anomalies Detected</span>
                    <span class="stat-icon">⚠️</span>
                </div>
                <h3 class="stat-value {'text-rose' if anomaly_count > 0 else ''}">{anomaly_count:,}</h3>
            </div>
            <div class="stat-card" style="min-height: 90px;">
                <div class="stat-header">
                    <span class="stat-title">Outlier Ratio</span>
                    <span class="stat-icon">📈</span>
                </div>
                <h3 class="stat-value">{anomaly_pct:.2f}%</h3>
            </div>
            <div class="stat-card" style="min-height: 90px;">
                <div class="stat-header">
                    <span class="stat-title">Clean Records</span>
                    <span class="stat-icon">🟢</span>
                </div>
                <h3 class="stat-value text-teal">{total_rows - anomaly_count:,}</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Visual distributions
    col_chart, col_download = st.columns([2, 1])
    
    with col_chart:
        df_dist = pd.DataFrame({
            'Status': ['Normal', 'Anomaly'],
            'Count': [total_rows - anomaly_count, anomaly_count]
        })
        fig = px.pie(
            df_dist,
            values='Count',
            names='Status',
            color='Status',
            color_discrete_map={'Normal': '#10b981', 'Anomaly': '#ef4444'},
            hole=0.4,
            title="Data Point Classification"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#cbd5e1',
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_download:
        st.markdown("##### Export Anomaly Log")
        st.markdown(
            """
            Export a full dataset report containing anomaly classifications and 
            normalized anomaly scores (0 to 1 scale) for record filtering.
            """
        )
        
        df_report = df.copy()
        df_report['Is_Anomaly'] = labels
        df_report['Anomaly_Score'] = scores
        csv_bytes = df_report.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Anomaly Report (CSV)",
            data=csv_bytes,
            file_name="data_detective_anomaly_report.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
    # Top anomalies table
    st.markdown('<div class="section-title">🕵️‍♂️ Top Anomalous Records</div>', unsafe_allow_html=True)
    df_temp = df.copy()
    df_temp['Is_Anomaly'] = labels
    df_temp['Anomaly_Score'] = scores
    
    # Sub-select anomalies only and sort by highest score
    df_anom = df_temp[df_temp['Is_Anomaly'] == "Anomaly"].sort_values('Anomaly_Score', ascending=False)
    
    if df_anom.empty:
        st.success("No anomalies detected based on the current contamination rate.")
    else:
        st.markdown(
            "The following records are sorted by their normalized anomaly score. A score of 1.0 represents the most isolated point."
        )
        st.dataframe(df_anom.head(10), use_container_width=True)
        
        # Interactive explanation module
        st.markdown('<div class="section-title">🔍 Anomaly Inspector (Deviation Explainer)</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <p style="color: #64748b; font-size: 0.85rem; margin-top: -8px; margin-bottom: 15px;">
                Select a specific anomalous row index to audit why it was flagged as an outlier.
                This calculates feature-level deviations (Z-Scores) against its parent cluster average (if clustering exists)
                or the global average.
            </p>
            """,
            unsafe_allow_html=True
        )
        
        selected_row_idx = st.selectbox(
            "Select Anomaly Index to Audit",
            options=df_anom.index.tolist(),
            format_func=lambda x: f"Row Index {x} (Score: {df_temp.loc[x, 'Anomaly_Score']:.3f})"
        )
        
        # Get cluster labels from dataframe if present
        cluster_labels = df.get('Cluster') if 'Cluster' in df.columns else None
        
        explanations = explain_anomaly_record(
            df, selected_row_idx, selected_cols, cluster_labels
        )
        
        # Render visual audit card
        if not explanations:
            st.info(
                """
                **Multidimensional Outlier Profile**:  
                This record represents a multi-feature anomaly. No single feature stands out as 
                an extreme outlier on its own, but the unique combination of feature values 
                is highly mathematically isolated.
                """
            )
        else:
            comp_group_name = explanations[0]['group_label']
            st.markdown(
                f"""
                <div style="
                    background: rgba(239, 68, 68, 0.05);
                    border: 1px solid rgba(239, 68, 68, 0.15);
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                ">
                    <h5 style="color: #ef4444; margin-top: 0; margin-bottom: 12px; font-weight: 700;">
                        🕵️‍♂️ Audit Findings: Row Index {selected_row_idx} (compared against {comp_group_name})
                    </h5>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                """,
                unsafe_allow_html=True
            )
            for exp in explanations:
                indicator = "🔺" if exp['direction'] == "higher" else "🔻"
                st.write(f"{indicator} {exp['text']}")
            st.markdown("</div></div>", unsafe_allow_html=True)
