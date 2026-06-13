import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge

def _create_time_features(dt_series: pd.Series) -> pd.DataFrame:
    """Extracts features from datetime for regression modeling."""
    features = pd.DataFrame(index=dt_series.index)
    # Trend component: days since start (linear trend)
    min_date = dt_series.min()
    features['days_since'] = (dt_series - min_date).dt.days
    
    # Seasonality components
    features['day_of_week'] = dt_series.dt.dayofweek
    features['month'] = dt_series.dt.month
    features['quarter'] = dt_series.dt.quarter
    
    return features

def generate_forecast(df: pd.DataFrame, date_col: str, value_col: str, agg_freq: str = 'D', horizon: int = 30) -> dict:
    """
    Generates a trend + seasonality forecast using a simple scikit-learn regression model.
    """
    work_df = df[[date_col, value_col]].copy()
    
    if not pd.api.types.is_datetime64_any_dtype(work_df[date_col]):
        work_df[date_col] = pd.to_datetime(work_df[date_col], format='mixed', errors='coerce')
        
    work_df = work_df.dropna(subset=[date_col, value_col])
    
    if len(work_df) == 0:
        return {"error": "No valid data after date parsing."}
        
    # Aggregate historical data
    work_df = work_df.set_index(date_col).sort_index()
    agg_df = work_df.resample(agg_freq).sum(numeric_only=True)
    agg_df[value_col] = agg_df[value_col].interpolate(method='linear').fillna(0)
    
    if len(agg_df) < 5:
        return {"error": "Not enough historical data points to generate a reliable forecast."}
        
    # 1. Prepare Training Data
    hist_dates = pd.Series(agg_df.index)
    X_train = _create_time_features(hist_dates)
    y_train = agg_df[value_col].values
    
    # 2. Train Model
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    
    # Calculate training residuals to establish confidence intervals
    preds_train = model.predict(X_train)
    residuals = y_train - preds_train
    std_residual = np.std(residuals) if len(residuals) > 0 else 0
    
    # 3. Prepare Future Data
    last_date = hist_dates.max()
    freq_mapping = {"D": "D", "W": "W", "ME": "ME"} # Map for date_range
    pd_freq = freq_mapping.get(agg_freq, "D")
    
    # Create future dates, starting next period
    future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=pd_freq)[1:]
    X_future = _create_time_features(pd.Series(future_dates))
    
    # 4. Predict
    preds_future = model.predict(X_future)
    
    # Build expanding confidence bounds
    # Uncertainty grows as we predict further into the future (sqrt of steps)
    expanding_factor = np.sqrt(np.arange(1, horizon + 1))
    
    # 95% Confidence Interval (~1.96 * std)
    z_score = 1.96
    margin_of_error = z_score * std_residual * expanding_factor
    
    upper_bound = preds_future + margin_of_error
    lower_bound = preds_future - margin_of_error
    
    # Prevent negative bounds if metric is generally positive
    if y_train.min() >= 0:
        lower_bound = np.maximum(lower_bound, 0)
        preds_future = np.maximum(preds_future, 0)
        upper_bound = np.maximum(upper_bound, 0)
        
    # Format Results
    forecast_df = pd.DataFrame({
        date_col: future_dates,
        'Forecast': preds_future,
        'Upper_Bound': upper_bound,
        'Lower_Bound': lower_bound
    })
    
    # Key Metrics
    hist_mean = np.mean(y_train)
    projected_end = preds_future[-1]
    
    if hist_mean != 0:
        growth_proj = ((projected_end - hist_mean) / abs(hist_mean)) * 100
    else:
        growth_proj = 0.0
        
    return {
        "historical": agg_df.reset_index(),
        "forecast": forecast_df,
        "metrics": {
            "historical_mean": hist_mean,
            "projected_end": projected_end,
            "growth_proj": growth_proj,
            "horizon": horizon
        },
        "error": None
    }
