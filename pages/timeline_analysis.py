import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from analytics.trend_analysis import identify_datetime_columns, analyze_time_series
from analytics.seasonality import analyze_seasonality
from analytics.change_point_detection import detect_change_points
from analytics.time_anomaly_detection import detect_time_anomalies
from analytics.forecasting import generate_forecast
from components.seasonality_dashboard import render_seasonality_dashboard
from components.change_point_dashboard import render_change_point_dashboard
from components.timeline_anomaly_dashboard import render_time_anomaly_dashboard
from components.forecast_dashboard import render_forecast_dashboard
from utils.timeline_tracker import record_timeline_event

def show_timeline_page(is_standalone=False):
    """
    Renders the Timeline Intelligence page.
    """
    if is_standalone:
        st.set_page_config(
            page_title="Data Detective - Timeline Intelligence",
            page_icon="⏳",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    # 1. State Check: Verify if dataset is loaded
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⏳ Case File Unassigned\n\nTimeline Intelligence requires an active dataset with a Date or Timestamp column. Please return to the homepage to upload a CSV/Excel file or load the simulation dataset.")
        if is_standalone:
            st.page_link("app.py", label="Return to Case Upload", icon="🏠", use_container_width=True)
        return

    df = st.session_state.df
    
    # Identify valid columns
    dt_cols = identify_datetime_columns(df)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not dt_cols:
        st.error("📅 No Timeline Detected\n\nWe couldn't detect any date or timestamp columns in this dataset. Time-series analysis cannot be performed.")
        return
        
    if not num_cols:
        st.error("Dataset has dates, but no numeric columns to track over time.")
        return

    # 2. Sidebar Parameters
    st.sidebar.header("⏳ TIME PARAMETERS")
    st.sidebar.divider()
    
    selected_date = st.sidebar.selectbox("📅 Date Column", options=dt_cols, key="timeline_date_selectbox")
    selected_val = st.sidebar.selectbox("📈 Metric to Track", options=num_cols, index=0, key="timeline_metric_selectbox")
    
    freq_mapping = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}
    selected_freq_label = st.sidebar.selectbox("🔄 Aggregation Frequency", options=list(freq_mapping.keys()), index=0, key="timeline_freq_selectbox")
    selected_freq = freq_mapping[selected_freq_label]
    
    window_size = st.sidebar.slider("Rolling Window", min_value=2, max_value=30, value=7, key="timeline_window_slider")
    forecast_horizon = st.sidebar.slider("🔮 Forecast Horizon", min_value=5, max_value=90, value=30, step=5, key="timeline_horizon_slider")


    # 3. Main Interface Header
    st.title("Timeline Intelligence")
    st.markdown("Analyze how your metrics evolve over time. We automatically group records, calculate moving averages, and determine trend direction to give you a clear picture of historical behavior.")

    # 4. Main UI Navigation (Lazy-loaded modules to prevent cross-dependencies)
    analysis_type = st.radio(
        "Select Analysis Module",
        [
            "📈 Trend Analysis", 
            "🗓️ Seasonality Cycles", 
            "🚨 Change Point Detection",
            "⚡ Anomaly Detection",
            "🔮 Future Forecasting"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if analysis_type == "📈 Trend Analysis":
        try:
            with st.spinner("Analyzing timeline trends..."):
                results = analyze_time_series(df, selected_date, selected_val, selected_freq, window_size)

            if results.get("error"):
                st.error(results["error"])
            else:
                # Record tracking event
                record_timeline_event("Timeline Intelligence Generated", f"({results['trend_direction']})")


            # 5. Executive Summary
            trend = results["trend_direction"]
            growth = results["growth_pct"]
            color = "#10b981" if trend == "Increasing" else "#f43f5e" if trend == "Decreasing" else "#38bdf8"
            icon = "📈" if trend == "Increasing" else "📉" if trend == "Decreasing" else "➡️"
            
            if trend == "Stable":
                summary_text = f"**{icon} The metric {selected_val} has remained relatively {trend.lower()}** over the analyzed period, showing a minor {growth:+.1f}% shift."
            else:
                direction_word = "grown" if trend == "Increasing" else "declined"
                summary_text = f"**{icon} The metric {selected_val} has {trend.lower()}**. Moving averages indicate it has {direction_word} by **{abs(growth):.1f}%** over the {results['n_periods']} periods analyzed."

            st.info(summary_text)

            # 6. KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="📅 Periods", value=f"{results['n_periods']}", delta=f"Total {selected_freq_label.lower()} steps", delta_color="off")
            with col2:
                st.metric(label=f"{icon} Growth Rate", value=f"{growth:+.1f}%", delta="Start vs End", delta_color="off")
            with col3:
                st.metric(label="⭐ Peak Value", value=f"{results['peak_val']:,.1f}", delta=f"On {results['peak_date'].strftime('%Y-%m-%d')}", delta_color="off")
            with col4:
                st.metric(label="📊 Total Volume", value=f"{results['total_volume']:,.0f}", delta="Sum of all periods", delta_color="off")

            # 7. Plotly Visualization
            st.subheader("📊 Time-Series Analysis")
            
            agg_df = results["data"]
            
            fig = go.Figure()

            # Raw Data Line
            fig.add_trace(go.Scatter(
                x=agg_df[selected_date],
                y=agg_df[selected_val],
                mode='lines',
                name='Raw Data',
                line=dict(color='rgba(255,255,255,0.3)', width=1),
                hoverinfo='x+y'
            ))

            # Moving Average Line
            fig.add_trace(go.Scatter(
                x=agg_df[selected_date],
                y=agg_df['Moving_Avg'],
                mode='lines',
                name=f'{window_size}-Period MA',
                line=dict(color='#38bdf8', width=3),
                hoverinfo='x+y'
            ))

            # Standard Deviation Band (Upper)
            fig.add_trace(go.Scatter(
                x=agg_df[selected_date],
                y=agg_df['Moving_Avg'] + agg_df['Rolling_Std'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Standard Deviation Band (Lower)
            fig.add_trace(go.Scatter(
                x=agg_df[selected_date],
                y=agg_df['Moving_Avg'] - agg_df['Rolling_Std'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(56, 189, 248, 0.1)',
                name='+/- 1 Std Dev',
                hoverinfo='skip'
            ))

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                margin=dict(l=20, r=20, t=20, b=20),
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
        except Exception as e:
            st.error(f"⚠️ Trend Analysis failed: {str(e)}")
            st.info("Continuing to render remaining sections...")

    elif analysis_type == "🗓️ Seasonality Cycles":
        try:
            with st.spinner("Extracting seasonal cycles..."):
                season_results = analyze_seasonality(df, selected_date, selected_val)
                render_seasonality_dashboard(season_results, selected_val)
        except Exception as e:
            st.error(f"⚠️ Seasonality extraction failed: {str(e)}")
            
    elif analysis_type == "🚨 Change Point Detection":
        try:
            with st.spinner("Detecting structural breaks..."):
                # Set rolling window to 7 or 14 to capture meaningful baseline shifts
                change_results = detect_change_points(df, selected_date, selected_val, selected_freq, max(7, window_size), z_threshold=2.5)
                render_change_point_dashboard(change_results, selected_val, selected_date)
        except Exception as e:
            st.error(f"⚠️ Change Point Detection failed: {str(e)}")
            
    elif analysis_type == "⚡ Anomaly Detection":
        try:
            with st.spinner("Scanning for point anomalies..."):
                anomaly_results = detect_time_anomalies(df, selected_date, selected_val, selected_freq, max(7, window_size))
                render_time_anomaly_dashboard(anomaly_results, selected_val, selected_date)
        except Exception as e:
            st.error(f"⚠️ Anomaly Detection failed: {str(e)}")
            
    elif analysis_type == "🔮 Future Forecasting":
        try:
            with st.spinner("Training predictive model..."):
                forecast_results = generate_forecast(df, selected_date, selected_val, selected_freq, forecast_horizon)
                render_forecast_dashboard(forecast_results, selected_val, selected_date)
        except Exception as e:
            st.error(f"⚠️ Forecasting failed: {str(e)}")

if __name__ == "__main__":
    show_timeline_page(is_standalone=True)
