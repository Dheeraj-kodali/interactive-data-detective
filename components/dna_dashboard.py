import streamlit as st
import plotly.graph_objects as go

def render_dna_radar_chart(dna_results: dict):
    """
    Renders the radar chart using Plotly Scatterpolar.
    """
    categories = ['Quality', 'Complexity', 'Clusterability', 'Stability', 'Richness']
    
    # We close the polygon by repeating the first element
    values = [dna_results[cat] for cat in categories]
    values.append(values[0])
    
    radar_categories = categories + [categories[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(167, 139, 250, 0.4)',
        line=dict(color='#a78bfa', width=3),
        marker=dict(color='#f8fafc', size=8),
        name='Dataset DNA'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#94a3b8', size=10)
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#e2e8f0', size=13, weight='bold')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_dna_breakdown(dna_results: dict):
    """
    Renders the 5 individual score bars.
    """
    st.markdown(
        """
        <style>
            .dna-bar-container {
                margin-bottom: 20px;
            }
            .dna-bar-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 6px;
            }
            .dna-bar-label {
                font-weight: 600;
                color: #e2e8f0;
                font-size: 0.95rem;
            }
            .dna-bar-value {
                font-weight: 800;
                color: #38bdf8;
                font-size: 0.95rem;
            }
            .dna-progress-bg {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                height: 8px;
                overflow: hidden;
            }
            .dna-progress-fill {
                height: 100%;
                border-radius: 8px;
                transition: width 1s ease-in-out;
            }
            .dna-bar-desc {
                font-size: 0.8rem;
                color: #94a3b8;
                margin-top: 6px;
                line-height: 1.3;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    metrics = [
        {"name": "Quality", "val": dna_results["Quality"], "color": "#10b981", "desc": "Cleanliness of data (missing values, duplicates)."},
        {"name": "Complexity", "val": dna_results["Complexity"], "color": "#f59e0b", "desc": "Dimensionality and categorical cardinality."},
        {"name": "Clusterability", "val": dna_results["Clusterability"], "color": "#38bdf8", "desc": "Tendency of the data to form distinct natural groups."},
        {"name": "Stability", "val": dna_results["Stability"], "color": "#ef4444", "desc": "Resistance to extreme outliers and statistical anomalies."},
        {"name": "Richness", "val": dna_results["Richness"], "color": "#a78bfa", "desc": "Diversity of data types and information density."}
    ]
    
    for m in metrics:
        st.markdown(
            f"""
            <div class="dna-bar-container">
                <div class="dna-bar-header">
                    <span class="dna-bar-label">{m['name']}</span>
                    <span class="dna-bar-value" style="color: {m['color']};">{m['val']}/100</span>
                </div>
                <div class="dna-progress-bg">
                    <div class="dna-progress-fill" style="width: {m['val']}%; background-color: {m['color']};"></div>
                </div>
                <div class="dna-bar-desc">{m['desc']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def show_dna_dashboard_page(is_standalone=False):
    """
    Main page entrypoint for Dataset DNA.
    """
    if is_standalone:
        st.set_page_config(page_title="Data Detective - Dataset DNA", page_icon="🧬", layout="wide")

    if 'df' not in st.session_state or st.session_state.df is None:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">🧬</div>
                <h2 style="color: #f8fafc; font-weight: 700; margin-bottom: 10px;">DNA Unassigned</h2>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 500px; margin: 0 auto 25px auto; line-height: 1.6;">
                    Upload a dataset to generate its unique fingerprint.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    from analytics.dataset_dna import generate_dataset_dna
    from utils.timeline_tracker import record_timeline_event
    
    df = st.session_state.df
    dna_results = generate_dataset_dna(df)
    record_timeline_event("Dataset DNA Generated", f"({dna_results['Overall']}/100)")
    
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.75) 100%);
                    border: 1px solid rgba(167, 139, 250, 0.15);
                    border-radius: 16px;
                    padding: 30px;
                    margin-bottom: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;">
            <div>
                <span style="display: inline-block; background: rgba(167, 139, 250, 0.1); color: #a78bfa; font-size: 0.75rem; font-weight: 700; padding: 5px 15px; border-radius: 20px; border: 1px solid rgba(167, 139, 250, 0.2); margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.05em;">Automated Profiling</span>
                <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Dataset DNA Profile</h1>
                <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.95rem;">A unique, multidimensional fingerprint representing the structural identity of your dataset.</p>
            </div>
            <div style="text-align: right; background: rgba(15, 23, 42, 0.5); padding: 15px 30px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;">Overall Score</div>
                <div style="font-size: 3rem; font-weight: 800; color: #a78bfa; line-height: 1;">{score}</div>
            </div>
        </div>
        """.format(score=dna_results['Overall']),
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-bottom: 15px; border-left: 4px solid #a78bfa; padding-left: 12px;">Spider/Radar Fingerprint</div>', unsafe_allow_html=True)
        render_dna_radar_chart(dna_results)
        
    with col2:
        st.markdown('<div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-bottom: 25px; border-left: 4px solid #38bdf8; padding-left: 12px;">Genetic Breakdown</div>', unsafe_allow_html=True)
        render_dna_breakdown(dna_results)

if __name__ == "__main__":
    show_dna_dashboard_page(is_standalone=True)
