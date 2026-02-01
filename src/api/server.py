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

app = FastAPI(title="MD Capital AI Server - ReAct Agent")

# Resolve data path
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "insurer_communications.csv")

# Global variables to hold data
if os.path.exists(DATA_PATH):
    df = load_data(DATA_PATH)
    logger.info(f"Loaded data from {DATA_PATH}")
else:
    logger.error(f"Data file not found at {DATA_PATH}")
    df = pd.DataFrame()

# Cache for initialized agents (keyed by API key hash for security)
_agent_cache = {}

class QueryRequest(BaseModel):
    question: str
    api_key: str

@app.get("/summary")
async def get_summary():
    """Get data statistics summary."""
    if df.empty:
        raise HTTPException(status_code=404, detail="Data not loaded")
    summary = get_data_summary(df)
    return summary

@app.get("/data")
async def get_raw_data():
    """Get raw communication data."""
    if df.empty:
        return []
    return df.to_dict(orient="records")

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    """
    Process a question through the ReAct agent.
    
    The agent will:
    1. Analyze the question (Thought)
    2. Select appropriate tools (Action) - analytics or retrieval
    3. Observe tool outputs (Observation)
    4. Synthesize a comprehensive answer (Final Answer)
    """
    logger.info(f"Received request: {request.question[:80]}...")
    try:
        if df.empty:
            raise ValueError("Dataframe is empty")
        
        # Initialize agent (with verbose=True to see ReAct reasoning)
        agent = MDCCapitalAgent(
            df=df, 
            api_key=request.api_key,
            verbose=True  # Enable verbose output to see Thought/Action/Observation cycle
        )
        
        # Run the ReAct agent
        response = agent.ask(request.question)
        
        logger.info(f"Agent responded successfully. Length: {len(response)} chars")
        return {
            "response": response,
            "agent_type": "ReAct",
            "tools_used": ["analytics_query", "retrieval_search"]
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "agent_type": "ReAct",
        "data_loaded": not df.empty,
        "record_count": len(df) if not df.empty else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
