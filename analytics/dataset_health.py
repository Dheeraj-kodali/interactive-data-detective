import pandas as pd
import numpy as np
from typing import Dict, Any, List

def calculate_health_scores(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates statistical data quality health scores for the given DataFrame.
    Returns scores out of 100 (high is better) and metadata for detailed auditing.
    """
    scores = {}
    audit_details = {}
    
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    
    # ------------------ 1. COMPLETENESS SCORE ------------------
    if total_cells == 0:
        completeness_score = 100.0
        missing_cells = 0
        missing_pct = 0.0
    else:
        missing_cells = int(df.isna().sum().sum())
        missing_pct = (missing_cells / total_cells) * 100
        completeness_score = max(0.0, 100.0 - missing_pct)
        
    scores['completeness'] = round(completeness_score, 1)
    
    # Column-level missing details
    missing_by_col = df.isna().sum()
    col_missing_details = []
    for col in df.columns:
        cnt = int(missing_by_col[col])
        if cnt > 0:
            col_missing_details.append({
                'column': col,
                'missing_count': cnt,
                'percentage': round((cnt / total_rows) * 100, 1) if total_rows > 0 else 0.0
            })
    # Sort by highest missing count
    col_missing_details = sorted(col_missing_details, key=lambda x: x['missing_count'], reverse=True)
    audit_details['missing_columns'] = col_missing_details
    audit_details['total_missing_cells'] = missing_cells
    audit_details['missing_percentage'] = round(missing_pct, 2)
    
    # ------------------ 2. CONSISTENCY SCORE ------------------
    if total_rows == 0:
        consistency_score = 100.0
        duplicate_rows = 0
        duplicate_pct = 0.0
    else:
        try:
            duplicate_rows = int(df.duplicated(keep='first').sum())
        except Exception:
            # Handle cases with unhashable types gracefully
            duplicate_rows = 0
        duplicate_pct = (duplicate_rows / total_rows) * 100
        consistency_score = max(0.0, 100.0 - duplicate_pct)
        
    scores['consistency'] = round(consistency_score, 1)
    audit_details['duplicate_rows'] = duplicate_rows
    audit_details['duplicate_percentage'] = round(duplicate_pct, 2)
    
    # ------------------ 3. OUTLIER HEALTH SCORE ------------------
    numeric_cols = df.select_dtypes(include=[np.number])
    total_numeric_cells = 0
    total_outliers = 0
    col_outlier_details = []
    
    for col in numeric_cols.columns:
        col_data = df[col].dropna()
        col_count = len(col_data)
        if col_count == 0:
            continue
            
        total_numeric_cells += col_count
        
        # Calculate IQR
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Count outliers
        outliers_mask = (col_data < lower_bound) | (col_data > upper_bound)
        outliers_count = int(outliers_mask.sum())
        total_outliers += outliers_count
        
        if outliers_count > 0:
            col_outlier_details.append({
                'column': col,
                'outliers_count': outliers_count,
                'percentage': round((outliers_count / col_count) * 100, 1),
                'lower_bound': round(float(lower_bound), 3),
                'upper_bound': round(float(upper_bound), 3),
                'min_value': round(float(col_data.min()), 3),
                'max_value': round(float(col_data.max()), 3)
            })
            
    # Sort by highest outlier percentage
    col_outlier_details = sorted(col_outlier_details, key=lambda x: x['percentage'], reverse=True)
    audit_details['outliers_columns'] = col_outlier_details
    audit_details['total_outlier_cells'] = total_outliers
    audit_details['total_numeric_cells'] = total_numeric_cells
    
    if total_numeric_cells == 0:
        outlier_health_score = 100.0
        outlier_pct = 0.0
    else:
        outlier_pct = (total_outliers / total_numeric_cells) * 100
        outlier_health_score = max(0.0, 100.0 - outlier_pct)
        
    scores['outlier_health'] = round(outlier_health_score, 1)
    scores['outlier_risk'] = round(outlier_pct, 1) # Represent outlier density
    
    # ------------------ 4. OVERALL HEALTH SCORE ------------------
    # Weighted combinations: 40% Completeness, 30% Consistency, 30% Outlier Health
    overall_health = (
        scores['completeness'] * 0.40 +
        scores['consistency'] * 0.30 +
        scores['outlier_health'] * 0.30
    )
    scores['overall'] = round(overall_health, 1)
    
    return {
        'scores': scores,
        'details': audit_details
    }
