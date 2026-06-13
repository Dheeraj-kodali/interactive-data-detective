import streamlit as st
import pandas as pd
import numpy as np

def format_memory_usage(bytes_value: int) -> str:
    """Format memory usage bytes into human-readable text."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def render_stats_cards(df: pd.DataFrame):
    """
    Renders gorgeous premium stats metrics cards for the dataset.
    """
    # Calculate stats
    row_count = len(df)
    col_count = len(df.columns)
    
    try:
        memory_bytes = df.memory_usage(deep=True).sum()
    except Exception:
        memory_bytes = df.memory_usage().sum()
    memory_str = format_memory_usage(memory_bytes)
    
    total_cells = row_count * col_count
    missing_cells = df.isna().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    
    try:
        duplicate_rows = df.duplicated().sum()
    except Exception:
        duplicate_rows = 0
        
    # Column types breakdown
    num_cols = len(df.select_dtypes(include=[np.number]).columns)
    cat_cols = len(df.select_dtypes(include=['object', 'category']).columns)
    date_cols = len(df.select_dtypes(include=['datetime', 'datetimetz']).columns)
    other_cols = col_count - (num_cols + cat_cols + date_cols)

    # Custom HTML Grid for statistics cards
    st.markdown(
        f"""
        <div class="stats-grid">
            <div class="kpi-card">
                <div class="kpi-icon" style="color: #38bdf8;">📊</div>
                <h3 class="kpi-title">Row Count</h3>
                <div class="kpi-value text-teal">{row_count:,}</div>
                <span style="font-size: 0.75rem; color: #64748b; margin-top: 5px;">Total data points</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: #a78bfa;">🗂️</div>
                <h3 class="kpi-title">Column Count</h3>
                <div class="kpi-value text-purple">{col_count}</div>
                <span style="font-size: 0.75rem; color: #64748b; margin-top: 5px;">{num_cols} Num • {cat_cols} Cat • {date_cols} Date</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: #94a3b8;">💾</div>
                <h3 class="kpi-title">Memory Footprint</h3>
                <div class="kpi-value">{memory_str}</div>
                <span style="font-size: 0.75rem; color: #64748b; margin-top: 5px;">In-memory size</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: #f43f5e;">🔍</div>
                <h3 class="kpi-title">Missing Values</h3>
                <div class="kpi-value {'text-rose' if missing_cells > 0 else ''}">{missing_cells:,}</div>
                <span style="font-size: 0.75rem; color: #64748b; margin-top: 5px;">{missing_pct:.2f}% of total cells</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: #fbbf24;">👥</div>
                <h3 class="kpi-title">Duplicate Rows</h3>
                <div class="kpi-value {'text-amber' if duplicate_rows > 0 else ''}">{duplicate_rows:,}</div>
                <span style="font-size: 0.75rem; color: #64748b; margin-top: 5px;">Identical records</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
