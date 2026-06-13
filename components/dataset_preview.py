import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from components.health_dashboard import render_health_dashboard

def render_dataset_preview(df: pd.DataFrame):
    """
    Renders the dataset preview section containing the interactive raw data viewer,
    column schema table, descriptive statistics, and correlation heatmaps.
    """
    st.markdown('<div class="section-title">🕵️‍♂️ Dataset Explorer</div>', unsafe_allow_html=True)
    
    # Create tabs for structured inspection
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Raw Data Preview", 
        "🩺 Dataset Health",
        "📋 Data Schema & Types", 
        "📈 Statistical Summary",
        "🔗 Correlation & Insights"
    ])
    
    with tab1:
        st.markdown("##### Browse Raw Data")
        st.markdown(
            "Use the built-in search and filters in the interactive table below to inspect records."
        )
        
        # Display DataFrame with streamlit's advanced interactive data editor/viewer
        st.dataframe(df, use_container_width=True, height=380)
        
    with tab2:
        render_health_dashboard(df)
        
    with tab3:
        st.markdown("##### Detailed Data Schema")
        st.markdown("An audit of column types, null counts, and memory footprint.")
        
        # Build schema summary dataframe
        schema_data = []
        for col in df.columns:
            non_null = df[col].count()
            nulls = df[col].isna().sum()
            null_pct = (nulls / len(df)) * 100
            dtype = str(df[col].dtype)
            unique = df[col].nunique()
            
            schema_data.append({
                "Column Name": col,
                "Data Type": dtype,
                "Non-Null Count": non_null,
                "Null Values": nulls,
                "Null %": f"{null_pct:.2f}%",
                "Unique Values": unique
            })
            
        schema_df = pd.DataFrame(schema_data)
        st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
    with tab4:
        st.markdown("##### Descriptive Statistics")
        
        # Split stats into numeric and categorical
        num_cols = df.select_dtypes(include=[np.number])
        cat_cols = df.select_dtypes(include=['object', 'category', 'boolean'])
        
        col_select1, col_select2 = st.columns(2)
        
        with col_select1:
            if not num_cols.empty:
                st.markdown("###### Numerical Variables")
                st.dataframe(num_cols.describe().T, use_container_width=True)
            else:
                st.info("No numerical variables found in this dataset.")
                
        with col_select2:
            if not cat_cols.empty:
                st.markdown("###### Categorical Variables")
                st.dataframe(cat_cols.describe().T, use_container_width=True)
            else:
                st.info("No categorical variables found in this dataset.")

    with tab5:
        st.markdown("##### Interactive Insights")
        
        num_df = df.select_dtypes(include=[np.number])
        
        # Visualizing correlation if multiple numeric columns exist
        if len(num_df.columns) > 1:
            st.markdown("###### Pearson Correlation Matrix")
            # Drop rows with NaN for correlation estimation
            corr_df = num_df.corr().round(3)
            
            # Use Plotly heat map
            fig = px.imshow(
                corr_df,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                labels=dict(color="Correlation")
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                margin=dict(l=40, r=40, t=20, b=40),
                coloraxis_colorbar=dict(
                    title="Correlation",
                    thicknessmode="pixels", thickness=15,
                    lenmode="fraction", len=0.7
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Upload a dataset with at least 2 numerical columns to view a Pearson correlation matrix.")
            
        # Visualizing missing values distribution if any
        missing_by_col = df.isna().sum()
        missing_by_col = missing_by_col[missing_by_col > 0]
        
        if not missing_by_col.empty:
            st.markdown("###### Missing Values Distribution")
            missing_plot_df = pd.DataFrame({
                'Column': missing_by_col.index,
                'Missing Count': missing_by_col.values,
                'Percentage': (missing_by_col.values / len(df) * 100).round(1)
            }).sort_values('Missing Count', ascending=False)
            
            fig_missing = px.bar(
                missing_plot_df,
                x='Column',
                y='Missing Count',
                text='Percentage',
                color='Missing Count',
                color_continuous_scale='YlOrRd',
                labels={'Missing Count': 'Count of Missing Cells'}
            )
            
            fig_missing.update_traces(
                texttemplate='%{text}%', 
                textposition='outside',
                marker_line_color='rgba(0,0,0,0)'
            )
            
            fig_missing.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                margin=dict(l=40, r=40, t=30, b=40),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.success("🎉 Quality Check: No missing values detected in the entire dataset!")
