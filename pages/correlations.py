import streamlit as st
import pandas as pd
import numpy as np

def show_correlations_page(is_standalone=False):
    """
    Renders the Correlation Discovery page.
    Manages controls, mines relationships, and displays dashboards.
    """
    if is_standalone:
        st.set_page_config(
            page_title="Data Detective - Correlation Discovery",
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
                    Correlation Discovery requires an active dataset to mine relationships. 
                    Please return to the homepage to upload a CSV/Excel file or load the simulation dataset.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if is_standalone:
            st.page_link("app.py", label="Return to Case Upload", icon="🏠", use_container_width=True)
        return

    # Import analytical engine and dashboard component
    from analytics.correlation_engine import (
        mine_correlations,
        get_cached_correlation_results,
        set_cached_correlation_results
    )
    from components.correlation_dashboard import render_correlation_dashboard
    from utils.file_loader import deduplicate_columns
    import collections
    
    df = st.session_state.df

    # 2. Pre-flight Validation: Check for duplicates
    if not df.columns.is_unique:
        duplicates = [item for item, count in collections.Counter(df.columns).items() if count > 1]
        st.warning(f"⚠️ **Duplicate Columns Detected**: Expected unique column names, got duplicates: {duplicates}")
        st.info("The application will automatically append suffixes to resolve this so your analysis can continue.")
        
        # Auto-resolve
        df = deduplicate_columns(df, source="Correlation Pre-flight")
        st.session_state.df = df
        
    # 3. Sidebar parameters
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
            <div style="font-size: 1.8rem; margin-bottom: 3px;">🔗</div>
            <h2 class="text-gradient-primary" style="margin: 0; font-size: 1.25rem;">RELATIONS</h2>
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
        # Include low-cardinality variables
        if df[col].nunique() < 30:
            default_columns.append(col)
            
    # Feature selector
    st.sidebar.markdown('<div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 5px;">🧬 Columns to Analyze</div>', unsafe_allow_html=True)
    selected_cols = st.sidebar.multiselect(
        "Columns to Analyze",
        options=df.columns.tolist(),
        default=default_columns,
        key="correlation_features_multiselect",
        label_visibility="collapsed"
    )
    
    # 3. Main Header
    st.markdown(
        """
        <div class="glass-card">
            <h2 class="text-gradient-primary" style="margin-top: 0;">Correlation & Relationship Discovery</h2>
            <p style="color: #94a3b8; line-height: 1.5; margin: 0;">
                Mine connections between variables using linear Pearson coefficients, monotonic Spearman rank scores, 
                and binned Mutual Information values. This dashboard helps you automatically detect strong linear, 
                rank-based, and non-linear patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 4. Trigger calculations
    if len(selected_cols) < 2:
        st.warning("⚠️ Please select at least 2 columns in the sidebar to perform correlation mining.")
    else:
        # Check cache first
        cached_ranked, cached_matrix, cached_cols = get_cached_correlation_results(df)
        if cached_ranked is not None and cached_cols == selected_cols:
            ranked_relationships = cached_ranked
            matrix_data = cached_matrix
            error_msg = ""
        else:
            ranked_relationships, matrix_data, error_msg = mine_correlations(df, selected_cols)
            if not error_msg:
                set_cached_correlation_results(df, ranked_relationships, matrix_data, selected_cols)
        
        if error_msg:
            st.error(error_msg)
        else:
            from utils.timeline_tracker import record_timeline_event
            record_timeline_event("Correlations Discovered", f"({len(ranked_relationships)} scanned)")
            
            # 5. Render dashboard
            render_correlation_dashboard(df, ranked_relationships, matrix_data)

# Execution block for standalone mode
if __name__ == "__main__":
    show_correlations_page(is_standalone=True)
