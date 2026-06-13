import pandas as pd
import numpy as np

def detect_change_points(df: pd.DataFrame, date_col: str, value_col: str, agg_freq: str = 'D', window: int = 14, z_threshold: float = 2.5) -> dict:
    """
    Detects structural breaks / change points in a time series using a rolling Z-score method.
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
    
    if len(agg_df) < window * 2:
        return {"error": "Not enough data points for change point detection window."}
        
    # Compute rolling stats (shifting by 1 so the current point is not in its own baseline)
    rolling_mean = agg_df[value_col].shift(1).rolling(window=window, min_periods=window//2).mean()
    rolling_std = agg_df[value_col].shift(1).rolling(window=window, min_periods=window//2).std()
    
    # Calculate Z-score
    # Avoid division by zero
    rolling_std = rolling_std.replace(0, 1e-5)
    agg_df['Z_Score'] = (agg_df[value_col] - rolling_mean) / rolling_std
    
    # Flag points that cross the threshold
    agg_df['Is_Change'] = np.abs(agg_df['Z_Score']) > z_threshold
    
    change_events = []
    
    # We want to group consecutive flagged points into a single "regime change event"
    in_event = False
    event_start_date = None
    event_peak_z = 0
    event_direction = ""
    
    dates = agg_df.index
    is_change = agg_df['Is_Change'].values
    z_scores = agg_df['Z_Score'].values
    vals = agg_df[value_col].values
    
    for i in range(len(dates)):
        if is_change[i]:
            if not in_event:
                in_event = True
                event_start_date = dates[i]
                event_peak_z = z_scores[i]
                event_direction = "Spike" if z_scores[i] > 0 else "Drop"
            else:
                # Update peak z-score if this point is more extreme
                if abs(z_scores[i]) > abs(event_peak_z):
                    event_peak_z = z_scores[i]
        else:
            if in_event:
                # Event ended
                # Calculate pre and post baselines
                end_idx = i - 1
                start_idx = np.where(dates == event_start_date)[0][0]
                
                # Pre-baseline: average of 'window' points before the start
                pre_start_idx = max(0, start_idx - window)
                pre_baseline = np.mean(vals[pre_start_idx:start_idx]) if start_idx > 0 else vals[0]
                
                # Post-baseline: average of 'window' points after the event ends (if available)
                post_end_idx = min(len(dates), i + window)
                post_baseline = np.mean(vals[i:post_end_idx]) if i < len(dates) else vals[-1]
                
                if pre_baseline != 0:
                    shift_pct = ((post_baseline - pre_baseline) / abs(pre_baseline)) * 100
                else:
                    shift_pct = 0.0
                    
                change_events.append({
                    "date": event_start_date,
                    "direction": event_direction,
                    "peak_z": event_peak_z,
                    "pre_baseline": pre_baseline,
                    "post_baseline": post_baseline,
                    "shift_pct": shift_pct
                })
                
                in_event = False
                
    # Handle event that hits the end of the series
    if in_event:
        start_idx = np.where(dates == event_start_date)[0][0]
        pre_start_idx = max(0, start_idx - window)
        pre_baseline = np.mean(vals[pre_start_idx:start_idx]) if start_idx > 0 else vals[0]
        # We don't have a post-baseline, just use the values during the event
        post_baseline = np.mean(vals[start_idx:])
        
        if pre_baseline != 0:
            shift_pct = ((post_baseline - pre_baseline) / abs(pre_baseline)) * 100
        else:
            shift_pct = 0.0
            
        change_events.append({
            "date": event_start_date,
            "direction": event_direction,
            "peak_z": event_peak_z,
            "pre_baseline": pre_baseline,
            "post_baseline": post_baseline,
            "shift_pct": shift_pct
        })

    # Sort events by severity (absolute z-score)
    change_events = sorted(change_events, key=lambda x: abs(x['peak_z']), reverse=True)
    
    return {
        "data": agg_df.reset_index(),
        "change_events": change_events,
        "error": None
    }
