import streamlit as st
import pandas as pd
import numpy as np

def inject_insight_css():
    pass

def render_metric_card(title: str, value: str, icon: str, color_hex: str = "#38bdf8"):
    st.markdown(
        f"""
        <div class="kpi-card" style="border-top: 3px solid {color_hex};">
            <div class="kpi-icon" style="color: {color_hex};">{icon}</div>
            <h3 class="kpi-title">{title}</h3>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_insight_sentence(text: str, icon: str, border_color: str = "#38bdf8"):
    st.markdown(
        f"""
        <div class="insight-row" style="border-left-color: {border_color};">
            <div class="insight-icon">{icon}</div>
            <p class="insight-text">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def generate_insights(df: pd.DataFrame, ranked_relationships: list = None) -> list:
    """
    Evaluates statistical rules on the dataframe to generate English insight strings.
    """
    insights = []
    total_records = len(df)
    
    # 1. Dataset Health
    if total_records > 0:
        missing_total = df.isna().sum().sum()
        total_cells = df.size
        missing_pct = (missing_total / total_cells) * 100
        
        if missing_pct > 5.0:
            insights.append({
                "text": f"Dataset has a <span class='insight-highlight'>high missing value rate ({missing_pct:.1f}%)</span>. Consider imputing or removing sparse features.",
                "icon": "⚠️",
                "color": "#f59e0b"
            })
        elif missing_pct == 0:
            insights.append({
                "text": "Dataset is completely clean with <span class='insight-highlight'>0 missing values</span>.",
                "icon": "✨",
                "color": "#10b981"
            })
            
    # 2. Segments
    if 'Cluster_Label' in df.columns:
        valid_clusters = df[df['Cluster_Label'] != "Outliers/Noise"]['Cluster_Label']
        if not valid_clusters.empty:
            cluster_counts = valid_clusters.value_counts()
            largest_cluster = cluster_counts.index[0]
            largest_pct = (cluster_counts.iloc[0] / total_records) * 100
            
            insights.append({
                "text": f"<span class='insight-highlight'>{largest_cluster}</span> is the dominant segment, containing <span class='insight-highlight'>{largest_pct:.1f}%</span> of all records.",
                "icon": "👥",
                "color": "#38bdf8"
            })
            
    # 3. Anomalies
    if 'Is_Anomaly' in df.columns:
        anomaly_count = (df['Is_Anomaly'] == 'Anomaly').sum()
        if anomaly_count > 0:
            insights.append({
                "text": f"The Isolation Forest detected <span class='insight-highlight'>{anomaly_count} highly unusual observations</span> requiring review.",
                "icon": "🚨",
                "color": "#ef4444"
            })
        else:
            insights.append({
                "text": "No statistical anomalies detected in the current dataset bounds.",
                "icon": "🛡️",
                "color": "#10b981"
            })
            
    # 4. Correlations
    if ranked_relationships:
        pos_linear = [r for r in ranked_relationships if not pd.isna(r['pearson']) and r['pearson'] >= 0.5]
        neg_linear = [r for r in ranked_relationships if not pd.isna(r['pearson']) and r['pearson'] <= -0.5]
        
        if pos_linear:
            top_pos = pos_linear[0]
            insights.append({
                "text": f"<span class='insight-highlight'>{top_pos['var1']}</span> and <span class='insight-highlight'>{top_pos['var2']}</span> show a strong positive relationship (Pearson: {top_pos['pearson']:.2f}).",
                "icon": "📈",
                "color": "#10b981"
            })
            
        if neg_linear:
            top_neg = sorted(neg_linear, key=lambda x: x['pearson'])[0]
            insights.append({
                "text": f"<span class='insight-highlight'>{top_neg['var1']}</span> and <span class='insight-highlight'>{top_neg['var2']}</span> show a strong inverse relationship (Pearson: {top_neg['pearson']:.2f}).",
                "icon": "📉",
                "color": "#f43f5e"
            })
            
    if not insights:
        insights.append({
            "text": "Run clustering, anomaly detection, or correlation mining to uncover more insights.",
            "icon": "🔍",
            "color": "#94a3b8"
        })
        
    return insights
