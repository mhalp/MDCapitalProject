import pandas as pd
import logging

logger = logging.getLogger("MDCCapitalUtils")

def load_data(file_path):
    """Load and parse the provided CSV file."""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {e}")
        return pd.DataFrame()

def get_data_summary(df):
    """Generate a basic statistical summary of the data."""
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
