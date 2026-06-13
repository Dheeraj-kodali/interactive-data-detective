import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from analytics.clustering import analyze_distinguishing_features
from typing import List, Dict, Any

def render_cluster_dashboard(df: pd.DataFrame, labels: List[str], selected_cols: List[str]):
    """
    Renders the Segment Analysis dashboard containing distribution charts,
    distinguishing traits explorer, comparison statistics, and report downloader.
    """
    st.markdown('<div class="section-title">📊 Segment Analysis Dashboard</div>', unsafe_allow_html=True)
    
    total_rows = len(df)
    
    # Calculate distributions
    label_series = pd.Series(labels)
    distribution = label_series.value_counts()
    
    df_dist = pd.DataFrame({
        'Segment': distribution.index,
        'Count': distribution.values,
        'Percentage': (distribution.values / total_rows * 100).round(2)
    }).sort_values('Segment')
    
    # Render stats summary
    num_segments = len(df_dist[df_dist['Segment'] != "Outliers/Noise"])
    has_noise = "Outliers/Noise" in label_series.values
    noise_count = int(distribution.get("Outliers/Noise", 0))
    noise_pct = (noise_count / total_rows * 100) if total_rows > 0 else 0
    
    st.markdown(
        f"""
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        ">
            <div class="stat-card" style="min-height: 90px;">
                <div class="stat-header">
                    <span class="stat-title">Segments Discovered</span>
                    <span class="stat-icon">🧩</span>
                </div>
                <h3 class="stat-value text-teal">{num_segments}</h3>
            </div>
            <div class="stat-card" style="min-height: 90px;">
                <div class="stat-header">
                    <span class="stat-title">Average Segment Size</span>
                    <span class="stat-icon">👥</span>
                </div>
                <h3 class="stat-value">{int(distribution[distribution.index != "Outliers/Noise"].mean()) if num_segments > 0 else 0:,} rows</h3>
            </div>
            <div class="stat-card" style="min-height: 90px;">
                <div class="stat-header">
                    <span class="stat-title">Outliers/Noise Density</span>
                    <span class="stat-icon">⚠️</span>
                </div>
                <h3 class="stat-value {'text-rose' if noise_count > 0 else ''}">{noise_count:,} ({noise_pct:.1f}%)</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_chart, col_download = st.columns([2, 1])
    
    with col_chart:
        # Plotly Bar Chart of Distribution
        fig = px.bar(
            df_dist,
            x='Segment',
            y='Count',
            text=df_dist['Percentage'].apply(lambda x: f"{x}%"),
            color='Segment',
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="Segment Population Size"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#cbd5e1',
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)'),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_download:
        st.markdown("##### Download Cluster Report")
        st.markdown(
            """
            Export the original dataset appended with a `Discovered_Segment` column 
            for downstream tasks or offline analysis.
            """
        )
        
        # Build CSV file
        df_report = df.copy()
        df_report['Discovered_Segment'] = labels
        csv_bytes = df_report.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Cluster Report (CSV)",
            data=csv_bytes,
            file_name="data_detective_cluster_report.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
    # Profile Explorer Section
    st.markdown('<div class="section-title">🔍 Segment Profiler</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <p style="color: #64748b; font-size: 0.85rem; margin-top: -8px; margin-bottom: 20px;">
            Select a segment tab to examine what features mathematically distinguish it 
            from the average population.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Calculate z-score profiles
    profiles = analyze_distinguishing_features(df, labels, selected_cols)
    
    # Render segment tabs
    seg_tabs = st.tabs(df_dist['Segment'].tolist())
    
    for idx, seg_name in enumerate(df_dist['Segment'].tolist()):
        with seg_tabs[idx]:
            seg_count = int(distribution[seg_name])
            seg_pct = (seg_count / total_rows * 100)
            
            st.markdown(f"**Segment Population**: **{seg_count:,} rows** ({seg_pct:.2f}% of dataset)")
            
            # Show Distinguishing Traits
            st.markdown("##### 🧬 Top Distinguishing Traits")
            traits = profiles.get(seg_name, [])
            
            if not traits:
                st.info("No numerical traits show strong deviations for this segment.")
            else:
                for trait in traits:
                    indicator = "🟢" if trait['direction'] == "higher" else "🔴"
                    st.markdown(
                        f"""
                        - **{trait['feature']}**: {indicator} {trait['description']}.  
                          Cluster Mean: `{trait['cluster_mean']}` vs. Global Average: `{trait['global_mean']}`.
                        """
                    )
                    
            # Numeric comparisons table
            numeric_cols = df[selected_cols].select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                st.markdown("##### 📊 Statistical Mean Comparisons")
                
                df_temp = df.copy()
                df_temp['__label'] = labels
                cluster_means = df_temp[df_temp['__label'] == seg_name][numeric_cols].mean()
                global_means = df[numeric_cols].mean()
                
                compare_data = []
                for col in numeric_cols:
                    c_mean = float(cluster_means[col])
                    g_mean = float(global_means[col])
                    diff = c_mean - g_mean
                    pct_diff = (diff / g_mean * 100) if g_mean != 0 else 0.0
                    
                    compare_data.append({
                        'Feature': col,
                        'Segment Average': round(c_mean, 3),
                        'Dataset Average': round(g_mean, 3),
                        'Difference': round(diff, 3),
                        'Difference %': f"{pct_diff:+.1f}%"
                    })
                    
                compare_df = pd.DataFrame(compare_data)
                st.dataframe(compare_df, use_container_width=True, hide_index=True)
