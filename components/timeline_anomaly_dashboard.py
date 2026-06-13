import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_time_anomaly_dashboard(results: dict, metric_name: str, date_col: str):
    """
    Renders the point-in-time anomaly detection visualization and ledger.
    """
    if results.get("error"):
        st.error(results["error"])
        return
        
    df = results["data"]
    anomalies = results["anomalies"]
    
    # 1. Visualization
    st.subheader("⚡ Anomaly Scatter Map")
    
    fig = go.Figure()
    
    # Expected Band
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df['Expected_Upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df['Expected_Lower'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 255, 255, 0.05)',
        name='Expected Range (IQR)',
        hoverinfo='skip'
    ))
    
    # Raw Data Line
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[metric_name],
        mode='lines',
        name='Actual Values',
        line=dict(color='rgba(56, 189, 248, 0.6)', width=2),
        hoverinfo='x+y'
    ))
    
    # Scatter Anomalies
    if anomalies:
        spike_dates = [a['date'] for a in anomalies if a['direction'] == 'Spike']
        spike_vals = [a['actual'] for a in anomalies if a['direction'] == 'Spike']
        spike_sizes = [max(8, min(24, a['severity'] / 4)) for a in anomalies if a['direction'] == 'Spike']
        
        drop_dates = [a['date'] for a in anomalies if a['direction'] == 'Drop']
        drop_vals = [a['actual'] for a in anomalies if a['direction'] == 'Drop']
        drop_sizes = [max(8, min(24, a['severity'] / 4)) for a in anomalies if a['direction'] == 'Drop']
        
        if spike_dates:
            fig.add_trace(go.Scatter(
                x=spike_dates,
                y=spike_vals,
                mode='markers',
                marker=dict(color='#10b981', size=spike_sizes, symbol='triangle-up', line=dict(color='#0b0f19', width=1)),
                name='Abnormal Spikes'
            ))
            
        if drop_dates:
            fig.add_trace(go.Scatter(
                x=drop_dates,
                y=drop_vals,
                mode='markers',
                marker=dict(color='#f43f5e', size=drop_sizes, symbol='triangle-down', line=dict(color='#0b0f19', width=1)),
                name='Abnormal Drops'
            ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(15, 23, 42, 0.5)'
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Anomaly Ledger
    st.subheader("📋 Anomaly Ledger")
    
    if not anomalies:
        st.success("🛡️ No transient anomalies detected. All data points fall within their expected historical interquartile ranges.")
        return
        
    for a in anomalies:
        is_spike = a['direction'] == 'Spike'
        color = "#10b981" if is_spike else "#f43f5e"
        icon = "🔺" if is_spike else "🔻"
        
        # Determine severity label
        if a['severity'] > 80:
            sev_label = "CRITICAL"
            sev_color = "#ef4444"
        elif a['severity'] > 50:
            sev_label = "HIGH"
            sev_color = "#f59e0b"
        else:
            sev_label = "MEDIUM"
            sev_color = "#3b82f6"
            
        date_str = pd.to_datetime(a['date']).strftime('%B %d, %Y')
        msg = f"**{icon} {date_str} - {sev_label} SEVERITY**\n\nRecorded **{a['actual']:,.1f}** (Expected ~{a['expected']:,.1f})\n\nScore: {a['severity']}/100"
        
        if a['severity'] > 80:
            st.error(msg)
        elif a['severity'] > 50:
            st.warning(msg)
        else:
            st.info(msg)
