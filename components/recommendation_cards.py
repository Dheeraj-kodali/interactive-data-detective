import streamlit as st
import pandas as pd
from analytics.recommendation_engine import generate_analytical_recommendations

def render_recommendation_cards(df: pd.DataFrame):
    """
    Renders the intelligent analytics recommendation cards.
    """
    recs = generate_analytical_recommendations(df)
    
    st.markdown('<div class="section-title" style="margin-top: 10px;">🎯 Recommended Next Steps</div>', unsafe_allow_html=True)
    
    # We will use columns to render them side-by-side
    cols = st.columns(len(recs))
    
    for i, rec in enumerate(recs):
        with cols[i]:
            st.markdown(
                f"""
                <div class="glass-card" style="height: 100%; border-top: 3px solid {rec['color']}; padding: 15px; display: flex; flex-direction: column; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="font-size: 1.5rem;">{rec['icon']}</div>
                        <h4 style="margin: 0; color: #f8fafc; font-size: 0.95rem;">{rec['title']}</h4>
                    </div>
                    <p style="margin: 0; color: #94a3b8; font-size: 0.8rem; line-height: 1.5; flex-grow: 1;">
                        {rec['reason']}
                    </p>
                    <div style="margin-top: auto; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05);">
                        <span style="color: {rec['color']}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">▶ Execute Module</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
