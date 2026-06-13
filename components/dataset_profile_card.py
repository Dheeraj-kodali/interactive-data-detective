import streamlit as st
import pandas as pd
from analytics.dataset_profiler import profile_dataset

def render_dataset_profile(df: pd.DataFrame):
    """
    Renders the Smart Dataset Profiler UI card on the dashboard.
    """
    profile = profile_dataset(df)
    
    st.markdown('<div class="section-title" style="margin-top: 25px;">🧠 Smart Dataset Profiler</div>', unsafe_allow_html=True)
    
    # Render the card
    modules_html = "".join([f'<li style="margin-bottom: 5px;"><span style="color: {profile["color"]}; margin-right: 8px;">◈</span> {m}</li>' for m in profile["modules"]])
    
    st.markdown(
        f"""
        <div class="glass-card" style="border-top: 4px solid {profile["color"]}; padding: 20px; margin-bottom: 25px;">
            <div style="display: flex; align-items: flex-start; gap: 20px;">
                <div style="font-size: 3.5rem; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; height: 90px; width: 90px; display: flex; align-items: center; justify-content: center;">
                    {profile["icon"]}
                </div>
                <div style="flex-grow: 1;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Detected Dataset Type</div>
                    <h2 style="margin: 0 0 10px 0; color: #f8fafc; font-size: 1.8rem; font-weight: 800;">{profile["type"]}</h2>
                    
                    <div style="margin-top: 15px; background: rgba(15, 23, 42, 0.4); padding: 12px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #cbd5e1; margin-bottom: 8px;">RECOMMENDED MODULES</div>
                        <ul style="margin: 0; padding-left: 10px; color: #94a3b8; font-size: 0.95rem; list-style-type: none;">
                            {modules_html}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
