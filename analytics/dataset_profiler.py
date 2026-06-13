import pandas as pd
import numpy as np
from analytics.trend_analysis import identify_datetime_columns

def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Scans the dataframe to classify the dataset type and recommend analytical modules.
    """
    cols = [str(c).lower() for c in df.columns]
    
    # Keyword sets
    customer_keywords = {'customer', 'user', 'client', 'age', 'gender', 'email', 'name', 'account_id', 'subscriber'}
    financial_keywords = {'revenue', 'profit', 'cost', 'price', 'salary', 'tax', 'margin', 'income', 'expense'}
    transaction_keywords = {'transaction', 'order', 'product', 'quantity', 'amount', 'purchase', 'cart', 'invoice'}
    
    # Scoring
    cust_score = sum(1 for c in cols if any(k in c for k in customer_keywords))
    fin_score = sum(1 for c in cols if any(k in c for k in financial_keywords))
    trans_score = sum(1 for c in cols if any(k in c for k in transaction_keywords))
    
    # Identify Date columns
    dt_cols = identify_datetime_columns(df)
    has_time = len(dt_cols) > 0
    
    # Classification Logic
    dataset_type = "General Tabular Dataset"
    icon = "📊"
    color = "#94a3b8"
    modules = ["Dataset DNA Profile", "Explorer Dashboard", "Correlation Discovery"]
    
    # Pick highest score
    max_score = max(cust_score, fin_score, trans_score)
    
    if max_score > 0:
        if trans_score == max_score:
            dataset_type = "Transaction Dataset"
            icon = "🛒"
            color = "#f59e0b"
            modules = ["Correlation Discovery", "Segment Discovery", "Semantic Data Map"]
        elif fin_score == max_score:
            dataset_type = "Financial Dataset"
            icon = "💰"
            color = "#10b981"
            modules = ["Anomaly Detection", "Correlation Discovery", "Executive Dashboard"]
        elif cust_score == max_score:
            dataset_type = "Customer Dataset"
            icon = "👥"
            color = "#3b82f6"
            modules = ["Segment Discovery", "Dataset DNA Profile", "Semantic Data Map"]
            
    # Override with Time Series if dates are present AND it's not strongly another type
    # Or just append Time Series to the name
    if has_time:
        if max_score == 0:
            dataset_type = "Time Series Dataset"
            icon = "⏳"
            color = "#8b5cf6"
            modules = ["Timeline Intelligence", "Future Forecasting", "Anomaly Detection"]
        else:
            dataset_type = f"Temporal {dataset_type}"
            modules.insert(0, "Timeline Intelligence")
            
    return {
        "type": dataset_type,
        "icon": icon,
        "color": color,
        "modules": modules[:3] # Recommend top 3
    }
