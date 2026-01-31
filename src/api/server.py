from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import logging

from ..agent import MDCCapitalAgent
from ..utils import load_data, get_data_summary

# Resolve project root for data path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MDCCapitalServer")

app = FastAPI(title="MD Capital AI Server")

# Resolve data path
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "insurer_communications.csv")

# Global variables to hold data
if os.path.exists(DATA_PATH):
    df = load_data(DATA_PATH)
    logger.info(f"Loaded data from {DATA_PATH}")
else:
    logger.error(f"Data file not found at {DATA_PATH}")
    df = pd.DataFrame()

class QueryRequest(BaseModel):
    question: str
    api_key: str

@app.get("/summary")
async def get_summary():
    if df.empty:
        raise HTTPException(status_code=404, detail="Data not loaded")
    summary = get_data_summary(df)
    return summary

@app.get("/data")
async def get_raw_data():
    if df.empty:
        return []
    return df.to_dict(orient="records")

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    logger.info(f"Received request: {request.question[:50]}...")
    try:
        if df.empty:
            raise ValueError("Dataframe is empty")
            
        agent = MDCCapitalAgent(df, request.api_key)
        response = agent.ask(request.question)
        
        logger.info(f"Agent responded successfully. Length: {len(response)} chars")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
