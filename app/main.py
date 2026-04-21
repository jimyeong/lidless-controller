from fastapi import FastAPI, Query
from app.physics import calculate_mould_risk
from datetime import datetime


app = FastAPI(title="Lidless Controller")

@app.get("/")
def read_root():
    return {"status": "Lidless Controller is Watching"}

@app.get("/api/analysis/mould-risk")
def get_mould_risk(period: str = Query("day", regex="^(day|week|month)$")):
    data_file = "humid_temp_readings_202604211431.csv"
    if not os.path.exists(data_file):
        return {"error": "Data file not found"}

    analysis = calculate_mould_risk_from_csv(data_file)

    return {
        "analysis_type": "mould_growth_assessment",
        "parameters": {period: period, threshold: "3.0°C"},
        "results": analysis,
    }
