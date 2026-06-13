import pandas as pd
from analytics.dataset_dna import generate_dataset_dna
from analytics.trend_analysis import identify_datetime_columns

def generate_analytical_recommendations(df: pd.DataFrame) -> list:
    """
    Evaluates dataset characteristics to recommend the most impactful analytical modules.
    """
    recommendations = []
    
    # Run lightweight Dataset DNA extraction
    dna = generate_dataset_dna(df)
    
    # 1. Timeline / Forecasting Recommendation
    dt_cols = identify_datetime_columns(df)
    if len(dt_cols) > 0:
        recommendations.append({
            "title": "Timeline Intelligence",
            "icon": "⏳",
            "color": "#8b5cf6",
            "reason": "We detected a strong time component. Run Timeline Intelligence to forecast future behavior and uncover cyclical seasonality."
        })
        
    # 2. Segment Discovery Recommendation
    if dna.get("Clusterability", 0) > 45:
        recommendations.append({
            "title": "Segment Discovery",
            "icon": "🧩",
            "color": "#3b82f6",
            "reason": f"High clusterability score ({dna.get('Clusterability')} / 100). The algorithm detects strong natural groupings that should be mapped out."
        })
        
    # 3. Anomaly Detection Recommendation
    if dna.get("Stability", 100) < 65:
        recommendations.append({
            "title": "Anomaly Detection",
            "icon": "🚨",
            "color": "#ef4444",
            "reason": f"Low stability score ({dna.get('Stability')} / 100). The dataset exhibits a high anomaly risk. Isolate these structural breaks immediately."
        })
        
    # 4. Correlation Discovery Recommendation
    if dna.get("Complexity", 0) > 40:
        recommendations.append({
            "title": "Correlation Discovery",
            "icon": "🔗",
            "color": "#10b981",
            "reason": f"High feature complexity ({dna.get('Complexity')} / 100). Run Correlation Discovery to untangle hidden relationships between your variables."
        })
        
    # Fallback if no strong signals
    if not recommendations:
        recommendations.append({
            "title": "Dataset DNA Profile",
            "icon": "🧬",
            "color": "#f59e0b",
            "reason": "Start by generating a full structural blueprint of your data to understand its underlying shape."
        })
        
    # Cap at top 4 to keep UI clean
    return recommendations[:4]
