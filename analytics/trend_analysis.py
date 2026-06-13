import pandas as pd
import numpy as np

def identify_datetime_columns(df: pd.DataFrame) -> list:
    """
    Identifies existing datetime columns or columns that strongly resemble dates.
    """
    dt_cols = []
    
    # 1. Native pandas datetime types
    native_dt = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
    dt_cols.extend(native_dt)
    
    # 2. Heuristics for string columns
    str_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in str_cols:
        if col in dt_cols:
            continue
            
        # Check first 50 non-null values to see if they parse as dates
        sample = df[col].dropna().head(50)
        if len(sample) == 0:
            continue
            
        try:
            pd.to_datetime(sample, format='mixed', errors='raise')
            dt_cols.append(col)
        except (ValueError, TypeError, pd.errors.ParserError):
            pass
            
    return dt_cols

def analyze_time_series(df: pd.DataFrame, date_col: str, value_col: str, agg_freq: str = 'D', window: int = 7) -> dict:
    """
    Calculates time-series statistics, moving averages, and growth metrics.
    
    Args:
        df: The dataframe
        date_col: Name of the column containing dates
        value_col: Name of the numeric column to aggregate
        agg_freq: Pandas frequency string ('D' for daily, 'W' for weekly, 'M' for monthly)
        window: Window size for moving averages
    """
    # Create a working copy
    work_df = df[[date_col, value_col]].copy()
    
    # Force convert to datetime if it's string
    if not pd.api.types.is_datetime64_any_dtype(work_df[date_col]):
        work_df[date_col] = pd.to_datetime(work_df[date_col], format='mixed', errors='coerce')
        
    work_df = work_df.dropna(subset=[date_col, value_col])
    
    if len(work_df) == 0:
        return {"error": "No valid data after date parsing."}
        
    # Set index and sort
    work_df = work_df.set_index(date_col).sort_index()
    
    # Aggregate values
    agg_df = work_df.resample(agg_freq).sum(numeric_only=True)
    
    # Fill missing dates with 0 (assuming volume/sales context, or ffill for price)
    # To be safe and generic, let's use linear interpolation, but fillna(0) if at boundaries
    agg_df[value_col] = agg_df[value_col].interpolate(method='linear').fillna(0)
    
    # Calculate rolling stats
    rolling = agg_df[value_col].rolling(window=window, min_periods=1)
    agg_df['Moving_Avg'] = rolling.mean()
    agg_df['Rolling_Std'] = rolling.std().fillna(0)
    
    # Trend Detection (Linear Regression on the Moving Average to smooth out noise)
    y = agg_df['Moving_Avg'].values
    x = np.arange(len(y))
    
    if len(y) > 1:
        slope, intercept = np.polyfit(x, y, 1)
        # Normalize slope relative to the mean of y to determine direction
        mean_y = np.mean(y) if np.mean(y) != 0 else 1.0
        normalized_slope = slope / mean_y
        
        if normalized_slope > 0.01:
            trend_dir = "Increasing"
        elif normalized_slope < -0.01:
            trend_dir = "Decreasing"
        else:
            trend_dir = "Stable"
    else:
        trend_dir = "Stable"
        slope = 0
        
    # Growth Calculation (Comparing start vs end of the smoothed trend)
    if len(y) > window:
        # Take mean of first window vs last window to avoid edge-case spikes
        start_val = np.mean(y[:window])
        end_val = np.mean(y[-window:])
    else:
        start_val = y[0] if len(y) > 0 else 0
        end_val = y[-1] if len(y) > 0 else 0
        
    if start_val != 0:
        growth_pct = ((end_val - start_val) / abs(start_val)) * 100
    else:
        growth_pct = 0.0
        
    # Highs and Lows
    peak_val = agg_df[value_col].max()
    peak_date = agg_df[value_col].idxmax()
    
    return {
        "data": agg_df.reset_index(),
        "trend_direction": trend_dir,
        "growth_pct": growth_pct,
        "start_val": start_val,
        "end_val": end_val,
        "peak_val": peak_val,
        "peak_date": peak_date,
        "total_volume": agg_df[value_col].sum(),
        "n_periods": len(agg_df),
        "error": None
    }
