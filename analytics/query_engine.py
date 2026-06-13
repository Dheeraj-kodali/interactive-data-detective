"""
Query Engine Module

This module provides natural language processing and interpretation for the 
Investigation Console. It parses user queries, detects analytical intent,
identifies relevant dataset columns, and returns structured responses.
"""
import pandas as pd
import re
import numpy as np
from typing import Dict, Any, Optional, List
import plotly.express as px

def detect_intent(query: str) -> Dict[str, str]:
    """
    Detects the analytical intent from a natural language query.
    
    Args:
        query (str): The natural language query from the user.
        
    Returns:
        Dict[str, str]: A dictionary containing the detected intent.
    """
    query_lower = query.lower()
    
    # Define keywords for intent matching
    intents = {
        'average': ['average', 'avg'],
        'mean': ['mean'],
        'maximum': ['maximum', 'max', 'highest', 'most', 'largest'],
        'minimum': ['minimum', 'min', 'lowest', 'least', 'smallest'],
        'sum': ['sum', 'total'],
        'count': ['count', 'how many', 'number of'],
        'trend': ['trend', 'over time', 'history'],
        'correlation': ['correlation', 'correlations', 'correlate', 'related', 'relationship'],
        'anomaly': ['anomaly', 'anomalies', 'outlier', 'outliers', 'unusual', 'weird'],
        'segment': ['segment', 'segments', 'segmentation'],
        'cluster': ['cluster', 'clusters', 'clustering', 'group'],
    }
    
    for intent, keywords in intents.items():
        if any(keyword in query_lower for keyword in keywords):
            return {"intent": intent}
            
    return {"intent": "unknown"}

def detect_date_column(df: pd.DataFrame) -> Optional[str]:
    """
    Automatically detects the primary date or timestamp column in the dataframe.
    
    Args:
        df (pd.DataFrame): The active dataset.
        
    Returns:
        Optional[str]: The name of the date column if found, otherwise None.
    """
    # 1. Look for existing datetime columns
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
            
    # 2. Look for columns with date/time in the name that can be parsed
    for col in df.columns:
        col_lower = str(col).lower()
        if any(k in col_lower for k in ['date', 'time', 'year', 'month', 'timestamp']):
            try:
                pd.to_datetime(df[col].dropna().head(10))
                return col
            except Exception:
                continue
                
    # 3. Fallback: try parsing any column as datetime
    for col in df.columns:
        try:
            pd.to_datetime(df[col].dropna().head(5))
            return col
        except Exception:
            continue
            
    return None

def detect_column(query: str, df: pd.DataFrame) -> Optional[str]:
    """
    Identifies which dataframe column the user is referring to in their query.
    
    Args:
        query (str): The natural language query.
        df (pd.DataFrame): The active dataset.
        
    Returns:
        Optional[str]: The exact column name if found, otherwise None.
    """
    query_lower = query.lower()
    columns = df.columns.tolist()
    
    # 1. Exact match (checking clean string with spaces vs underscore)
    for col in columns:
        col_lower = str(col).lower()
        col_clean = col_lower.replace('_', ' ')
        if col_clean in query_lower or col_lower in query_lower:
            return col
            
    # 2. Synonym expansion for common business terms (e.g. revenue -> sales, total_sales_usd)
    synonyms = {
        'revenue': ['sales', 'price', 'amount', 'income', 'turnover'],
        'sales': ['revenue', 'price', 'amount', 'qty', 'quantity'],
        'profit': ['earnings', 'margin', 'gain']
    }
    
    for key, syns in synonyms.items():
        pattern = rf"\b{re.escape(key)}\b"
        if re.search(pattern, query_lower):
            # Look for columns that contain the key or any of the synonyms
            candidates = [key] + syns
            for candidate in candidates:
                for col in columns:
                    col_lower = str(col).lower()
                    if candidate in col_lower:
                        return col

    # 3. Token overlap using word boundaries (handles spaces, underscores, etc.)
    for col in columns:
        col_lower = str(col).lower()
        col_tokens = re.split(r'[\s_]+', col_lower)
        for token in col_tokens:
            if len(token) > 2:
                # Use regex word boundaries to prevent matching substrings of other words (e.g. 'age' in 'average')
                if re.search(rf"\b{re.escape(token)}\b", query_lower):
                    return col

    return None

def answer_query(query: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Processes the query, computes the requested metric or generates a chart, and returns structured output.
    
    Args:
        query (str): The natural language query.
        df (pd.DataFrame): The active dataset.
        
    Returns:
        Dict[str, Any]: Structured dictionary containing the result or error.
            Success format (metric):
            {
                "type": "metric",
                "title": "...",
                "value": ...
            }
            Success format (chart):
            {
                "type": "chart",
                "chart_type": "line",
                "title": "...",
                "figure": fig
            }
            Success format (correlation):
            {
                "type": "correlation",
                "title": "...",
                "ranked_relationships": ...,
                "matrix_data": ...,
                "columns_analyzed": ...
            }
            Error format:
            {
                "type": "error",
                "message": "..."
            }
    """
    # 1. Extract context
    intent_dict = detect_intent(query)
    intent = intent_dict.get("intent", "unknown")
    
    supported_intents = ['average', 'mean', 'maximum', 'minimum', 'sum', 'count', 'trend', 'correlation', 'anomaly']
    if intent not in supported_intents:
        return {
            "type": "error",
            "message": f"Unsupported or unknown analytical intent '{intent}'. Try asking for average, mean, maximum, minimum, sum, count, trend, correlation, or anomaly."
        }
        
    # Correlation and anomaly don't target a single column; other intents do.
    column = None
    if intent not in ['correlation', 'anomaly']:
        column = detect_column(query, df)
        if not column:
            return {
                "type": "error",
                "message": "Could not identify a matching column in the dataset based on your query."
            }
        
    # 2. Compute Result
    try:
        # Special case: Correlation Intent
        if intent == 'correlation':
            import streamlit as st
            from analytics.correlation_engine import (
                mine_correlations,
                get_cached_correlation_results,
                set_cached_correlation_results
            )
            
            # Check cache first
            ranked_relationships, matrix_data, selected_cols = get_cached_correlation_results(df)
            
            if ranked_relationships is None:
                # Select columns to analyze, similar to pages/correlations.py
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
                
                selected_cols = numeric_cols.copy()
                for col in categorical_cols:
                    if df[col].nunique() < 30:
                        selected_cols.append(col)
                        
                if len(selected_cols) < 2:
                    return {
                        "type": "error",
                        "message": "Need at least 2 columns in the dataset to perform correlation analysis."
                    }
                    
                ranked_relationships, matrix_data, error_msg = mine_correlations(df, selected_cols)
                
                if error_msg:
                    return {
                        "type": "error",
                        "message": error_msg
                    }
                
                # Save into cache
                set_cached_correlation_results(df, ranked_relationships, matrix_data, selected_cols)
                
            # Determine query subtype
            query_lower = query.lower()
            query_subtype = 'general'
            if any(k in query_lower for k in ['strongest', 'highest', 'max', 'best', 'most correlated']):
                query_subtype = 'strongest'
            elif any(k in query_lower for k in ['top', 'rank', 'best 10', 'top 10', 'list']):
                query_subtype = 'top'
                
            strongest_rel = ranked_relationships[0] if ranked_relationships else None
            
            return {
                "type": "correlation",
                "title": "Correlation Analysis",
                "ranked_relationships": ranked_relationships,
                "matrix_data": matrix_data,
                "columns_analyzed": selected_cols,
                "query_subtype": query_subtype,
                "strongest_relationship": strongest_rel
            }

        # Special case: Anomaly Intent
        if intent == 'anomaly':
            import streamlit as st
            
            # Check if columns exist in df
            if 'Is_Anomaly' in df.columns and 'Anomaly_Score' in df.columns:
                labels = df['Is_Anomaly'].tolist()
                scores = df['Anomaly_Score'].tolist()
                anomaly_count = (df['Is_Anomaly'] == 'Anomaly').sum()
            else:
                from analytics.anomaly_detection import calculate_anomalies
                # Select numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if not numeric_cols:
                    return {
                        "type": "error",
                        "message": "Anomaly detection requires at least one numeric column in the dataset."
                    }
                    
                labels, scores, error_msg = calculate_anomalies(df, numeric_cols, 0.05)
                if error_msg:
                    return {
                        "type": "error",
                        "message": error_msg
                    }
                    
                # Store back in dataframe and st.session_state
                df['Is_Anomaly'] = labels
                df['Anomaly_Score'] = scores
                
                anomaly_count = (pd.Series(labels) == "Anomaly").sum()
                max_score = np.max(scores) if len(scores) > 0 else 0.0
                st.session_state["anomaly_results"] = {
                    "total_anomalies": int(anomaly_count),
                    "max_score": float(max_score)
                }
                
            # Determine query subtype
            query_lower = query.lower()
            query_subtype = 'general'
            if any(k in query_lower for k in ['top', 'extreme', 'most', 'worst', 'highest', 'rank']):
                query_subtype = 'top'
            elif any(k in query_lower for k in ['count', 'number', 'how many', 'total']):
                query_subtype = 'count'
            elif any(k in query_lower for k in ['show', 'list', 'table', 'records', 'outliers']):
                query_subtype = 'show'
                
            return {
                "type": "anomaly",
                "title": "Anomaly Detection Analysis",
                "labels": labels,
                "scores": scores,
                "anomaly_count": int(anomaly_count),
                "query_subtype": query_subtype
            }

        # Special case: Segment / Cluster Intent
        if intent in ['segment', 'cluster']:
            import streamlit as st
            
            # Check if cluster labels already exist in dataframe
            if 'Cluster_Label' in df.columns:
                labels = df['Cluster_Label'].tolist()
            else:
                from analytics.clustering import calculate_clusters
                # Select numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if not numeric_cols:
                    return {
                        "type": "error",
                        "message": "Segment Discovery requires at least one numeric column in the dataset."
                    }
                    
                labels, error_msg = calculate_clusters(df, numeric_cols, "K-Means", {"n_clusters": 4})
                if error_msg:
                    return {
                        "type": "error",
                        "message": error_msg
                    }
                    
                df['Cluster_Label'] = labels
                
                # Update st.session_state segment results
                unique_clusters = len(set(labels) - {"Outliers/Noise"})
                valid_clusters = [l for l in labels if l != "Outliers/Noise"]
                largest_cluster = pd.Series(valid_clusters).value_counts().index[0] if valid_clusters else "None"
                st.session_state["segment_results"] = {
                    "unique_clusters": unique_clusters,
                    "largest_cluster": largest_cluster
                }
                
            # Check if UMAP coordinates already exist in dataframe
            if 'UMAP_X' not in df.columns or 'UMAP_Y' not in df.columns:
                from analytics.umap_engine import run_umap_projection
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    df_mapped, error_msg = run_umap_projection(
                        df, 
                        numeric_cols, 
                        n_neighbors=min(15, len(df)), 
                        min_dist=0.1
                    )
                    if not error_msg:
                        df['UMAP_X'] = df_mapped['UMAP_X']
                        df['UMAP_Y'] = df_mapped['UMAP_Y']
            
            # Determine query subtype
            query_lower = query.lower()
            query_subtype = 'general'
            if any(k in query_lower for k in ['largest', 'biggest', 'most populated', 'dominant', 'main']):
                query_subtype = 'largest'
            elif any(k in query_lower for k in ['summary', 'profile', 'traits', 'characteristics', 'describe']):
                query_subtype = 'summary'
                
            has_umap = 'UMAP_X' in df.columns and 'UMAP_Y' in df.columns
            
            return {
                "type": "segment",
                "title": "Segment Discovery Analysis",
                "labels": labels,
                "has_umap": has_umap,
                "query_subtype": query_subtype
            }

        # Special case: Trend Chart
        if intent == 'trend':
            date_col = detect_date_column(df)
            if not date_col:
                return {
                    "type": "error",
                    "message": f"Could not identify a date column in the dataset to plot a trend over time for '{column}'."
                }
                
            # Copy dataframe columns we need
            temp_df = df[[date_col, column]].copy()
            temp_df[date_col] = pd.to_datetime(temp_df[date_col])
            temp_df = temp_df.dropna(subset=[date_col, column])
            
            if not pd.api.types.is_numeric_dtype(temp_df[column]):
                return {
                    "type": "error",
                    "message": f"Cannot plot trend on non-numeric column '{column}'."
                }
                
            # Aggregate by month (sum of total monthly sales/profit/revenue)
            temp_df['Month'] = temp_df[date_col].dt.to_period('M').dt.to_timestamp()
            monthly_data = temp_df.groupby('Month')[column].sum().reset_index()
            monthly_data = monthly_data.sort_values('Month')
            
            if monthly_data.empty:
                return {
                    "type": "error",
                    "message": f"No valid data points found to generate a monthly trend for '{column}'."
                }
                
            # Generate Plotly line chart
            fig = px.line(
                monthly_data,
                x='Month',
                y=column,
                title=f"Monthly {column} Trend"
            )
            
            fig.update_traces(
                line_color='#38bdf8', 
                line_width=3, 
                marker=dict(size=8, color='#a78bfa', line_width=1.5, line_color='#f8fafc')
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.05)',
                    title="Date"
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.05)',
                    title=column
                )
            )
            
            return {
                "type": "chart",
                "chart_type": "line",
                "title": f"Monthly {column} Trend",
                "figure": fig
            }

        # Otherwise, standard metrics
        series = df[column]
        
        # Determine Title
        title_mapping = {
            'average': f"Average {column}",
            'mean': f"Mean {column}",
            'maximum': f"Maximum {column}",
            'minimum': f"Minimum {column}",
            'sum': f"Total {column}",
            'count': f"Count of {column}"
        }
        title = title_mapping.get(intent, f"{intent.capitalize()} {column}")
        
        # Compute Value using pandas
        if intent in ['average', 'mean']:
            if not pd.api.types.is_numeric_dtype(series):
                return {
                    "type": "error",
                    "message": f"Cannot compute {intent} on non-numeric column '{column}'."
                }
            value = series.mean()
            
        elif intent == 'sum':
            if not pd.api.types.is_numeric_dtype(series):
                return {
                    "type": "error",
                    "message": f"Cannot compute sum on non-numeric column '{column}'."
                }
            value = series.sum()
            
        elif intent == 'maximum':
            value = series.max()
            
        elif intent == 'minimum':
            value = series.min()
            
        elif intent == 'count':
            value = series.count()
            
        else:
            return {
                "type": "error",
                "message": f"Intent '{intent}' is registered as supported but has no computation path."
            }
            
        # Convert numpy/pandas scalar to Python type
        if hasattr(value, 'item'):
            value = value.item()
            
        if pd.isna(value):
            value = None
            
        return {
            "type": "metric",
            "title": title,
            "value": value
        }
        
    except Exception as e:
        return {
            "type": "error",
            "message": f"Computation error: {str(e)}"
        }
