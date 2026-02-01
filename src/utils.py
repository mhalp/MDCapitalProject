import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger("MDCCapital.Utils")

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load and parse the provided CSV file.
    
    Args:
        file_path (str): Path to the CSV data file.
        
    Returns:
        pd.DataFrame: Loaded data or empty DataFrame on failure.
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {e}")
        return pd.DataFrame()

def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a basic statistical summary of the data.
    
    Args:
        df (pd.DataFrame): The input records.
        
    Returns:
        Dict[str, Any]: Summary statistics including record count, insurer list, 
                        status distribution, and averages.
    """
    if df.empty:
        return {
            "total_records": 0,
            "insurers": [],
            "status_counts": {},
            "avg_urgency": 0.0,
            "avg_days": 0.0
        }
        
    summary = {
        "total_records": len(df),
        "insurers": df['insurer_name'].unique().tolist(),
        "status_counts": df['claim_status'].value_counts().to_dict(),
        "avg_urgency": float(df['urgency'].mean()),
        "avg_days": float(df['days_since_submission'].mean())
    }
    return summary
