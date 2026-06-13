import streamlit as st
import pandas as pd
from utils.timeline_tracker import get_timeline_event

def render_timeline():
    """
    Renders the vertical Investigation Timeline on the dashboard.
    """
    pass
    steps = [
        {"id": "Dataset Loaded", "desc": "Case file securely imported."},
        {"id": "Data Quality Checked", "desc": "Missing values and duplicates scanned."},
        {"id": "Dataset DNA Generated", "desc": "Structural fingerprint calculated."},
        {"id": "Clusters Found", "desc": "Natural segments identified."},
        {"id": "Anomalies Found", "desc": "Outliers isolated from the norm."},
        {"id": "Correlations Discovered", "desc": "Hidden relationships mapped."},
        {"id": "Timeline Intelligence Generated", "desc": "Time-series trends analyzed."},
        {"id": "Findings Generated", "desc": "Executive summary compiled."}
    ]
    
    html = '<div class="timeline-container">'
    
    for step in steps:
        event = get_timeline_event(step["id"])
        
        if event is not None:
            # Completed
            dot_class = "completed"
            title_class = ""
            time_badge = f'<span class="timeline-time">{event["time"]}</span>'
            meta_text = f'{step["desc"]} <strong>{event["meta"]}</strong>' if event["meta"] else step["desc"]
        else:
            # Pending
            dot_class = "pending"
            title_class = "pending"
            time_badge = '<span class="timeline-time">Pending</span>'
            meta_text = "Awaiting investigation."
            
        html += f"""
        <div class="timeline-item">
            <div class="timeline-dot {dot_class}"></div>
            <div class="timeline-content">
                <div class="timeline-header">
                    <span class="timeline-title {title_class}">{step["id"]}</span>
                    {time_badge}
                </div>
                <p class="timeline-meta">{meta_text}</p>
            </div>
        </div>
        """
        
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)
