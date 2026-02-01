from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import logging
from typing import List, Dict, Any

from ..agent import MDCCapitalAgent
from ..utils import load_data, get_data_summary

# Configure logging for the API server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MDCCapital.Server")

app = FastAPI(
    title="MD Capital AI Server",
    description="Backend API for insurer communications analysis",
    version="1.0.0"
)

# Resolve project root and data path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "insurer_communications.csv")

# Global state
df = pd.DataFrame()

@app.on_event("startup")
async def startup_event():
    """Initializes the server by loading data on startup."""
    global df
    if os.path.exists(DATA_PATH):
        df = load_data(DATA_PATH)
        if not df.empty:
            logger.info(f"System ready. Loaded {len(df)} records.")
    else:
        logger.error(f"Critical Error: Data file not found at {DATA_PATH}")

class QueryRequest(BaseModel):
    """Schema for incoming LLM query requests."""
    question: str
    api_key: str

@app.get("/summary", response_model=Dict[str, Any])
async def get_summary():
    """Returns a statistical summary of the loaded data."""
    if df.empty:
        raise HTTPException(status_code=503, detail="Data repository unavailable")
    return get_data_summary(df)

@app.get("/data", response_model=List[Dict[str, Any]])
async def get_raw_data():
    """Returns the full raw dataset in JSON format."""
    if df.empty:
        return []
    return df.to_dict(orient="records")

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    """
    Proxies a question to the MDCCapitalAgent for LLM analysis.
    """
    logger.info(f"Incoming LLM request: {request.question[:50]}...")
    try:
        if df.empty:
            raise ValueError("No data available for analysis")
            
        agent = MDCCapitalAgent(df, request.api_key)
        response = agent.ask(request.question)
        
        logger.info(f"Analysis complete. Response length: {len(response)} chars")
        return {"response": response}
    except Exception as e:
        logger.error(f"Request processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # In production, this would be handled by a runner like gunicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
