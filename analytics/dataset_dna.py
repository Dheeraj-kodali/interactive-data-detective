import pandas as pd
import numpy as np
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import warnings

def _downsample_if_needed(df: pd.DataFrame, max_rows: int = 5000) -> pd.DataFrame:
    """Safely downsample dataset to ensure fast calculation."""
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42)
    return df

def calculate_quality_score(df: pd.DataFrame) -> float:
    """
    Score based on missing values and duplicates.
    0% missing/dupes = 100.
    """
    if df.empty:
        return 0.0
    
    total_cells = df.size
    missing_cells = df.isna().sum().sum()
    missing_pct = missing_cells / total_cells if total_cells > 0 else 1.0
    
    total_rows = len(df)
    duplicate_rows = df.duplicated().sum()
    duplicate_pct = duplicate_rows / total_rows if total_rows > 0 else 1.0
    
    # Penalize missing values more heavily
    missing_penalty = min(100.0, missing_pct * 200.0)
    duplicate_penalty = min(100.0, duplicate_pct * 100.0)
    
    score = 100.0 - (missing_penalty * 0.7 + duplicate_penalty * 0.3)
    return max(0.0, round(score, 1))

def calculate_complexity_score(df: pd.DataFrame) -> float:
    """
    Score based on number of features relative to rows and cardinality.
    Higher score = More complex.
    """
    if df.empty:
        return 0.0
        
    num_rows, num_cols = df.shape
    
    # Dimension ratio (cols per 1000 rows)
    dim_ratio = min(100.0, (num_cols / max(1, num_rows / 1000.0)) * 5.0)
    
    # Cardinality of categorical features
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    avg_cardinality = 0.0
    if len(cat_cols) > 0:
        unique_counts = [df[col].nunique() for col in cat_cols]
        # Cap cardinality score contribution at 100 unique values
        avg_cardinality = min(100.0, np.mean(unique_counts) * 2.0)
        
    score = (dim_ratio * 0.5) + (avg_cardinality * 0.5)
    # We want to scale it so a typical dataset gets around 40-70.
    # We will log-scale roughly or just return the min of 100.
    return min(100.0, max(0.0, round(score, 1)))

def calculate_clusterability_score(df: pd.DataFrame) -> float:
    """
    Score based on silhouette score of KMeans(k=3).
    Higher silhouette = higher clusterability.
    """
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) < 1 or len(df) < 10:
        return 0.0
        
    df_samp = _downsample_if_needed(df.dropna(subset=num_cols))
    if len(df_samp) < 10:
        return 0.0
        
    try:
        X = StandardScaler().fit_transform(df_samp[num_cols])
        # Add tiny noise to prevent constant data issues
        X += np.random.normal(0, 1e-4, X.shape)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kmeans = KMeans(n_clusters=min(3, len(X)-1), random_state=42, n_init='auto')
            labels = kmeans.fit_predict(X)
            
            if len(set(labels)) > 1:
                sil_score = silhouette_score(X, labels)
                # Map silhouette (-1 to 1) to (0 to 100)
                # Typically sil_score is between 0 and 0.6.
                mapped_score = min(100.0, max(0.0, (sil_score + 0.1) * 125.0))
                return round(mapped_score, 1)
    except Exception:
        pass
        
    return 20.0 # fallback

def calculate_anomaly_risk_score(df: pd.DataFrame) -> float:
    """
    Score based on anomaly rate. High anomaly rate = Lower risk score (lower stability).
    Or wait, if we want high score = good dataset, then Anomaly Resistance Score.
    Let's call it 'Anomaly Stability' or just invert the risk.
    """
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) < 1 or len(df) < 10:
        return 100.0
        
    df_samp = _downsample_if_needed(df.dropna(subset=num_cols))
    if len(df_samp) < 10:
        return 100.0
        
    try:
        X = StandardScaler().fit_transform(df_samp[num_cols])
        iso = IsolationForest(contamination='auto', random_state=42)
        labels = iso.fit_predict(X)
        
        anomaly_rate = (labels == -1).sum() / len(labels)
        # Typically anomaly rate is 0.01 to 0.15.
        # Score = 100 if rate is 0, 0 if rate is 0.2
        score = 100.0 - min(100.0, anomaly_rate * 500.0)
        return max(0.0, round(score, 1))
    except Exception:
        return 50.0

def calculate_feature_richness_score(df: pd.DataFrame) -> float:
    """
    Mix of numeric, categorical, and datetime.
    """
    if df.empty:
        return 0.0
        
    num_cols = len(df.select_dtypes(include=[np.number]).columns)
    cat_cols = len(df.select_dtypes(exclude=[np.number, 'datetime']).columns)
    dt_cols = len(df.select_dtypes(include=['datetime']).columns)
    
    total = max(1, len(df.columns))
    
    # Calculate Shannon entropy of the column type distribution to encourage diversity
    p_num = num_cols / total
    p_cat = cat_cols / total
    p_dt = dt_cols / total
    
    entropy = 0
    for p in [p_num, p_cat, p_dt]:
        if p > 0:
            entropy -= p * np.log(p)
            
    # Max entropy for 3 classes is ln(3) ~ 1.098
    diversity_score = (entropy / 1.098) * 100.0
    
    # Boost if there are many columns
    volume_boost = min(30.0, total * 1.5)
    
    score = (diversity_score * 0.7) + (volume_boost)
    return min(100.0, max(0.0, round(score, 1)))

@st.cache_data(show_spinner="Extracting Dataset DNA...")
def generate_dataset_dna(df: pd.DataFrame) -> dict:
    """
    Generates all 5 DNA scores and the overall score.
    """
    quality = calculate_quality_score(df)
    complexity = calculate_complexity_score(df)
    clusterability = calculate_clusterability_score(df)
    stability = calculate_anomaly_risk_score(df)
    richness = calculate_feature_richness_score(df)
    
    overall = round((quality + complexity + clusterability + stability + richness) / 5.0, 1)
    
    return {
        "Quality": quality,
        "Complexity": complexity,
        "Clusterability": clusterability,
        "Stability": stability,
        "Richness": richness,
        "Overall": overall
    }
