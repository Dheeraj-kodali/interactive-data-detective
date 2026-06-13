import pandas as pd
import numpy as np
import streamlit as st
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Tuple

def preprocess_clustering_data(df: pd.DataFrame, selected_cols: List[str]) -> np.ndarray:
    """
    Sub-selects columns, handles datetimes, imputes null values, 
    one-hot encodes categorical fields, and scales with StandardScaler.
    Returns scaled features as a NumPy array.
    """
    df_sub = df[selected_cols].copy()
    
    # Convert datetimes to epoch seconds
    for col in df_sub.columns:
        if pd.api.types.is_datetime64_any_dtype(df_sub[col]):
            try:
                df_sub[col] = df_sub[col].astype('int64') // 10**9
            except Exception:
                df_sub = df_sub.drop(columns=[col])
                
    # Identify column groups
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
        raise ValueError("No valid features remain after preprocessing.")
        
    # Scale features
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_encoded)
    return scaled_data

@st.cache_data(show_spinner="Running clustering model...")
def calculate_clusters(
    df: pd.DataFrame, 
    selected_cols: List[str], 
    algorithm: str, 
    params: Dict[str, Any]
) -> Tuple[List[str], str]:
    """
    Performs clustering and returns list of string labels and any error message.
    """
    if not selected_cols:
        return [], "Please select at least one feature for clustering."
    if len(df) < 2:
        return [], "Dataset must have at least 2 rows for clustering."
        
    try:
        scaled_data = preprocess_clustering_data(df, selected_cols)
        
        if algorithm == "K-Means":
            k = int(params.get("n_clusters", 4))
            # KMeans might fail if k > number of rows
            k = min(k, len(df))
            model = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels = model.fit_predict(scaled_data)
            label_strings = [f"Cluster {val}" for val in labels]
            
        elif algorithm == "DBSCAN":
            eps = float(params.get("eps", 0.5))
            min_samples = int(params.get("min_samples", 5))
            model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = model.fit_predict(scaled_data)
            
            # Map labels (-1 is Noise, others are clusters)
            label_strings = []
            for val in labels:
                if val == -1:
                    label_strings.append("Outliers/Noise")
                else:
                    label_strings.append(f"Cluster {val}")
        else:
            return [], f"Unknown algorithm: {algorithm}"
            
        return label_strings, ""
        
    except Exception as e:
        return [], f"An error occurred during clustering calculation: {str(e)}"

def analyze_distinguishing_features(
    df: pd.DataFrame, 
    labels: List[str], 
    selected_cols: List[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Analyzes which numerical features distinguish each cluster from the global mean.
    Uses z-score calculation: Z = (cluster_mean - global_mean) / global_std.
    """
    results = {}
    unique_labels = sorted(list(set(labels)))
    
    # Filter numeric features from selected columns
    numeric_cols = df[selected_cols].select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return {label: [] for label in unique_labels}
        
    # Calculate global means and standard deviations
    global_means = df[numeric_cols].mean()
    global_stds = df[numeric_cols].std().replace(0, 1.0) # Avoid division by zero
    
    df_temp = df.copy()
    df_temp['__cluster_label'] = labels
    
    for label in unique_labels:
        cluster_df = df_temp[df_temp['__cluster_label'] == label]
        cluster_len = len(cluster_df)
        
        if cluster_len == 0:
            results[label] = []
            continue
            
        cluster_means = cluster_df[numeric_cols].mean()
        distinguishing = []
        
        for col in numeric_cols:
            mean_c = cluster_means[col]
            mean_g = global_means[col]
            std_g = global_stds[col]
            
            if pd.isna(mean_c) or pd.isna(mean_g) or pd.isna(std_g):
                continue
                
            # Z-score metric
            z_score = (mean_c - mean_g) / std_g
            
            # Absolute z-score > 0.4 indicates deviation
            if abs(z_score) >= 0.4:
                direction = "higher" if z_score > 0 else "lower"
                distinguishing.append({
                    'feature': col,
                    'z_score': round(z_score, 2),
                    'cluster_mean': round(float(mean_c), 2),
                    'global_mean': round(float(mean_g), 2),
                    'direction': direction,
                    'description': f"Values are significantly {direction} than average (Z-Score: {z_score:+.2f})"
                })
                
        # Sort by absolute strength of z-score
        distinguishing = sorted(distinguishing, key=lambda x: abs(x['z_score']), reverse=True)
        results[label] = distinguishing[:5] # Top 5 traits
        
    return results
