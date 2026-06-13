import streamlit as st
import pandas as pd
import numpy as np

def show_data_map_page(is_standalone=False):
    """
    Renders the data map page.
    Args:
        is_standalone (bool): If True, configures the page headers/styling directly.
                             If False, assumes page structure and CSS are set by app.py.
    """
    if is_standalone:
        # Configure page metadata
        st.set_page_config(
            page_title="Data Detective - Semantic Data Map",
            page_icon="🕵️‍♂️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    # 1. State Check: Verify if dataset is loaded
    if 'df' not in st.session_state or st.session_state.df is None:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; margin-top: 50px; border-color: rgba(244, 63, 94, 0.2);">
                <div style="font-size: 3rem; margin-bottom: 15px;">🕵️‍♂️</div>
                <h2 style="color: #f8fafc; font-weight: 700; margin-bottom: 10px;">Case File Unassigned</h2>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 500px; margin: 0 auto 25px auto; line-height: 1.6;">
                    The Semantic Data Map requires an active dataset to start investigation. 
                    Please return to the homepage to upload a CSV/Excel file or load the simulation dataset.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if is_standalone:
            st.page_link("app.py", label="Return to Case Upload", icon="🏠", use_container_width=True)
        return

    # Import analytical engines and components
    from analytics.umap_engine import run_umap_projection
    from components.data_map_visualization import render_data_map_plot
    
    df = st.session_state.df
    
    # 2. Sidebar parameters control (Only displayed if dataset is active)
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
            <div style="font-size: 1.8rem; margin-bottom: 3px;">🗺️</div>
            <h2 class="text-gradient-primary" style="margin: 0; font-size: 1.25rem;">MAP PARAMETERS</h2>
        </div>
        <hr style="border-color: rgba(255, 255, 255, 0.05); margin-top: 0; margin-bottom: 15px;" />
        """,
        unsafe_allow_html=True
    )
    
    # Intelligently select default columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    default_columns = numeric_cols.copy()
    for col in categorical_cols:
        if df[col].nunique() < 30:
            default_columns.append(col)
            
    # Feature selector
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 5px;">🧬 Columns to Map</div>', unsafe_allow_html=True)
    selected_features = st.sidebar.multiselect(
        "Columns to Map",
        options=df.columns.tolist(),
        default=default_columns,
        key="umap_features_multiselect",
        label_visibility="collapsed"
    )
    
    # UMAP parameters sliders
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 2px;">👥 Neighbors (n_neighbors)</div>', unsafe_allow_html=True)
    n_neighbors = st.sidebar.slider(
        "Neighbors",
        min_value=2,
        max_value=min(100, len(df)),
        value=min(15, len(df)),
        key="umap_n_neighbors_slider",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 10px; margin-bottom: 2px;">📏 Minimum Distance (min_dist)</div>', unsafe_allow_html=True)
    min_dist = st.sidebar.slider(
        "Minimum Distance",
        min_value=0.0,
        max_value=0.99,
        value=0.1,
        step=0.05,
        key="umap_min_dist_slider",
        label_visibility="collapsed"
    )
    
    # Color variable selector
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 5px;">🎨 Color Points By</div>', unsafe_allow_html=True)
    color_by_col = st.sidebar.selectbox(
        "Color Points By",
        options=df.columns.tolist(),
        index=0,
        key="umap_color_by_selectbox",
        label_visibility="collapsed"
    )
    
    # 3. Main Interface Header
    st.markdown(
        """
        <div class="glass-card">
            <h2 class="text-gradient-primary" style="margin-top: 0;">Interactive Data Map</h2>
            <p style="color: #94a3b8; line-height: 1.5; margin: 0;">
                This map represents every row of your dataset as an individual coordinate.
                By converting high-dimensional numeric and categorical variables into a 2D space (using UMAP), 
                natural clusters and trends emerge visually. Data points that share similar feature patterns group together.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 4. Run calculations
    if not selected_features:
        st.warning("⚠️ Please select at least one column in the sidebar to plot the semantic map.")
    else:
        df_mapped, error_msg = run_umap_projection(
            df, selected_features, n_neighbors, min_dist
        )
        
        if error_msg:
            st.error(error_msg)
        else:
            # 5. Render Plot
            render_data_map_plot(df_mapped, color_by_col)

# Execution block for multi-page mode
if __name__ == "__main__":
    show_data_map_page(is_standalone=True)
