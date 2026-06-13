import streamlit as st

def inject_global_css():
    """
    Injects a unified SaaS-style design system.
    This replaces all inline <style> blocks scattered across components.
    """
    st.markdown(
        """
        <style>
            /* Import premium font */
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

            /* Global Font Override & Background styling */
            html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: #0b0f19 !important;
                color: #e2e8f0 !important;
            }
            
            /* Sidebar layout customization */
            [data-testid="stSidebar"] {
                background-color: #0f172a !important;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            /* Streamlit Tabs customized style overrides */
            button[data-baseweb="tab"] {
                font-size: 0.95rem !important;
                font-weight: 600 !important;
                color: #94a3b8 !important;
                border-bottom: 2px solid transparent !important;
                transition: all 0.2s ease !important;
                padding: 10px 16px !important;
            }
            
            button[data-baseweb="tab"]:hover {
                color: #38bdf8 !important;
            }
            
            button[data-baseweb="tab"][aria-selected="true"] {
                color: #38bdf8 !important;
                border-bottom-color: #38bdf8 !important;
                background: rgba(56, 189, 248, 0.05) !important;
                border-top-left-radius: 6px !important;
                border-top-right-radius: 6px !important;
            }

            /* --- Unified SaaS Classes --- */
            
            /* Standard Glassmorphism Card */
            .glass-card {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.75) 100%);
                border: 1px solid rgba(56, 189, 248, 0.12);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 25px;
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .glass-card:hover {
                border-color: rgba(167, 139, 250, 0.25);
                box-shadow: 0 10px 25px rgba(167, 139, 250, 0.08);
            }
            
            /* Section Titles */
            .section-title {
                font-size: 1.25rem;
                font-weight: 700;
                color: #f8fafc;
                margin-top: 15px;
                margin-bottom: 15px;
                border-left: 4px solid #38bdf8;
                padding-left: 12px;
                letter-spacing: -0.01em;
            }
            
            /* Big Gradients for Headers */
            .text-gradient-primary {
                background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }
            
            .text-gradient-light {
                background: linear-gradient(135deg, #f8fafc 10%, #cbd5e1 50%, #94a3b8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }

            /* Metric/KPI Cards */
            .kpi-card {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                min-height: 120px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .kpi-card:hover {
                transform: translateY(-3px);
                border-color: rgba(56, 189, 248, 0.3);
                background: rgba(30, 41, 59, 0.8);
            }
            
            .kpi-title {
                font-size: 0.85rem;
                color: #94a3b8;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            }
            
            .kpi-value {
                font-size: 2rem;
                font-weight: 800;
                color: #f8fafc;
                line-height: 1.2;
            }
            
            .kpi-icon {
                position: absolute;
                top: 15px;
                right: 15px;
                font-size: 1.5rem;
                opacity: 0.7;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px;
                margin-bottom: 25px;
                width: 100%;
            }
            
            /* Timeline Specific Classes */
            .timeline-container {
                position: relative;
                max-width: 100%;
                margin: 20px 0;
                padding-left: 20px;
            }
            .timeline-container::before {
                content: '';
                position: absolute;
                top: 15px;
                bottom: 15px;
                left: 27px;
                width: 2px;
                background: rgba(255, 255, 255, 0.1);
            }
            .timeline-item {
                position: relative;
                margin-bottom: 25px;
                padding-left: 35px;
            }
            .timeline-dot {
                position: absolute;
                left: 0;
                top: 4px;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #0f172a;
                border: 2px solid #38bdf8;
                z-index: 1;
                transition: all 0.3s ease;
            }
            .timeline-dot.completed {
                background: #38bdf8;
                box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
            }
            .timeline-dot.pending {
                border-color: rgba(255, 255, 255, 0.2);
            }
            .timeline-content {
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 12px 16px;
                transition: transform 0.2s ease;
            }
            .timeline-content:hover {
                transform: translateX(5px);
                border-color: rgba(56, 189, 248, 0.2);
            }
            .timeline-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 4px;
            }
            .timeline-title {
                font-weight: 700;
                color: #e2e8f0;
                font-size: 0.95rem;
            }
            .timeline-title.pending {
                color: #64748b;
            }
            .timeline-time {
                font-size: 0.75rem;
                color: #94a3b8;
                background: rgba(255, 255, 255, 0.05);
                padding: 2px 8px;
                border-radius: 12px;
            }
            .timeline-meta {
                font-size: 0.8rem;
                color: #94a3b8;
                margin: 0;
            }

            /* Insight Rows */
            .insight-row {
                background: rgba(15, 23, 42, 0.5);
                border-left: 4px solid #38bdf8;
                padding: 16px 20px;
                margin-bottom: 12px;
                border-radius: 4px 8px 8px 4px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .insight-icon {
                font-size: 1.4rem;
            }
            .insight-text {
                font-size: 0.95rem;
                color: #e2e8f0;
                margin: 0;
                line-height: 1.5;
            }
            .insight-highlight {
                font-weight: 700;
            }
            
            /* Text Gradients */
            .text-teal {
                background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            .text-purple {
                background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            .text-amber {
                background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            .text-rose {
                background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            
            /* Streamlit Slider Overrides */
            div[data-baseweb="slider"] {
                padding-bottom: 15px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
