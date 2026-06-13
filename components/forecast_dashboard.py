import streamlit as st
import plotly.graph_objects as go

def render_forecast_dashboard(results: dict, metric_name: str, date_col: str):
    """
    Renders the predictive forecasting visualizations and summary KPIs.
    """
    if results.get("error"):
        st.error(results["error"])
        return
        
    hist_df = results["historical"]
    fcast_df = results["forecast"]
    metrics = results["metrics"]
    
    # 1. KPI Summary Cards
    st.subheader("🔮 Future Projections")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="📊 Historical Baseline (Average)", value=f"{metrics['historical_mean']:,.1f}")
        
    with col2:
        proj = metrics['projected_end']
        st.metric(label="🎯 Projected End Value", value=f"{proj:,.1f}")
        
    with col3:
        growth = metrics['growth_proj']
        g_icon = "📈" if growth > 0 else "📉" if growth < 0 else "➡️"
        st.metric(label=f"{g_icon} Projected Trajectory", value=f"{growth:+.1f}%", delta="Relative to mean", delta_color="off")
        
    # 2. Visualization
    st.subheader("🔭 Forecasting Map")
    
    fig = go.Figure()
    
    # Plot Historical Data
    fig.add_trace(go.Scatter(
        x=hist_df[date_col],
        y=hist_df[metric_name],
        mode='lines',
        name='Historical Data',
        line=dict(color='#cbd5e1', width=2),
        hoverinfo='x+y'
    ))
    
    # To connect the two lines seamlessly, we insert the last historical point into the forecast arrays
    connect_date = [hist_df[date_col].iloc[-1]]
    connect_val = [hist_df[metric_name].iloc[-1]]
    
    f_dates = connect_date + fcast_df[date_col].tolist()
    f_preds = connect_val + fcast_df['Forecast'].tolist()
    f_upper = connect_val + fcast_df['Upper_Bound'].tolist()
    f_lower = connect_val + fcast_df['Lower_Bound'].tolist()
    
    # Plot Confidence Band (Upper)
    fig.add_trace(go.Scatter(
        x=f_dates,
        y=f_upper,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Plot Confidence Band (Lower)
    fig.add_trace(go.Scatter(
        x=f_dates,
        y=f_lower,
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(192, 132, 252, 0.15)',
        name='95% Confidence Interval',
        hoverinfo='skip'
    ))
    
    # Plot Forecasted Mean
    fig.add_trace(go.Scatter(
        x=f_dates,
        y=f_preds,
        mode='lines',
        name='Forecast Trajectory',
        line=dict(color='#c084fc', width=3, dash='dash'),
        hoverinfo='x+y'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        margin=dict(l=20, r=20, t=30, b=20),
        height=450,
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
