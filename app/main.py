from fastapi import FastAPI, Query
from app.physics import calculate_mould_risk
import os

app = FastAPI()
# connect CLOUDAMPQ




@app.get("/")
def read_root():
    return {"message": "Lidless Controller AI is running"}

@app.get("/api/analysis/mould-risk")
def get_analysis(period: str = Query("day", pattern="^(day|week|month)$")):
    # This logic ensures we find the file regardless of where you start the terminal
    base_path = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_path, "humid_temp_readings_202604211431.csv")
    
    try:
        result = calculate_mould_risk(csv_path)
        return result
    except Exception as e:
        return {"error": "Internal Server Error", "details": str(e)}