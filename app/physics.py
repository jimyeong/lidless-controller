import math
import pandas as pd

def get_dew_point(t: float, rh: float) -> float:
    """Calculates Dew Point using the Magnus-Tetens formula."""
    a, b = 17.625, 243.04
    alpha = math.log(rh/100.0) + ((a * t) / (b + t))
    return (b * alpha) / (a - alpha)

def calculate_mould_risk_from_csv(file_path: str):
    # Load your original data
    df = pd.read_csv(file_path)
    
    # Calculate dew point for every row
    df['dew_point'] = df.apply(lambda row: get_dew_point(row['temperature'], row['humidity']), axis=1)
    
    # Identify 'Danger' points where Ambient Temp - Dew Point < 3.0°C
    df['is_at_risk'] = (df['temperature'] - df['dew_point']) < 3.0
    
    danger_count = df['is_at_risk'].sum()
    total_samples = len(df)
    risk_score = round(danger_count / total_samples, 2)
    
    return {
        "risk_score": risk_score,
        "danger_samples": int(danger_count),
        "total_samples": total_samples,
        "status": "high_risk" if risk_score > 0.6 else "warning" if risk_score > 0.3 else "safe"
    }