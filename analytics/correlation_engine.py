import pandas as pd
import numpy as np
import streamlit as st
from sklearn.metrics import mutual_info_score
from typing import List, Dict, Any, Tuple, Optional

def get_binned_series(s: pd.Series) -> pd.Series:
    """Helper to convert continuous numeric features to binned categories for MI."""
    s_clean = s.dropna()
    if s_clean.empty:
        return s_clean
    if pd.api.types.is_numeric_dtype(s_clean):
        if s_clean.nunique() <= 10:
            return s_clean.astype(str)
        else:
            return pd.cut(s_clean, bins=10, labels=False, duplicates='drop').astype(str)
    else:
        return s_clean.astype(str)

def calculate_mi_score(df: pd.DataFrame, col1: str, col2: str) -> float:
    """Calculates Mutual Information by aligning index and binning continuous columns."""
    if col1 == col2:
        df_clean = df[[col1]].dropna()
        if len(df_clean) < 10:
            return 0.0
        s1 = get_binned_series(df_clean[col1])
        return float(mutual_info_score(s1, s1))
        
    df_clean = df[[col1, col2]].dropna()
    if len(df_clean) < 10:
        return 0.0
        
    s1 = get_binned_series(df_clean[col1])
    s2 = get_binned_series(df_clean[col2])
    
    # Ensure inner alignment
    s1, s2 = s1.align(s2, join='inner')
    if s1.empty or s2.empty:
        return 0.0
        
    return float(mutual_info_score(s1, s2))

@st.cache_data(show_spinner="Mining dataset for relationships...")
def mine_correlations(df: pd.DataFrame, columns: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], str]:
    """
    Computes Pearson, Spearman, and Mutual Info between column pairs.
    Ranks them by strength and returns a list of ranked relationships.
    """
    if len(columns) < 2:
        return [], {}, "Please select at least 2 columns to perform correlation analysis."
        
    # Validation: Ensure selected columns are unique
    if len(set(columns)) != len(columns):
        import collections
        duplicates = [item for item, count in collections.Counter(columns).items() if count > 1]
        return [], {}, f"Expected unique column names, got duplicates: {duplicates}. Please resolve duplicate columns."
        
    relationships = []
    matrix_data = {
        'pearson': {},
        'spearman': {},
        'mutual_info': {}
    }
    
    try:
        # Pre-initialize matrices
        for col in columns:
            matrix_data['pearson'][col] = {}
            matrix_data['spearman'][col] = {}
            matrix_data['mutual_info'][col] = {}
            
        n_cols = len(columns)
        for i in range(n_cols):
            col1 = columns[i]
            # Self correlation
            matrix_data['pearson'][col1][col1] = 1.0
            matrix_data['spearman'][col1][col1] = 1.0
            matrix_data['mutual_info'][col1][col1] = calculate_mi_score(df, col1, col1)
            
            for j in range(i + 1, n_cols):
                col2 = columns[j]
                
                # Check types
                is_num1 = pd.api.types.is_numeric_dtype(df[col1])
                is_num2 = pd.api.types.is_numeric_dtype(df[col2])
                
                p_val, s_val = np.nan, np.nan
                
                if is_num1 and is_num2:
                    df_clean = df[[col1, col2]].dropna()
                    if len(df_clean) >= 5:
                        p_val = float(df_clean[col1].corr(df_clean[col2], method='pearson'))
                        s_val = float(df_clean[col1].corr(df_clean[col2], method='spearman'))
                        
                mi_val = calculate_mi_score(df, col1, col2)
                
                # Update symmetric matrices
                matrix_data['pearson'][col1][col2] = p_val
                matrix_data['pearson'][col2][col1] = p_val
                
                matrix_data['spearman'][col1][col2] = s_val
                matrix_data['spearman'][col2][col1] = s_val
                
                matrix_data['mutual_info'][col1][col2] = mi_val
                matrix_data['mutual_info'][col2][col1] = mi_val
                
                relationships.append({
                    'var1': col1,
                    'var2': col2,
                    'pearson': p_val,
                    'spearman': s_val,
                    'mutual_info': mi_val,
                    'is_numeric': (is_num1 and is_num2)
                })
                
        # Classify Findings
        findings = {
            'positive': [],
            'negative': [],
            'nonlinear': []
        }
        
        for rel in relationships:
            # Positive linear
            if not pd.isna(rel['pearson']) and rel['pearson'] >= 0.5:
                findings['positive'].append(rel)
            # Negative linear
            elif not pd.isna(rel['pearson']) and rel['pearson'] <= -0.5:
                findings['negative'].append(rel)
            # Non-linear check (high Mutual Info but low Pearson)
            elif rel['is_numeric'] and not pd.isna(rel['pearson']) and rel['mutual_info'] >= 0.18 and abs(rel['pearson']) < 0.2:
                findings['nonlinear'].append(rel)
                
        # Sort findings by absolute strength
        findings['positive'] = sorted(findings['positive'], key=lambda x: x['pearson'], reverse=True)
        findings['negative'] = sorted(findings['negative'], key=lambda x: x['pearson']) # Most negative first
        findings['nonlinear'] = sorted(findings['nonlinear'], key=lambda x: x['mutual_info'], reverse=True)
        
        # Sort general relationships by strongest correlation or MI
        ranked_relationships = sorted(
            relationships,
            key=lambda x: max(abs(x['pearson']) if not pd.isna(x['pearson']) else 0.0, x['mutual_info']),
            reverse=True
        )
        
        return ranked_relationships, matrix_data, ""
        
    except Exception as e:
        return [], {}, f"An error occurred during correlation mining: {str(e)}"

def get_cached_correlation_results(df: pd.DataFrame) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]], Optional[List[str]]]:
    """
    Retrieves cached correlation results from st.session_state if they exist
    and match the shape and columns of the provided dataframe.
    """
    if 'correlation_results' not in st.session_state:
        return None, None, None
        
    cache = st.session_state['correlation_results']
    if not isinstance(cache, dict):
        return None, None, None
        
    # Validate cache against current dataframe
    cache_shape = cache.get('df_shape')
    cache_columns = cache.get('df_columns')
    
    if cache_shape != df.shape or cache_columns != list(df.columns):
        # Cache is invalid/for a different dataframe
        return None, None, None
        
    return cache.get('ranked_relationships'), cache.get('matrix_data'), cache.get('columns_analyzed')

def set_cached_correlation_results(df: pd.DataFrame, ranked_relationships: List[Dict[str, Any]], matrix_data: Dict[str, Any], columns_analyzed: List[str]):
    """
    Stores correlation results in st.session_state.
    """
    st.session_state['correlation_results'] = {
        'df_id': id(df),
        'df_shape': df.shape,
        'df_columns': list(df.columns),
        'columns_analyzed': columns_analyzed,
        'ranked_relationships': ranked_relationships,
        'matrix_data': matrix_data
    }
