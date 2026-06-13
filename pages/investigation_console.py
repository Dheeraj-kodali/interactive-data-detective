import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any

def generate_dynamic_examples(df: pd.DataFrame) -> List[str]:
    cols = df.columns.tolist()
    cols_lower = [c.lower() for c in cols]
    
    # Helper to find column by synonyms
    def find_col(synonyms, default_col_type='numeric'):
        for syn in synonyms:
            for c, cl in zip(cols, cols_lower):
                if syn in cl:
                    return c
        # Fallback
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        if default_col_type == 'numeric' and numeric_cols:
            return numeric_cols[0]
        elif default_col_type == 'categorical' and categorical_cols:
            return categorical_cols[0]
        return cols[0] if cols else ""

    # Find columns
    sales_col = find_col(['sales', 'price', 'quantity'])
    revenue_col = find_col(['revenue', 'sales', 'spend'])
    profit_col = find_col(['profit', 'earnings', 'margin'])
    segment_col = find_col(['segment', 'cluster', 'category', 'region'], default_col_type='categorical')
    
    # Format examples
    examples = [
        f"What is average {sales_col}?" if sales_col else "What is average sales?",
        f"Show {revenue_col} trend." if revenue_col else "Show revenue trend.",
        "Show anomalies.",
        "Show strongest correlations.",
        f"Largest {segment_col}." if segment_col else "Largest customer segment.",
        f"Total {profit_col}." if profit_col else "Total profit."
    ]
    return examples

def show_investigation_console_page(is_standalone=True):
    # Initialize basic config and styles if running directly
    if is_standalone:
        st.set_page_config(
            page_title="Data Detective - Investigation Console",
            page_icon="🕵️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        from utils.styling import inject_global_css
        inject_global_css()
        
        from components.sidebar import render_sidebar
        render_sidebar()

    # The page should load only if a dataset has already been uploaded
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset from the sidebar to access the Investigation Console.")
        return

    # Initialize session state variables for examples click
    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = ""
    if 'auto_submit' not in st.session_state:
        st.session_state.auto_submit = False

    # Clean UI Structure
    st.markdown('<div class="section-title">🕵️ Investigation Console</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem;">
            Ask Data Detective about your dataset. Formulate your question clearly and the engine will query your data to find the answer.
        </p>
    """, unsafe_allow_html=True)

    # Dynamic Clickable Examples
    st.markdown('<div style="font-weight: 600; font-size: 0.95rem; color: #f8fafc; margin-bottom: 10px;">💡 Try asking:</div>', unsafe_allow_html=True)
    examples = generate_dynamic_examples(st.session_state.df)
    
    # Grid of buttons
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    col_ex4, col_ex5, col_ex6 = st.columns(3)
    
    with col_ex1:
        if st.button(f"📊 {examples[0]}", use_container_width=True, key="ex_btn_0"):
            st.session_state.selected_example = examples[0]
            st.session_state.auto_submit = True
            st.rerun()
    with col_ex2:
        if st.button(f"📈 {examples[1]}", use_container_width=True, key="ex_btn_1"):
            st.session_state.selected_example = examples[1]
            st.session_state.auto_submit = True
            st.rerun()
    with col_ex3:
        if st.button(f"🚨 {examples[2]}", use_container_width=True, key="ex_btn_2"):
            st.session_state.selected_example = examples[2]
            st.session_state.auto_submit = True
            st.rerun()
    with col_ex4:
        if st.button(f"🔗 {examples[3]}", use_container_width=True, key="ex_btn_3"):
            st.session_state.selected_example = examples[3]
            st.session_state.auto_submit = True
            st.rerun()
    with col_ex5:
        if st.button(f"🧩 {examples[4]}", use_container_width=True, key="ex_btn_4"):
            st.session_state.selected_example = examples[4]
            st.session_state.auto_submit = True
            st.rerun()
    with col_ex6:
        if st.button(f"💰 {examples[5]}", use_container_width=True, key="ex_btn_5"):
            st.session_state.selected_example = examples[5]
            st.session_state.auto_submit = True
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Input Area
    default_val = st.session_state.selected_example
    
    with st.form("investigation_form"):
        question = st.text_area(
            "What would you like to know?",
            value=default_val,
            placeholder="e.g., Are there any missing values in the sales column?",
            height=120
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("🔍 Ask", use_container_width=True)
            
    should_execute = False
    query_text = ""
    
    if submit_button:
        query_text = question.strip()
        should_execute = True
    elif st.session_state.auto_submit and st.session_state.selected_example:
        query_text = st.session_state.selected_example
        should_execute = True
        
    if should_execute:
        # Clear auto_submit and selected_example so it does not persist across future manual reruns
        st.session_state.auto_submit = False
        st.session_state.selected_example = ""
        
        if query_text:
            question = query_text
            # Import query engine logic
            from analytics.query_engine import answer_query
            
            with st.spinner("Analyzing dataset..."):
                result = answer_query(query_text, st.session_state.df)
                
            if result.get("type") == "metric":
                st.success("Query processed successfully!")
                
                # Display the result in a clean metrics display
                col_metric, _ = st.columns([1, 2])
                with col_metric:
                    val = result["value"]
                    # Format float nicely if it is float
                    if isinstance(val, float):
                        val_str = f"{val:,.2f}"
                    elif isinstance(val, int):
                        val_str = f"{val:,}"
                    else:
                        val_str = str(val)
                    st.metric(label=result["title"], value=val_str)
                    
                st.info(f"Analyzed question: *\"{question.strip()}\"*")
                
            elif result.get("type") == "chart":
                st.success("Query processed successfully and trend chart generated!")
                
                # Render the Plotly chart inside a container
                st.plotly_chart(result["figure"], use_container_width=True)
                
                st.info(f"Analyzed question: *\"{question.strip()}\"*")
                
            elif result.get("type") == "correlation":
                st.success("Correlation discovery analysis completed successfully!")
                
                # Check query subtype and display custom visual highlights
                query_subtype = result.get("query_subtype", "general")
                if query_subtype == "strongest":
                    strongest = result.get("strongest_relationship")
                    if strongest:
                        pearson_val = strongest['pearson']
                        dir_str = "positive" if pearson_val > 0 else "negative"
                        strength_str = "strong" if abs(pearson_val) >= 0.7 else "moderate" if abs(pearson_val) >= 0.4 else "weak"
                        st.markdown(
                            f"""
                            <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 12px; padding: 20px; margin-bottom: 25px;">
                                <h4 style="color: #10b981; margin: 0 0 10px 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    🎯 Strongest Correlation Detected
                                </h4>
                                <p style="color: #cbd5e1; margin: 0; font-size: 1rem; line-height: 1.6;">
                                    The strongest relationship in the dataset is between <strong>{strongest['var1']}</strong> and <strong>{strongest['var2']}</strong>.
                                    This represents a <strong>{strength_str} {dir_str}</strong> correlation.
                                </p>
                                <ul style="margin: 10px 0 0 0; padding-left: 20px; color: #94a3b8; font-size: 0.9rem;">
                                    <li>Pearson (Linear): <code>{strongest['pearson']:+.3f}</code></li>
                                    <li>Spearman (Rank): <code>{strongest['spearman']:+.3f}</code></li>
                                    <li>Mutual Information: <code>{strongest['mutual_info']:.3f}</code></li>
                                </ul>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                elif query_subtype == "top":
                    st.markdown(
                        """
                        <div style="background: rgba(167, 139, 250, 0.04); border: 1px solid rgba(167, 139, 250, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #a78bfa; margin: 0 0 8px 0; font-weight: 700;">🏆 Top Relationships</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Below are the top 10 strongest variable pairings ranked by their linear correlation and information overlap.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div style="background: rgba(56, 189, 248, 0.04); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #38bdf8; margin: 0 0 8px 0; font-weight: 700;">🔗 Correlation Discovery</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Displaying comprehensive relationship analysis across your dataset features.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # 1. Summary Statistics
                st.markdown("##### 📊 Summary Statistics")
                ranked_rels = result["ranked_relationships"]
                
                total_pairs = len(ranked_rels)
                pos_count = len([r for r in ranked_rels if not pd.isna(r['pearson']) and r['pearson'] >= 0.5])
                neg_count = len([r for r in ranked_rels if not pd.isna(r['pearson']) and r['pearson'] <= -0.5])
                nonlinear_count = len([r for r in ranked_rels if r['is_numeric'] and not pd.isna(r['pearson']) and r['mutual_info'] >= 0.18 and abs(r['pearson']) < 0.2])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Scanned Pairs", f"{total_pairs}")
                with col2:
                    st.metric("Strong Positive (Pearson >= 0.5)", f"{pos_count}")
                with col3:
                    st.metric("Strong Negative (Pearson <= -0.5)", f"{neg_count}")
                with col4:
                    st.metric("Potential Non-Linear", f"{nonlinear_count}")
                
                # 2. Correlation Matrix Heatmap
                st.markdown("##### 🗺️ Pearson Correlation Heatmap")
                matrix_df = pd.DataFrame(result["matrix_data"]['pearson'])
                
                import plotly.express as px
                fig = px.imshow(
                    matrix_df.round(3),
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    zmin=-1.0,
                    zmax=1.0,
                    labels=dict(color="Correlation")
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#cbd5e1',
                    margin=dict(l=40, r=40, t=20, b=40)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 3. Top 10 Relationships
                st.markdown("##### 🏆 Top 10 Relationships (Ranked by Strength)")
                top_relationships = []
                for r in ranked_rels[:10]:
                    pearson = f"{r['pearson']:.3f}" if not pd.isna(r['pearson']) else "N/A"
                    spearman = f"{r['spearman']:.3f}" if not pd.isna(r['spearman']) else "N/A"
                    mi = f"{r['mutual_info']:.3f}"
                    top_relationships.append({
                        "Variable 1": r['var1'],
                        "Variable 2": r['var2'],
                        "Pearson (Linear)": pearson,
                        "Spearman (Rank)": spearman,
                        "Mutual Information": mi,
                        "Type": "Numeric-Numeric" if r['is_numeric'] else "Mixed/Categorical"
                    })
                st.dataframe(pd.DataFrame(top_relationships), use_container_width=True, hide_index=True)
                
                st.info(f"Analyzed question: *\"{question.strip()}\"*")

            elif result.get("type") == "anomaly":
                st.success("Anomaly detection analysis completed successfully!")
                
                # Check query subtype and display custom header message
                query_subtype = result.get("query_subtype", "general")
                if query_subtype == "top":
                    st.markdown(
                        """
                        <div style="background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #ef4444; margin: 0 0 8px 0; font-weight: 700;">🏆 Top Anomalies & Outliers</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Here are the most extreme anomalies in your dataset, ranked by their Isolation Forest anomaly score.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif query_subtype == "count":
                    st.markdown(
                        f"""
                        <div style="background: rgba(245, 158, 11, 0.04); border: 1px solid rgba(245, 158, 11, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #f59e0b; margin: 0 0 8px 0; font-weight: 700;">🚨 Outlier Count Summary</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Isolation Forest has flagged <strong>{result['anomaly_count']:,}</strong> records as anomalous. See detailed breakdown below.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div style="background: rgba(56, 189, 248, 0.04); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #38bdf8; margin: 0 0 8px 0; font-weight: 700;">🚨 Anomaly Detection Findings</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Displaying identified outliers and statistical anomalies in the dataset features.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # 4. Display anomaly count
                anomaly_count = result["anomaly_count"]
                total_rows = len(st.session_state.df)
                anomaly_pct = (anomaly_count / total_rows * 100) if total_rows > 0 else 0.0
                
                st.markdown("##### 🚨 Anomaly Summary")
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.metric("Anomalies Detected", f"{anomaly_count:,}")
                with col_c2:
                    st.metric("Outlier Ratio", f"{anomaly_pct:.2f}%")
                with col_c3:
                    st.metric("Normal Records", f"{total_rows - anomaly_count:,}")
                    
                # 3. Show anomaly chart
                st.markdown("##### 📊 Anomaly Distribution Chart")
                df_dist = pd.DataFrame({
                    'Status': ['Normal', 'Anomaly'],
                    'Count': [total_rows - anomaly_count, anomaly_count]
                })
                import plotly.express as px
                fig = px.pie(
                    df_dist,
                    values='Count',
                    names='Status',
                    color='Status',
                    color_discrete_map={'Normal': '#10b981', 'Anomaly': '#ef4444'},
                    hole=0.4,
                    title="Data Point Classification"
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#cbd5e1',
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 2. Show anomaly table
                st.markdown("##### 🕵️‍♂️ Anomalous Records Table (Top 10)")
                df_temp = st.session_state.df.copy()
                df_temp['Is_Anomaly'] = result["labels"]
                df_temp['Anomaly_Score'] = result["scores"]
                
                df_anom = df_temp[df_temp['Is_Anomaly'] == "Anomaly"].sort_values('Anomaly_Score', ascending=False)
                
                if df_anom.empty:
                    st.success("No anomalies detected based on the current contamination rate.")
                else:
                    st.dataframe(df_anom.head(10), use_container_width=True)
                    
                st.info(f"Analyzed question: *\"{question.strip()}\"*")

            elif result.get("type") == "segment":
                st.success("Segment Discovery analysis completed successfully!")
                
                df = st.session_state.df
                labels = result["labels"]
                
                # Check query subtype and display custom callouts
                query_subtype = result.get("query_subtype", "general")
                if query_subtype == "largest":
                    # Find largest segment
                    label_series = pd.Series(labels)
                    valid_counts = label_series[label_series != "Outliers/Noise"].value_counts()
                    if not valid_counts.empty:
                        largest_name = valid_counts.index[0]
                        largest_size = valid_counts.iloc[0]
                        largest_pct = (largest_size / len(labels)) * 100
                        st.markdown(
                            f"""
                            <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 12px; padding: 20px; margin-bottom: 25px;">
                                <h4 style="color: #10b981; margin: 0 0 10px 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    👑 Largest Segment Identified
                                </h4>
                                <p style="color: #cbd5e1; margin: 0; font-size: 1.05rem; line-height: 1.6;">
                                    The dominant cluster is <strong>{largest_name}</strong> containing <strong>{largest_size:,}</strong> records,
                                    which represents <strong>{largest_pct:.2f}%</strong> of the entire dataset.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                elif query_subtype == "summary":
                    st.markdown(
                        """
                        <div style="background: rgba(167, 139, 250, 0.04); border: 1px solid rgba(167, 139, 250, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #a78bfa; margin: 0 0 8px 0; font-weight: 700;">🧩 Cluster & Segment Summary</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Below is a statistical summary of the naturally occurring segments in your dataset.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div style="background: rgba(56, 189, 248, 0.04); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 25px;">
                            <h4 style="color: #38bdf8; margin: 0 0 8px 0; font-weight: 700;">🕵️ Segment Discovery Findings</h4>
                            <p style="color: #cbd5e1; margin: 0; font-size: 0.95rem;">
                                Showing details of mathematical clusters and natural segments found in the dataset.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # 1. Segment sizes
                st.markdown("##### 👥 Segment Sizes & Distribution")
                label_series = pd.Series(labels)
                distribution = label_series.value_counts()
                total_rows = len(df)
                
                df_dist = pd.DataFrame({
                    'Segment': distribution.index,
                    'Count': distribution.values,
                    'Percentage': (distribution.values / total_rows * 100).round(2)
                }).sort_values('Segment')
                
                col_s1, col_s2 = st.columns([1, 1])
                with col_s1:
                    st.dataframe(df_dist, use_container_width=True, hide_index=True)
                with col_s2:
                    import plotly.express as px
                    fig_pie = px.pie(
                        df_dist,
                        values='Count',
                        names='Segment',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Safe,
                        title="Segment Population Size"
                    )
                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#cbd5e1',
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=True
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                # 2. Segment profiles
                st.markdown("##### 🧬 Segment Profiles (Distinguishing Traits)")
                from analytics.clustering import analyze_distinguishing_features
                
                # Identify numeric features
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                profiles = analyze_distinguishing_features(df, labels, numeric_cols)
                
                for seg_name in df_dist['Segment'].tolist():
                    with st.expander(f"🔍 Profile: {seg_name}"):
                        seg_count = int(distribution[seg_name])
                        seg_pct = (seg_count / total_rows * 100)
                        st.markdown(f"**Segment Population**: **{seg_count:,} rows** ({seg_pct:.2f}% of dataset)")
                        
                        traits = profiles.get(seg_name, [])
                        if not traits:
                            st.info("No numerical traits show strong deviations for this segment.")
                        else:
                            for trait in traits:
                                indicator = "🟢" if trait['direction'] == "higher" else "🔴"
                                st.markdown(
                                    f"""
                                    - **{trait['feature']}**: {indicator} {trait['description']}.  
                                      Cluster Mean: `{trait['cluster_mean']}` vs. Global Average: `{trait['global_mean']}`.
                                    """
                                )

                # 3. Segment visualization
                if result.get("has_umap"):
                    st.markdown("##### 🗺️ UMAP 2D Projection Space")
                    import plotly.express as px
                    fig_umap = px.scatter(
                        df,
                        x='UMAP_X',
                        y='UMAP_Y',
                        color='Cluster_Label',
                        hover_name=df.index,
                        color_discrete_sequence=px.colors.qualitative.Safe,
                        labels={'UMAP_X': 'Dimension 1', 'UMAP_Y': 'Dimension 2'},
                        title="UMAP Semantic Projection colored by Segment"
                    )
                    fig_umap.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#cbd5e1',
                        margin=dict(l=20, r=20, t=40, b=20),
                        legend=dict(bgcolor='rgba(15, 23, 42, 0.5)')
                    )
                    st.plotly_chart(fig_umap, use_container_width=True)
                else:
                    st.info("💡 Run the **Semantic Data Map** page to view the UMAP 2D Segment Projection.")
                    
                st.info(f"Analyzed question: *\"{question.strip()}\"*")
            else:
                # Handle errors and unsupported query types gracefully
                error_msg = result.get("message", "An unknown error occurred during computation.")
                st.error(f"❌ {error_msg}")
                
                # If intent was unknown/unsupported, show a helpful guidance note
                if "intent" in error_msg.lower() or "unsupported" in error_msg.lower():
                    st.info(
                        "💡 **Data Detective Tips:**\n"
                        "- Supported calculations: **average**, **mean**, **maximum**, **minimum**, **sum**, **count**.\n"
                        "- Specify the column name clearly (e.g. *Sales*, *Revenue*, *Profit*).\n"
                        "- Examples: *'What is average Sales?'*, *'Show maximum Revenue'*, *'Total Profit'*."
                    )
                elif "column" in error_msg.lower():
                    # Mention the available columns in the dataframe for convenience
                    available_cols = ", ".join(f"`{col}`" for col in st.session_state.df.columns)
                    st.info(
                        f"💡 **Column Matching Tips:**\n"
                        f"- Make sure the column name is spelled similarly to columns in your dataset.\n"
                        f"- Available columns in this dataset: {available_cols}"
                    )
        else:
            st.error("Please enter a question before submitting.")

if __name__ == "__main__":
    show_investigation_console_page(is_standalone=True)
