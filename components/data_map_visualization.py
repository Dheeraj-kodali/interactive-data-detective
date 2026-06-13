import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def render_data_map_plot(df: pd.DataFrame, color_by_col: str):
    """
    Renders an interactive scatter plot of the UMAP embedding.
    Supports hover details, selective row highlighting, and Anomaly highlight overlays.
    """
    if 'UMAP_X' not in df.columns or 'UMAP_Y' not in df.columns:
        st.error("UMAP coordinates missing from DataFrame. Run projection first.")
        return

    # Add row index to DataFrame for hover reference
    df_plot = df.copy()
    df_plot['Row_Index'] = df_plot.index
    
    # Select hover columns (first 6 columns excluding coordinates)
    all_cols = list(df.columns)
    hover_cols = []
    for col in all_cols:
        if col not in ['UMAP_X', 'UMAP_Y', 'Row_Index', 'Is_Anomaly', 'Anomaly_Score'] and len(hover_cols) < 6:
            hover_cols.append(col)
            
    # Set up Hover Data structure for Plotly
    hover_data = {col: True for col in hover_cols}
    hover_data['Row_Index'] = True
    hover_data['UMAP_X'] = ':.3f'
    hover_data['UMAP_Y'] = ':.3f'
    if 'Anomaly_Score' in df_plot.columns:
        hover_data['Anomaly_Score'] = ':.3f'
    
    # 1. Check if Anomaly column is present to run overlay method
    if 'Is_Anomaly' in df_plot.columns:
        df_normal = df_plot[df_plot['Is_Anomaly'] == 'Normal']
        df_anomaly = df_plot[df_plot['Is_Anomaly'] == 'Anomaly']
        
        # If there are no normal points (unlikely), default to plotting all
        if df_normal.empty:
            df_normal = df_plot
            
        is_numeric = pd.api.types.is_numeric_dtype(df_normal[color_by_col])
        color_scale = "Viridis" if is_numeric else px.colors.qualitative.Safe
        
        # Plot normal points trace
        fig = px.scatter(
            df_normal,
            x='UMAP_X',
            y='UMAP_Y',
            color=color_by_col,
            hover_name='Row_Index',
            hover_data=hover_data,
            color_continuous_scale=color_scale if is_numeric else None,
            color_discrete_sequence=None if is_numeric else color_scale,
            opacity=0.65,
            labels={'UMAP_X': 'Dimension 1', 'UMAP_Y': 'Dimension 2'}
        )
        
        # Give normal points trace a description
        fig.update_traces(
            marker=dict(
                size=6.5,
                line=dict(width=0.4, color='rgba(255, 255, 255, 0.2)')
            )
        )
        
        # Add Anomaly points trace on top if anomalies exist
        if not df_anomaly.empty:
            fig_anom = px.scatter(
                df_anomaly,
                x='UMAP_X',
                y='UMAP_Y',
                hover_name='Row_Index',
                hover_data=hover_data,
                opacity=0.95
            )
            fig_anom.update_traces(
                marker=dict(
                    color='#ef4444', # Bright red/rose highlight
                    size=9,
                    symbol='circle',
                    line=dict(width=1.5, color='#ffffff') # High contrast white border
                ),
                name="⚠️ Anomalies (Outliers)",
                showlegend=True
            )
            # Append anomaly trace to figure
            fig.add_trace(fig_anom.data[0])
            
    else:
        # Standard rendering if no anomaly analysis exists
        is_numeric = pd.api.types.is_numeric_dtype(df_plot[color_by_col])
        color_scale = "Viridis" if is_numeric else px.colors.qualitative.Safe
        
        fig = px.scatter(
            df_plot,
            x='UMAP_X',
            y='UMAP_Y',
            color=color_by_col,
            hover_name='Row_Index',
            hover_data=hover_data,
            color_continuous_scale=color_scale if is_numeric else None,
            color_discrete_sequence=None if is_numeric else color_scale,
            opacity=0.75,
            labels={'UMAP_X': 'Dimension 1', 'UMAP_Y': 'Dimension 2'}
        )
        fig.update_traces(
            marker=dict(
                size=7,
                line=dict(width=0.5, color='rgba(255, 255, 255, 0.25)')
            )
        )
    
    # Apply modern style overrides matching the dark slate look
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        font_family="'Plus Jakarta Sans', sans-serif",
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=False,
            showticklabels=True,
            tickcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=False,
            showticklabels=True,
            tickcolor='rgba(255, 255, 255, 0.1)'
        ),
        legend=dict(
            title=dict(font=dict(size=11, color='#cbd5e1')),
            bgcolor='rgba(15, 23, 42, 0.5)',
            bordercolor='rgba(255, 255, 255, 0.05)',
            borderwidth=1
        ),
        coloraxis_colorbar=dict(
            title=dict(font=dict(size=11, color='#cbd5e1')),
            thicknessmode="pixels", thickness=15,
            lenmode="fraction", len=0.8
        ) if ('Is_Anomaly' not in df_plot.columns and is_numeric) or ('Is_Anomaly' in df_plot.columns and is_numeric) else None
    )

    st.markdown('<div class="section-title">🗺️ Interactive Semantic Map</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <p style="color: #64748b; font-size: 0.85rem; margin-top: -8px; margin-bottom: 15px;">
            Hover over points to examine records. Use the toolbar on the upper right of the plot 
            (Lasso or Box Select) to isolate a subset of points and audit them below.
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    # Render with event selection features if available (Streamlit >= 1.35.0)
    try:
        select_event = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode=["points", "box", "lasso"]
        )
        
        # Check if points were selected
        if select_event and "selection" in select_event and select_event["selection"]["points"]:
            points = select_event["selection"]["points"]
            selected_indices = [p["point_index"] for p in points]
            
            st.markdown(
                f"""
                <div style="margin-top: 25px; margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #38bdf8; font-size: 1rem;">🔍 Isolated Audit (Selected {len(selected_indices)} records)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.dataframe(df.iloc[selected_indices], use_container_width=True)
            
    except TypeError:
        # Fallback if older streamlit is present
        st.plotly_chart(fig, use_container_width=True)
