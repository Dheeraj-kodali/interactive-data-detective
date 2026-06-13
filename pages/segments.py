import streamlit as st
import pandas as pd
import numpy as np

def show_segments_page(is_standalone=False):
    """
    Renders the Segment Discovery page.
    Handles algorithm params, calls modeling layer, and renders dashboards.
    """
    if is_standalone:
        st.set_page_config(
            page_title="Data Detective - Hidden Segment Discovery",
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
                    Segment Discovery requires an active dataset to partition records. 
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
    from analytics.clustering import calculate_clusters
    from components.cluster_dashboard import render_cluster_dashboard
    
    df = st.session_state.df
    
    # 2. Sidebar Parameters
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
            <div style="font-size: 1.8rem; margin-bottom: 3px;">🔍</div>
            <h2 style="
                background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                font-size: 1.25rem;
                font-weight: 800;
            ">CLUSTERING</h2>
        </div>
        <hr style="border-color: rgba(255, 255, 255, 0.05); margin-top: 0; margin-bottom: 15px;" />
        """,
        unsafe_allow_html=True
    )
    
    # Algorithm Selector
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 5px;">🤖 Algorithm</div>', unsafe_allow_html=True)
    algorithm = st.sidebar.selectbox(
        "Algorithm",
        options=["K-Means", "DBSCAN"],
        key="cluster_algo_select",
        label_visibility="collapsed"
    )
    
    # Hyperparameters
    params = {}
    if algorithm == "K-Means":
        st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 2px;">🔢 Cluster Count (k)</div>', unsafe_allow_html=True)
        n_clusters = st.sidebar.slider(
            "Cluster Count",
            min_value=2,
            max_value=min(15, len(df)),
            value=min(4, len(df)),
            key="kmeans_k_slider",
            label_visibility="collapsed"
        )
        params["n_clusters"] = n_clusters
    else:
        st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 2px;">📏 Radius (eps)</div>', unsafe_allow_html=True)
        eps = st.sidebar.slider(
            "Radius",
            min_value=0.05,
            max_value=5.0,
            value=0.5,
            step=0.05,
            key="dbscan_eps_slider",
            label_visibility="collapsed"
        )
        params["eps"] = eps
        
        st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 10px; margin-bottom: 2px;">👥 Min Samples</div>', unsafe_allow_html=True)
        min_samples = st.sidebar.slider(
            "Min Samples",
            min_value=2,
            max_value=50,
            value=5,
            key="dbscan_min_samples_slider",
            label_visibility="collapsed"
        )
        params["min_samples"] = min_samples

    # Feature selections
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 15px; margin-bottom: 5px;">🧬 Columns to Cluster</div>', unsafe_allow_html=True)
    selected_cols = st.sidebar.multiselect(
        "Columns to Cluster",
        options=df.columns.tolist(),
        default=numeric_cols,
        key="cluster_features_multiselect",
        label_visibility="collapsed"
    )
    
    # 3. Main Header
    st.markdown(
        """
        <div class="glass-card">
            <h2 class="text-gradient-primary" style="margin-top: 0;">Hidden Segment Discovery</h2>
            <p style="color: #94a3b8; line-height: 1.5; margin: 0;">
                This module automatically categorizes your dataset records into logical subsets (segments). 
                By grouping observations that exhibit similar numeric patterns, we reveal hidden behaviors 
                and characteristic profiles within your data.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 4. Trigger calculations
    if not selected_cols:
        st.warning("⚠️ Please select at least one feature in the sidebar to run the clustering analysis.")
    else:
        labels, error_msg = calculate_clusters(df, selected_cols, algorithm, params)
        
        if error_msg:
            st.error(error_msg)
        else:
            # Save labels into the session state DataFrame
            # This enables UMAP or table views on other pages to immediately map by cluster labels!
            st.session_state.df['Cluster_Label'] = labels
            
            from utils.timeline_tracker import record_timeline_event
            unique_clusters = len(set(labels) - {"Outliers/Noise"})
            record_timeline_event("Clusters Found", f"({unique_clusters} segments)")
            
            # Explicitly store aggregated results to decouple from fragile df reloading
            valid_clusters = [l for l in labels if l != "Outliers/Noise"]
            if valid_clusters:
                largest_cluster = pd.Series(valid_clusters).value_counts().index[0]
            else:
                largest_cluster = "None"
                
            st.session_state["segment_results"] = {
                "unique_clusters": unique_clusters,
                "largest_cluster": largest_cluster
            }
            
            # 5. Render dashboard panel
            render_cluster_dashboard(df, labels, selected_cols)

# Execution block for multi-page mode
if __name__ == "__main__":
    show_segments_page(is_standalone=True)
