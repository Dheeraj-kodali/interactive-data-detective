import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Tuple

def preprocess_anomaly_data(df: pd.DataFrame, selected_cols: List[str]) -> np.ndarray:
    """
    Sub-selects features, converts datetimes to timestamps,
    imputes missing values, encodes categories, and standardizes data.
    """
    df_sub = df[selected_cols].copy()
    
    # Datetime to epoch
    for col in df_sub.columns:
        if pd.api.types.is_datetime64_any_dtype(df_sub[col]):
            try:
                df_sub[col] = df_sub[col].astype('int64') // 10**9
            except Exception:
                df_sub = df_sub.drop(columns=[col])
                
    # Identify types
    numeric_cols = df_sub.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df_sub.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Impute missing values
    for col in numeric_cols:
        if df_sub[col].isna().any():
            median_val = df_sub[col].median()
            df_sub[col] = df_sub[col].fillna(median_val if not pd.isna(median_val) else 0.0)
            
    for col in categorical_cols:
        if df_sub[col].isna().any():
            df_sub[col] = df_sub[col].fillna("Missing")
            
    # Encode categorical variables
    if categorical_cols:
        df_encoded = pd.get_dummies(df_sub, columns=categorical_cols, drop_first=True)
    else:
        df_encoded = df_sub.copy()
        
    if df_encoded.shape[1] == 0:
        raise ValueError("No features available after preprocessing.")
        
    # Scale data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_encoded)
    return scaled_data

@st.cache_data(show_spinner="Analyzing records for anomalies...")
def calculate_anomalies(
    df: pd.DataFrame, 
    selected_cols: List[str], 
    contamination: float
) -> Tuple[List[str], List[float], str]:
    """
    Fits an IsolationForest model and returns a list of labels ('Normal'/'Anomaly'),
    normalized anomaly scores, and an error message (if any).
    """
    if not selected_cols:
        return [], [], "Please select at least one column for anomaly analysis."
    if len(df) < 5:
        return [], [], "Anomaly detection requires at least 5 records to fit the Isolation Forest model."
        
    try:
        scaled_data = preprocess_anomaly_data(df, selected_cols)
        
        # Fit Isolation Forest
        model = IsolationForest(
            contamination=float(contamination),
            random_state=42,
            n_jobs=-1
        )
        # fit_predict returns 1 for normal, -1 for anomaly
        preds = model.fit_predict(scaled_data)
        
        # Calculate raw anomaly score (higher means more anomalous)
        # score_samples returns negative values (lower path length -> lower score -> anomaly)
        # We negate it so higher values mean higher anomaly density
        raw_scores = -model.score_samples(scaled_data)
        
        # Normalize scores to [0, 1] range
        min_s = raw_scores.min()
        max_s = raw_scores.max()
        if max_s > min_s:
            normalized_scores = (raw_scores - min_s) / (max_s - min_s)
        else:
            normalized_scores = np.zeros_like(raw_scores)
            
        labels = ["Anomaly" if p == -1 else "Normal" for p in preds]
        scores_list = [float(s) for s in normalized_scores]
        
        return labels, scores_list, ""
        
    except Exception as e:
        return [], [], f"An error occurred during anomaly calculation: {str(e)}"

def explain_anomaly_record(
    df: pd.DataFrame, 
    row_idx: int, 
    selected_cols: List[str], 
    cluster_labels: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Compares the specific anomalous row values to its parent cluster average (if clustering exists)
    or global dataset averages to explain why it is anomalous.
    Returns:
        List of dicts containing feature deviance statistics.
    """
    explanations = []
    numeric_cols = df[selected_cols].select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols or row_idx >= len(df) or row_idx < 0:
        return []
        
    row_values = df.iloc[row_idx]
    
    # Determine the comparison group (cluster vs global)
    is_cluster_comp = False
    cluster_val = None
    if cluster_labels is not None and len(cluster_labels) == len(df):
        cluster_val = cluster_labels[row_idx]
        # Compare against cluster average if it belongs to a valid cluster (excluding Outliers/Noise)
        if cluster_val and cluster_val != "Outliers/Noise":
            is_cluster_comp = True
            
    df_temp = df.copy()
    if is_cluster_comp:
        df_temp['__cluster'] = cluster_labels
        comp_group = df_temp[df_temp['__cluster'] == cluster_val][numeric_cols]
        group_label = f"Cluster '{cluster_val}'"
    else:
        comp_group = df[numeric_cols]
        group_label = "Global Dataset"
        
    # Calculate group means and standard deviations
    group_means = comp_group.mean()
    group_stds = comp_group.std().replace(0, 1.0) # Prevent division by zero
    
    for col in numeric_cols:
        val = float(row_values[col])
        g_mean = float(group_means[col])
        g_std = float(group_stds[col])
        
        if pd.isna(val) or pd.isna(g_mean) or pd.isna(g_std):
            continue
            
        z_score = (val - g_mean) / g_std
        
        # Absolute z-score > 1.5 indicates substantial deviance for an outlier
        if abs(z_score) >= 1.5:
            direction = "higher" if z_score > 0 else "lower"
            explanations.append({
                'feature': col,
                'value': round(val, 2),
                'group_mean': round(g_mean, 2),
                'z_score': round(z_score, 2),
                'direction': direction,
                'group_label': group_label,
                'text': f"**{col}** is `{val}` (average for {group_label} is `{g_mean}`), deviating by **{z_score:+.2f}** standard deviations ({direction})"
            })
            
    # Sort by absolute strength of deviation
    explanations = sorted(explanations, key=lambda x: abs(x['z_score']), reverse=True)
    return explanations
