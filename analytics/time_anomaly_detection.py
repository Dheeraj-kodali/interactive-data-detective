import pandas as pd
import numpy as np

def detect_time_anomalies(df: pd.DataFrame, date_col: str, value_col: str, agg_freq: str = 'D', window: int = 14) -> dict:
    """
    Detects point anomalies (transient spikes and drops) in a time series using a robust Rolling IQR method.
    """
    work_df = df[[date_col, value_col]].copy()
    
    if not pd.api.types.is_datetime64_any_dtype(work_df[date_col]):
        work_df[date_col] = pd.to_datetime(work_df[date_col], format='mixed', errors='coerce')
        
    work_df = work_df.dropna(subset=[date_col, value_col])
    
    if len(work_df) == 0:
        return {"error": "No valid data after date parsing."}
        
    # Aggregate
    work_df = work_df.set_index(date_col).sort_index()
    agg_df = work_df.resample(agg_freq).sum(numeric_only=True)
    agg_df[value_col] = agg_df[value_col].interpolate(method='linear').fillna(0)
    
    if len(agg_df) < window:
        return {"error": "Not enough data points for anomaly detection window."}
        
    # Calculate rolling median and robust IQR (Interquartile Range)
    # Using window around the point (centered=True) or lagging. We'll use lagging for real-time similarity.
    # To avoid the anomaly itself pulling the median, we can just use a standard rolling window and a strict multiplier.
    
    rolling_q25 = agg_df[value_col].rolling(window=window, min_periods=window//2).quantile(0.25)
    rolling_q75 = agg_df[value_col].rolling(window=window, min_periods=window//2).quantile(0.75)
    rolling_median = agg_df[value_col].rolling(window=window, min_periods=window//2).median()
    
    iqr = rolling_q75 - rolling_q25
    iqr = iqr.replace(0, np.mean(iqr) if np.mean(iqr) > 0 else 1e-5) # Prevent 0 IQR
    
    # Standard threshold is 1.5 * IQR. We'll use 2.0 to be a bit more strict for "anomalies"
    iqr_multiplier = 2.0
    
    upper_bound = rolling_q75 + (iqr_multiplier * iqr)
    lower_bound = rolling_q25 - (iqr_multiplier * iqr)
    
    agg_df['Expected_Upper'] = upper_bound
    agg_df['Expected_Lower'] = lower_bound
    agg_df['Baseline'] = rolling_median
    
    anomalies = []
    
    dates = agg_df.index
    vals = agg_df[value_col].values
    uppers = agg_df['Expected_Upper'].values
    lowers = agg_df['Expected_Lower'].values
    baselines = agg_df['Baseline'].values
    
    for i in range(len(dates)):
        val = vals[i]
        upper = uppers[i]
        lower = lowers[i]
        baseline = baselines[i]
        
        if pd.isna(upper) or pd.isna(lower):
            continue
            
        is_anomaly = False
        direction = ""
        deviation = 0
        
        if val > upper:
            is_anomaly = True
            direction = "Spike"
            deviation = val - upper
        elif val < lower:
            is_anomaly = True
            direction = "Drop"
            deviation = lower - val
            
        if is_anomaly:
            # Calculate Severity (0-100)
            # How many IQRs beyond the bound is it?
            # 1 IQR beyond = score 50, 2 IQRs = score 80, 3+ = 100
            current_iqr = (upper - lower) / (2 * iqr_multiplier) # recover local IQR
            if current_iqr > 0:
                severity_ratio = deviation / current_iqr
                severity_score = min(100, max(1, int(severity_ratio * 30))) 
            else:
                severity_score = 100
                
            anomalies.append({
                "date": dates[i],
                "direction": direction,
                "actual": val,
                "expected": baseline,
                "expected_range": (lower, upper),
                "severity": severity_score
            })
            
    # Sort by severity
    anomalies = sorted(anomalies, key=lambda x: x['severity'], reverse=True)
    
    return {
        "data": agg_df.reset_index(),
        "anomalies": anomalies,
        "error": None
    }
