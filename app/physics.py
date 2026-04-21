import math
import pandas as pd
import os

def get_dew_point(t: float, rh: float) -> float:
    a, b = 17.625, 243.04
    alpha = math.log(rh / 100.0) + ((a * t) / (b + t))
    return (b * alpha) / (a - alpha)

def calculate_mould_risk(file_path: str):
    if not os.path.exists(file_path):
        print(f"DEBUG: File not found at {file_path}")
        return {"error": "File not found"}

    df = pd.read_csv(file_path)
    
    if df.empty:
        print("DEBUG: CSV file is empty")
        return {"error": "CSV is empty"}

    # Calculate Dew Point
    df['dew_point'] = df.apply(lambda r: get_dew_point(r['temperature'], r['humidity']), axis=1)
    
    # Calculate Risk (Delta < 3.0)
    df['is_at_risk'] = (df['temperature'] - df['dew_point']) < 3.0
    
    risk_score = float(df['is_at_risk'].mean())
    
    # Ensure this return is at the very end of the function
    return {
        "risk_score": round(risk_score, 4),
        "sample_count": len(df),
        "status": "STABLE" if risk_score < 0.5 else "WARNING"
    }