import streamlit as st
import pandas as pd
from analytics.dataset_health import calculate_health_scores

def get_status_color(score: float) -> str:
    """Returns color styling and label based on health score threshold."""
    if score >= 80.0:
        return "#10b981", "Excellent", "🟢"  # Green
    elif score >= 50.0:
        return "#f59e0b", "Fair (Warning)", "🟡"  # Amber
    else:
        return "#ef4444", "Critical Danger", "🔴"  # Red

def get_gradient_css(color: str) -> str:
    """Helper to return CSS gradient starting with the designated score color."""
    if color == "#10b981":
        return "linear-gradient(90deg, #10b981 0%, #059669 100%)"
    elif color == "#f59e0b":
        return "linear-gradient(90deg, #fbbf24 0%, #d97706 100%)"
    else:
        return "linear-gradient(90deg, #f43f5e 0%, #e11d48 100%)"

def render_health_dashboard(df: pd.DataFrame):
    """
    Computes and renders the dataset health dashboard with custom visual progress bars,
    status badges, and detail logs.
    """
    st.markdown('<div class="section-title">🩺 Dataset Health Report</div>', unsafe_allow_html=True)
    
    # Calculate health analytics
    health_results = calculate_health_scores(df)
    scores = health_results['scores']
    details = health_results['details']
    
    overall_score = scores['overall']
    overall_color, overall_label, overall_emoji = get_status_color(overall_score)
    
    # Render Overall Health Header
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.7) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 5px solid {overall_color};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
        ">
            <div>
                <h4 style="margin: 0; font-size: 1.1rem; color: #94a3b8; font-weight: 500;">Overall Data Health</h4>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
                    <span style="font-size: 1.8rem; font-weight: 800; color: #ffffff;">{overall_score}</span>
                    <span style="font-size: 1.1rem; color: #cbd5e1;">/ 100</span>
                </div>
            </div>
            <div style="
                background: {overall_color}1a;
                border: 1px solid {overall_color}33;
                border-radius: 20px;
                padding: 6px 16px;
                display: flex;
                align-items: center;
                gap: 6px;
            ">
                <span style="font-size: 0.9rem;">{overall_emoji}</span>
                <span style="font-weight: 700; color: {overall_color}; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.03em;">{overall_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Grid of three metrics components
    comp_score = scores['completeness']
    cons_score = scores['consistency']
    out_score = scores['outlier_health']
    
    c_color, _, _ = get_status_color(comp_score)
    cs_color, _, _ = get_status_color(cons_score)
    o_color, _, _ = get_status_color(out_score)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class="stat-card" style="min-height: 140px;">
                <div class="stat-header">
                    <span class="stat-title">Completeness</span>
                    <span class="stat-icon">📄</span>
                </div>
                <h3 class="stat-value" style="color: {c_color}; -webkit-text-fill-color: {c_color};">{comp_score}%</h3>
                <div style="background-color: rgba(255,255,255,0.04); border-radius: 8px; height: 7px; width: 100%; margin: 8px 0;">
                    <div style="background: {get_gradient_css(c_color)}; width: {comp_score}%; height: 100%; border-radius: 8px;"></div>
                </div>
                <span class="stat-subtext" style="color: #cbd5e1;">{details['total_missing_cells']:,} missing values ({details['missing_percentage']}% of cells)</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class="stat-card" style="min-height: 140px;">
                <div class="stat-header">
                    <span class="stat-title">Consistency</span>
                    <span class="stat-icon">👥</span>
                </div>
                <h3 class="stat-value" style="color: {cs_color}; -webkit-text-fill-color: {cs_color};">{cons_score}%</h3>
                <div style="background-color: rgba(255,255,255,0.04); border-radius: 8px; height: 7px; width: 100%; margin: 8px 0;">
                    <div style="background: {get_gradient_css(cs_color)}; width: {cons_score}%; height: 100%; border-radius: 8px;"></div>
                </div>
                <span class="stat-subtext" style="color: #cbd5e1;">{details['duplicate_rows']:,} duplicate rows ({details['duplicate_percentage']}% of records)</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="stat-card" style="min-height: 140px;">
                <div class="stat-header">
                    <span class="stat-title">Outlier Cleanliness</span>
                    <span class="stat-icon">📈</span>
                </div>
                <h3 class="stat-value" style="color: {o_color}; -webkit-text-fill-color: {o_color};">{out_score}%</h3>
                <div style="background-color: rgba(255,255,255,0.04); border-radius: 8px; height: 7px; width: 100%; margin: 8px 0;">
                    <div style="background: {get_gradient_css(o_color)}; width: {out_score}%; height: 100%; border-radius: 8px;"></div>
                </div>
                <span class="stat-subtext" style="color: #cbd5e1;">{details['total_outlier_cells']:,} outliers in {len(df.select_dtypes(include=['number']).columns)} numeric cols</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # Detailed Audit Findings Section
    st.markdown('<div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc; margin-top: 30px; margin-bottom: 15px;">🔍 Detailed Audit Logs</div>', unsafe_allow_html=True)
    
    # 1. Missing Values Expander
    with st.expander("📄 Missing Values Audit Report", expanded=False):
        if details['total_missing_cells'] == 0:
            st.success("Perfect Completeness! No null/missing values found in the dataset.")
        else:
            st.warning(f"Found {details['total_missing_cells']:,} missing cells. Here is the column-level summary:")
            missing_table = pd.DataFrame(details['missing_columns'])
            # Format columns name for presentation
            missing_table.columns = ["Column Name", "Missing Rows Count", "Percentage of Rows"]
            st.dataframe(missing_table, use_container_width=True, hide_index=True)
            
            st.markdown(
                """
                > **💡 Detective's Imputation Recommendation**:
                > - For numerical columns, consider replacing missing values with the **Median** if distributions are skewed, or the **Mean** if normally distributed.
                > - For categorical fields, impute using the **Mode** (most frequent class) or represent them as a new category (e.g. *"Unknown"*).
                """
            )
            
    # 2. Duplicate Records Expander
    with st.expander("👥 Duplicate Records Audit Report", expanded=False):
        if details['duplicate_rows'] == 0:
            st.success("Perfect Consistency! All rows represent unique records.")
        else:
            st.warning(f"Found {details['duplicate_rows']:,} exact duplicate rows ({details['duplicate_percentage']}% of dataset).")
            # Show a small preview of duplicates if possible
            try:
                dupes_df = df[df.duplicated(keep=False)]
                st.markdown("###### Preview of Duplicated Rows (showing up to 5 examples):")
                st.dataframe(dupes_df.head(5), use_container_width=True)
            except Exception:
                pass
                
            st.markdown(
                """
                > **💡 Detective's Duplication Recommendation**:
                > - Verify if duplicates are log entries representing separate recurring events or pure system errors.
                > - If they are redundant duplicates, consider dropping them using pandas `df.drop_duplicates()`.
                """
            )
            
    # 3. Outlier Audit Expander
    with st.expander("📈 Outlier Detection Audit Report (IQR Method)", expanded=False):
        if len(df.select_dtypes(include=['number']).columns) == 0:
            st.info("No numerical variables found in the dataset to perform outlier analysis.")
        elif details['total_outlier_cells'] == 0:
            st.success("No statistical outliers detected in any of the numerical columns using the IQR threshold $[Q1 - 1.5 \\times IQR, Q3 + 1.5 \\times IQR]$.")
        else:
            st.warning(f"Detected {details['total_outlier_cells']:,} outlier cells in numeric variables.")
            outliers_table = pd.DataFrame(details['outliers_columns'])
            # Format headers
            outliers_table.columns = ["Column", "Outlier Count", "Outlier %", "Lower Bound", "Upper Bound", "Min Value", "Max Value"]
            st.dataframe(outliers_table, use_container_width=True, hide_index=True)
            
            st.markdown(
                """
                > **💡 Detective's Outlier Recommendation**:
                > - Outliers can represent critical anomalies (e.g., fraud, failures) or natural variances in heavily skewed distributions (e.g., sales sizes).
                > - If outliers are due to measurement/data entry errors, apply winsorization or filter them out before model training.
                """
            )
