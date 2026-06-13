import pandas as pd
import numpy as np
import streamlit as st
import umap
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple

@st.cache_data(show_spinner="Running UMAP projection (this might take a few moments)...")
def run_umap_projection(
    df: pd.DataFrame, 
    selected_cols: List[str], 
    n_neighbors: int, 
    min_dist: float
) -> Tuple[pd.DataFrame, str]:
    """
    Preprocesses the dataset, applies UMAP dimensionality reduction, and returns
    a DataFrame containing the 2D coordinates ('UMAP_X', 'UMAP_Y') along with the original data.
    Returns:
        Tuple[pd.DataFrame, str]: (DataFrame with UMAP coords, error_message)
    """
    if not selected_cols:
        return pd.DataFrame(), "Please select at least one column for the projection."
        
    if len(df) < 3:
        return pd.DataFrame(), "UMAP projection requires at least 3 rows of data."
        
    try:
        # 1. Sub-select and copy
        df_sub = df[selected_cols].copy()
        
        # 2. Preprocess Datetimes to numeric epoch seconds
        for col in df_sub.columns:
            if pd.api.types.is_datetime64_any_dtype(df_sub[col]):
                try:
                    df_sub[col] = df_sub[col].astype('int64') // 10**9
                except Exception:
                    df_sub = df_sub.drop(columns=[col])
                    
        # 3. Identify types
        numeric_cols = df_sub.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df_sub.select_dtypes(exclude=[np.number]).columns.tolist()
        
        # 4. Handle Missing Values
        # Numeric Imputation
        for col in numeric_cols:
            if df_sub[col].isna().any():
                col_median = df_sub[col].median()
                if pd.isna(col_median):
                    df_sub[col] = df_sub[col].fillna(0.0)
                else:
                    df_sub[col] = df_sub[col].fillna(col_median)
                    
        # Categorical Imputation
        for col in categorical_cols:
            if df_sub[col].isna().any():
                df_sub[col] = df_sub[col].fillna("Missing")
                
        # 5. One-Hot Encoding for Categorical columns
        if categorical_cols:
            # Drop first to avoid collinearity
            df_encoded = pd.get_dummies(df_sub, columns=categorical_cols, drop_first=True)
        else:
            df_encoded = df_sub.copy()
            
        if df_encoded.shape[1] == 0:
            return pd.DataFrame(), "No valid features left after preprocessing."
            
        # 6. Standardize Features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_encoded)
        
        # 7. Clamp UMAP neighbors to prevent crashes
        # n_neighbors must be >= 2 and < total_rows
        adjusted_neighbors = min(int(n_neighbors), max(2, len(df) - 1))
        
        # 8. Run UMAP Projection
        reducer = umap.UMAP(
            n_neighbors=adjusted_neighbors,
            min_dist=float(min_dist),
            n_components=2,
            random_state=42
        )
        
        embedding = reducer.fit_transform(scaled_data)
        
        # 9. Build Output DataFrame
        df_out = df.copy()
        df_out['UMAP_X'] = embedding[:, 0]
        df_out['UMAP_Y'] = embedding[:, 1]
        
        return df_out, ""
        
    except Exception as e:
        return pd.DataFrame(), f"An error occurred during projection: {str(e)}"
