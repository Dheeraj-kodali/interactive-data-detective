import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

def render_correlation_dashboard(
    df: pd.DataFrame, 
    ranked_relationships: List[Dict[str, Any]], 
    matrix_data: Dict[str, Any]
):
    """
    Renders the Correlation Discovery dashboard with a Findings Panel,
    Symmetric Matrix Heatmap, and OLS Scatter Explorer.
    """
    
    # 1. Findings Panel (Automatic classification)
    st.markdown('<div class="section-title">🕵️‍♂️ Correlation Findings Panel</div>', unsafe_allow_html=True)
    
    # Separate findings
    pos_findings = [r for r in ranked_relationships if not pd.isna(r['pearson']) and r['pearson'] >= 0.5]
    neg_findings = [r for r in ranked_relationships if not pd.isna(r['pearson']) and r['pearson'] <= -0.5]
    nonlinear_findings = [r for r in ranked_relationships if r['is_numeric'] and not pd.isna(r['pearson']) and r['mutual_info'] >= 0.18 and abs(r['pearson']) < 0.2]
    
    if not pos_findings and not neg_findings and not nonlinear_findings:
        st.info("No strong statistical relationships (linear or non-linear) were identified in the dataset.")
    else:
        st.markdown(
            """
            <p style="color: #64748b; font-size: 0.85rem; margin-top: -8px; margin-bottom: 15px;">
                The detective has analyzed relationship combinations and discovered the following key behaviors.
            </p>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if pos_findings:
                st.markdown(
                    """
                    <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 15px;">
                        <h6 style="color: #10b981; margin: 0 0 10px 0; font-weight: 700;">🟢 Strong Positive Trends</h6>
                        <ul style="font-size: 0.82rem; margin: 0; padding-left: 18px; line-height: 1.6; color: #cbd5e1;">
                    """ + "".join([f"<li><strong>{r['var1']}</strong> increases alongside <strong>{r['var2']}</strong> (Pearson: <code>{r['pearson']:.2f}</code>)</li>" for r in pos_findings[:4]]) + "</ul></div>",
                    unsafe_allow_html=True
                )
                
            if neg_findings:
                st.markdown(
                    """
                    <div style="background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 12px; padding: 16px;">
                        <h6 style="color: #ef4444; margin: 0 0 10px 0; font-weight: 700;">🔴 Strong Negative Trends</h6>
                        <ul style="font-size: 0.82rem; margin: 0; padding-left: 18px; line-height: 1.6; color: #cbd5e1;">
                    """ + "".join([f"<li><strong>{r['var1']}</strong> decreases as <strong>{r['var2']}</strong> increases (Pearson: <code>{r['pearson']:.2f}</code>)</li>" for r in neg_findings[:4]]) + "</ul></div>",
                    unsafe_allow_html=True
                )
                
        with col2:
            if nonlinear_findings:
                st.markdown(
                    """
                    <div style="background: rgba(245, 158, 11, 0.04); border: 1px solid rgba(245, 158, 11, 0.15); border-radius: 12px; padding: 16px; min-height: 100%;">
                        <h6 style="color: #f59e0b; margin: 0 0 10px 0; font-weight: 700;">🟡 Potential Non-Linear Connections</h6>
                        <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px; line-height: 1.4;">
                            These feature pairs show high information overlap (Mutual Info) but close to zero linear correlation, suggesting curved or complex relationships.
                        </p>
                        <ul style="font-size: 0.82rem; margin: 0; padding-left: 18px; line-height: 1.6; color: #cbd5e1;">
                    """ + "".join([f"<li><strong>{r['var1']}</strong> and <strong>{r['var2']}</strong> are connected (MI: <code>{r['mutual_info']:.2f}</code>, Pearson: <code>{r['pearson']:.2f}</code>)</li>" for r in nonlinear_findings[:4]]) + "</ul></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 16px; min-height: 100%; display: flex; align-items: center; justify-content: center;">
                        <span style="color: #64748b; font-size: 0.85rem; text-align: center;">No non-linear associations met the target info threshold.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # 2. Visualizations
    st.markdown('<div class="section-title">📊 Correlation Visualizations</div>', unsafe_allow_html=True)
    
    tab_heat, tab_net = st.tabs(["📊 Matrix Heatmap", "🕸️ Network Graph"])
    
    with tab_heat:
        matrix_type = st.radio(
        "Choose Coefficient Matrix Type",
        options=["Pearson (Linear)", "Spearman (Rank/Monotonic)", "Mutual Information (Overlap Strength)"],
        horizontal=True
    )
    
    # Extract selected matrix dataframe
    if "Pearson" in matrix_type:
        matrix_df = pd.DataFrame(matrix_data['pearson'])
        title_tag = "Pearson Correlation Matrix"
        colorscale = "RdBu_r"
        zmin, zmax = -1.0, 1.0
    elif "Spearman" in matrix_type:
        matrix_df = pd.DataFrame(matrix_data['spearman'])
        title_tag = "Spearman Rank Correlation Matrix"
        colorscale = "RdBu_r"
        zmin, zmax = -1.0, 1.0
    else:
        matrix_df = pd.DataFrame(matrix_data['mutual_info'])
        title_tag = "Mutual Information Matrix (Nats)"
        colorscale = "YlOrRd"
        zmin, zmax = 0.0, float(matrix_df.max().max())
        
        # Render Plotly Heatmap
        fig_heat = px.imshow(
            matrix_df.round(3),
            text_auto=True,
            color_continuous_scale=colorscale,
            zmin=zmin, zmax=zmax,
            title=title_tag
        )
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#cbd5e1',
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with tab_net:
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>View correlations as an interactive force-directed network graph. Adjust the slider to filter out weak relationships.</p>", unsafe_allow_html=True)
        
        # We use Pearson for the network graph as it gives directionality (positive/negative)
        net_matrix_df = pd.DataFrame(matrix_data['pearson'])
        
        threshold = st.slider(
            "Significant Edge Threshold (Absolute Pearson Correlation)",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            key="network_threshold"
        )
        
        from components.correlation_network import render_network_graph
        render_network_graph(net_matrix_df, threshold)

    # 3. Relationship Explorer
    st.markdown('<div class="section-title">🔍 Relationship Explorer</div>', unsafe_allow_html=True)
    
    # Format labels for selection
    rel_format_list = []
    rel_map = {}
    for r in ranked_relationships:
        p_str = f"Pearson: {r['pearson']:+.2f}" if not pd.isna(r['pearson']) else "Pearson: N/A"
        label = f"{r['var1']} vs {r['var2']} ({p_str} • MI: {r['mutual_info']:.2f})"
        rel_format_list.append(label)
        rel_map[label] = r
        
    selected_rel_label = st.selectbox(
        "Select Relationship Pair to Analyze",
        options=rel_format_list
    )
    
    selected_rel = rel_map[selected_rel_label]
    v1 = selected_rel['var1']
    v2 = selected_rel['var2']
    
    # Render Scatter with manual regression fit
    df_scatter = df[[v1, v2]].dropna()
    
    if df_scatter.empty:
        st.error("Cannot plot: Selected columns have zero overlapping non-null records.")
    else:
        col_plot, col_stats = st.columns([2, 1])
        
        with col_plot:
            fig_scatter = px.scatter(
                df_scatter,
                x=v1,
                y=v2,
                opacity=0.75,
                title=f"Scatter Plot: {v1} vs {v2}"
            )
            
            # If both are numeric, fit trend line
            is_num1 = pd.api.types.is_numeric_dtype(df_scatter[v1])
            is_num2 = pd.api.types.is_numeric_dtype(df_scatter[v2])
            
            m, intercept = 0.0, 0.0
            r_squared = 0.0
            
            if is_num1 and is_num2 and len(df_scatter) >= 3:
                x_vals = df_scatter[v1].values
                y_vals = df_scatter[v2].values
                
                # Manual OLS: y = mx + c
                try:
                    m, intercept = np.polyfit(x_vals, y_vals, 1)
                    
                    # Generate line coordinates
                    x_line = np.array([x_vals.min(), x_vals.max()])
                    y_line = m * x_line + intercept
                    
                    # Add trace to plotly
                    fig_scatter.add_trace(go.Scatter(
                        x=x_line,
                        y=y_line,
                        mode='lines',
                        name='OLS Trendline',
                        line=dict(color='#ef4444', width=2.5, dash='dash')
                    ))
                    
                    # Calculate R2
                    y_pred = m * x_vals + intercept
                    ss_res = np.sum((y_vals - y_pred) ** 2)
                    ss_tot = np.sum((y_vals - np.mean(y_vals)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
                    
                except Exception:
                    pass
                    
            fig_scatter.update_traces(
                marker=dict(size=7.5, line=dict(width=0.4, color='rgba(255, 255, 255, 0.25)'))
            )
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                legend=dict(bgcolor='rgba(15, 23, 42, 0.5)')
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_stats:
            st.markdown("##### Relationship Statistics")
            
            stats_table = [
                {"Metric": "Pearson Correlation (Linear)", "Value": f"{selected_rel['pearson']:+.3f}" if not pd.isna(selected_rel['pearson']) else "N/A (Categorical)"},
                {"Metric": "Spearman Correlation (Monotonic)", "Value": f"{selected_rel['spearman']:+.3f}" if not pd.isna(selected_rel['spearman']) else "N/A (Categorical)"},
                {"Metric": "Mutual Information (Nats)", "Value": f"{selected_rel['mutual_info']:.3f}"},
            ]
            
            if is_num1 and is_num2 and len(df_scatter) >= 3:
                stats_table.extend([
                    {"Metric": "R-Squared (Coeff of Det)", "Value": f"{r_squared:.4f}"},
                    {"Metric": "OLS Slope (Beta)", "Value": f"{m:+.4f}"},
                    {"Metric": "OLS Intercept (Alpha)", "Value": f"{intercept:+.4f}"},
                ])
                
            stats_df = pd.DataFrame(stats_table)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Show a brief text explanation
            st.markdown("##### Interpretation Guide")
            if not pd.isna(selected_rel['pearson']):
                r_abs = abs(selected_rel['pearson'])
                if r_abs >= 0.7:
                    strength = "strong"
                elif r_abs >= 0.4:
                    strength = "moderate"
                else:
                    strength = "weak"
                    
                direction = "positive" if selected_rel['pearson'] > 0 else "negative"
                st.write(
                    f"Features show a **{strength} {direction}** linear connection. "
                    f"Approximately **{r_squared*100:.1f}%** of the variance in `{v2}` can be explained "
                    f"by the linear influence of `{v1}`."
                )
            else:
                st.write(
                    f"One or both variables are categorical. The Mutual Information score "
                    f"of **{selected_rel['mutual_info']:.3f}** indicates how much information "
                    f"about `{v2}` is captured when observing `{v1}`."
                )
