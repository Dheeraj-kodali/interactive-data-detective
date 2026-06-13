import pandas as pd
import numpy as np

def analyze_seasonality(df: pd.DataFrame, date_col: str, value_col: str) -> dict:
    """
    Extracts seasonal components and aggregates the data to find recurring cycles.
    """
    work_df = df[[date_col, value_col]].copy()
    
    if not pd.api.types.is_datetime64_any_dtype(work_df[date_col]):
        work_df[date_col] = pd.to_datetime(work_df[date_col], format='mixed', errors='coerce')
        
    work_df = work_df.dropna(subset=[date_col, value_col])
    
    if len(work_df) == 0:
        return {"error": "No valid data after date parsing."}
        
    # Extract components
    work_df['DayOfWeek'] = work_df[date_col].dt.day_name()
    work_df['DayOfWeek_Num'] = work_df[date_col].dt.dayofweek
    work_df['Month'] = work_df[date_col].dt.month_name()
    work_df['Month_Num'] = work_df[date_col].dt.month
    work_df['Quarter'] = "Q" + work_df[date_col].dt.quarter.astype(str)
    
    # Calculate Weekly Seasonality
    weekly_agg = work_df.groupby(['DayOfWeek_Num', 'DayOfWeek'])[value_col].mean().reset_index()
    weekly_agg = weekly_agg.sort_values('DayOfWeek_Num')
    
    # Calculate Monthly Seasonality
    monthly_agg = work_df.groupby(['Month_Num', 'Month'])[value_col].mean().reset_index()
    monthly_agg = monthly_agg.sort_values('Month_Num')
    
    # Calculate Quarterly Seasonality
    quarterly_agg = work_df.groupby('Quarter')[value_col].mean().reset_index()
    quarterly_agg = quarterly_agg.sort_values('Quarter')
    
    # Compute seasonality strength (Coefficient of Variation for each cycle)
    # Higher CV means more variance between the buckets, implying stronger seasonality
    weekly_cv = (weekly_agg[value_col].std() / weekly_agg[value_col].mean()) if weekly_agg[value_col].mean() != 0 else 0
    monthly_cv = (monthly_agg[value_col].std() / monthly_agg[value_col].mean()) if monthly_agg[value_col].mean() != 0 else 0
    quarterly_cv = (quarterly_agg[value_col].std() / quarterly_agg[value_col].mean()) if quarterly_agg[value_col].mean() != 0 else 0
    
    strengths = {
        "Weekly": weekly_cv,
        "Monthly": monthly_cv,
        "Quarterly": quarterly_cv
    }
    
    # Determine strongest pattern
    valid_strengths = {k: v for k, v in strengths.items() if not pd.isna(v)}
    strongest_cycle = max(valid_strengths, key=valid_strengths.get) if valid_strengths else "None"
    
    # Generate insights
    insights = []
    
    # Weekly insights
    if not weekly_agg.empty and len(weekly_agg) > 1:
        peak_day = weekly_agg.loc[weekly_agg[value_col].idxmax(), 'DayOfWeek']
        low_day = weekly_agg.loc[weekly_agg[value_col].idxmin(), 'DayOfWeek']
        peak_val = weekly_agg[value_col].max()
        low_val = weekly_agg[value_col].min()
        if peak_val > low_val * 1.1: # At least 10% variance to be notable
            insights.append({
                "text": f"<strong>{value_col}</strong> consistently peaks on <span class='insight-highlight'>{peak_day}s</span> and drops lowest on <span class='insight-highlight'>{low_day}s</span>.",
                "icon": "📅",
                "color": "#38bdf8"
            })
            
    # Monthly insights
    if not monthly_agg.empty and len(monthly_agg) > 2:
        peak_month = monthly_agg.loc[monthly_agg[value_col].idxmax(), 'Month']
        low_month = monthly_agg.loc[monthly_agg[value_col].idxmin(), 'Month']
        peak_val = monthly_agg[value_col].max()
        low_val = monthly_agg[value_col].min()
        if peak_val > low_val * 1.15: # At least 15% variance to be notable
            insights.append({
                "text": f"Historically, <span class='insight-highlight'>{peak_month}</span> is the strongest month of the year, while <span class='insight-highlight'>{low_month}</span> is the weakest.",
                "icon": "📆",
                "color": "#a78bfa"
            })
            
    if not insights:
        insights.append({
            "text": "No significant recurring seasonal patterns detected across the selected time frames.",
            "icon": "⚖️",
            "color": "#94a3b8"
        })

    return {
        "weekly": weekly_agg,
        "monthly": monthly_agg,
        "quarterly": quarterly_agg,
        "strengths": valid_strengths,
        "strongest_cycle": strongest_cycle,
        "insights": insights,
        "error": None
    }
