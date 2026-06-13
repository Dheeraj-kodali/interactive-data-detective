import streamlit as st
import pandas as pd
from utils.file_loader import load_data_file, get_sample_dataset

def render_sidebar():
    """
    Renders the sidebar component including project title/logo,
    file uploader, and active file info panel.
    """
    # 1. Title/Logo Branding
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <div style="font-size: 3rem; margin-bottom: 5px;">🕵️‍♂️</div>
            <h1 style="
                background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                font-size: 1.85rem;
                font-weight: 800;
                letter-spacing: -0.02em;
            ">DATA DETECTIVE</h1>
            <p style="
                color: #64748b;
                font-size: 0.8rem;
                margin-top: 5px;
                font-weight: 500;
            ">Interactive Data Science Engine</p>
        </div>
        <hr style="border-color: rgba(255, 255, 255, 0.05); margin-top: 0; margin-bottom: 20px;" />
        """,
        unsafe_allow_html=True
    )
    
    # Initialize session state variables if they don't exist
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'file_size' not in st.session_state:
        st.session_state.file_size = None
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    st.sidebar.markdown('<div style="font-weight: 600; font-size: 0.95rem; color: #f8fafc; margin-bottom: 10px;">📥 Upload Dataset</div>', unsafe_allow_html=True)
    
    # 2. File Uploader Widget
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed"
    )

    # 3. Handle File Upload
    if uploaded_file is not None:
        try:
            # Read bytes to pass to cached loader
            file_bytes = uploaded_file.getvalue()
            df = load_data_file(file_bytes, uploaded_file.name)
            
            # Save into session state
            st.session_state.df = df
            st.session_state.file_name = uploaded_file.name
            
            # Clear cached results
            if 'correlation_results' in st.session_state:
                del st.session_state['correlation_results']
            if 'anomaly_results' in st.session_state:
                del st.session_state['anomaly_results']
            if 'segment_results' in st.session_state:
                del st.session_state['segment_results']
            
            # Format size
            size_bytes = uploaded_file.size
            if size_bytes < 1024 * 1024:
                st.session_state.file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                st.session_state.file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
                
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")

    # 4. Quick Start Sample Data Button
    if st.session_state.df is None:
        st.sidebar.markdown(
            """
            <div style="text-align: center; margin: 15px 0;">
                <span style="color: #64748b; font-size: 0.8rem;">— OR —</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.sidebar.button("🚀 Load Sample Dataset", use_container_width=True, type="secondary"):
            with st.spinner("Generating sample dataset..."):
                sample_df = get_sample_dataset()
                st.session_state.df = sample_df
                st.session_state.file_name = "e_commerce_sales_sample.csv"
                st.session_state.file_size = "138 KB (Generated)"
                
                # Clear cached results
                if 'correlation_results' in st.session_state:
                    del st.session_state['correlation_results']
                if 'anomaly_results' in st.session_state:
                    del st.session_state['anomaly_results']
                if 'segment_results' in st.session_state:
                    del st.session_state['segment_results']
                # Rerun to update main view immediately
                st.rerun()

    # 5. Dataset Specifications Panel
    if st.session_state.df is not None:
        st.sidebar.markdown(
            """
            <div style="
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 12px;
                margin-top: 25px;
                margin-bottom: 15px;
            ">
                <div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;">📁 Active Dataset</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #38bdf8; word-break: break-all; margin-bottom: 6px;">{}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Size: <span style="color: #cbd5e1; font-weight: 600;">{}</span></div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Rows: <span style="color: #cbd5e1; font-weight: 600;">{:,}</span></div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Cols: <span style="color: #cbd5e1; font-weight: 600;">{}</span></div>
            </div>
            """.format(st.session_state.file_name, st.session_state.file_size, len(st.session_state.df), len(st.session_state.df.columns)),
            unsafe_allow_html=True
        )
        
        # Reset Button to clear dataset
        if st.sidebar.button("🗑️ Clear Dataset", use_container_width=True, type="primary"):
            st.session_state.df = None
            st.session_state.file_name = None
            st.session_state.file_size = None
            
            # Clear cached results
            if 'correlation_results' in st.session_state:
                del st.session_state['correlation_results']
            if 'anomaly_results' in st.session_state:
                del st.session_state['anomaly_results']
            if 'segment_results' in st.session_state:
                del st.session_state['segment_results']
                
            st.session_state.uploader_key += 1  # Force file uploader to recreate empty
            st.rerun()
