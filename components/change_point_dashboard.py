import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.write("DEBUG CHANGE POINT DASHBOARD LOADED")
st.write(pd.__name__)

def render_change_point_dashboard(results: dict, metric_name: str, date_col: str):
    """
    Renders the change point detection visualizations and summary report.
    """
    if results.get("error"):
        st.error(results["error"])
        return
        
    df = results["data"]
    events = results["change_events"]
    
    # 1. Visualization
    st.subheader("📊 Structural Breaks Map")
    
    fig = go.Figure()
    
    # Raw data line
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[metric_name],
        mode='lines',
        name='Raw Data',
        line=dict(color='#cbd5e1', width=2),
        hoverinfo='x+y'
    ))
    
    # Highlight change points
    for idx, event in enumerate(events):
        color = "#f43f5e" if event["direction"] == "Drop" else "#10b981"
        
        # Vertical line at change point
        fig.add_vline(
            x=event["date"], 
            line_width=2, 
            line_dash="dash", 
            line_color=color,
            annotation_text=f"Shift {idx+1}", 
            annotation_position="top right",
            annotation_font_color=color
        )
        
        # Highlight marker
        fig.add_trace(go.Scatter(
            x=[event["date"]],
            y=[df.loc[df[date_col] == event["date"], metric_name].values[0]],
            mode='markers',
            marker=dict(color=color, size=12, symbol='star'),
            name=f"Shift {idx+1} ({event['direction']})",
            showlegend=True
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
    
    # 2. Summary Report
    st.subheader("📝 Regime Shift Report")
    
    if not events:
        st.success("✅ No significant structural breaks or regime changes detected. The time-series is stable within expected standard deviations.")
        return
        
    # Render an alert card for each event
    for idx, event in enumerate(events):
        is_drop = event["direction"] == "Drop"
        icon = "📉" if is_drop else "📈"
        
        shift_date = pd.to_datetime(event['date']).strftime('%B %d, %Y')
        
        if is_drop:
            st.error(f"**{icon} Shift {idx+1}: {event['direction']} detected around {shift_date}**\n\nThe metric **{metric_name}** abruptly shifted from a baseline of {event['pre_baseline']:,.1f} to a new regime averaging {event['post_baseline']:,.1f}.\n\n**Impact:** {event['shift_pct']:+.1f}%")
        else:
            st.success(f"**{icon} Shift {idx+1}: {event['direction']} detected around {shift_date}**\n\nThe metric **{metric_name}** abruptly shifted from a baseline of {event['pre_baseline']:,.1f} to a new regime averaging {event['post_baseline']:,.1f}.\n\n**Impact:** {event['shift_pct']:+.1f}%")
