import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_seasonality_dashboard(results: dict, metric_name: str):
    """
    Renders the seasonality visualizations and insights.
    """
    if results.get("error"):
        st.error(results["error"])
        return
        
    insights = results.get("insights", [])
    
    # 1. Display Insights
    st.subheader("💡 Seasonal Insights")
    for insight in insights:
        st.info(f"{insight['icon']} {insight['text']}")
        
    # 2. Display KPI Cards for Strength
    strengths = results.get("strengths", {})
    strongest = results.get("strongest_cycle", "None")
    
    col1, col2, col3 = st.columns(3)
    
    def render_strength_card(col, title, cycle_key, icon):
        val = strengths.get(cycle_key, 0)
        score = min(100, int((val / 0.5) * 100))
        is_strongest = (cycle_key == strongest)
        
        label = f"{icon} {title} Strength {'(Dominant)' if is_strongest else ''}"
        col.metric(label=label, value=f"{score}/100", delta=f"Var Coef: {val:.3f}", delta_color="off")
        
    render_strength_card(col1, "Weekly", "Weekly", "📅")
    render_strength_card(col2, "Monthly", "Monthly", "📆")
    render_strength_card(col3, "Quarterly", "Quarterly", "📊")
        
    # 3. Visualizations
    st.subheader("📊 Cyclical Patterns")
    
    weekly = results["weekly"]
    monthly = results["monthly"]
    quarterly = results["quarterly"]
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Weekly Cycle", "Monthly Cycle", "Quarterly Cycle"),
        horizontal_spacing=0.08
    )
    
    # Weekly Trace
    if not weekly.empty:
        fig.add_trace(go.Bar(
            x=weekly['DayOfWeek'].str[:3],
            y=weekly[metric_name],
            marker_color='#38bdf8',
            name="Weekly",
            showlegend=False
        ), row=1, col=1)
        
    # Monthly Trace
    if not monthly.empty:
        fig.add_trace(go.Bar(
            x=monthly['Month'].str[:3],
            y=monthly[metric_name],
            marker_color='#a78bfa',
            name="Monthly",
            showlegend=False
        ), row=1, col=2)
        
    # Quarterly Trace
    if not quarterly.empty:
        fig.add_trace(go.Bar(
            x=quarterly['Quarter'],
            y=quarterly[metric_name],
            marker_color='#fbbf24',
            name="Quarterly",
            showlegend=False
        ), row=1, col=3)
        
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=False, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    
    st.plotly_chart(fig, use_container_width=True)
