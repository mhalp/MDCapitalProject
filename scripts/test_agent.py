import os
import pandas as pd
import sys
import logging

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_ROOT)

from src.agent import MDCCapitalAgent

# Configure logging for terminal output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_agent(api_key):
    # Resolve data path
    DATA_PATH = os.path.join(PROJECT_ROOT, "data", "insurer_communications.csv")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    print("Initializing Agent...")
    # Using gemini-1.5-flash as it's faster and cheaper for testing
    agent = MDCCapitalAgent(df, api_key, model="gemini-1.5-flash")
    
    query = "What are the top 3 rejection reasons?"
    print(f"Asking query: {query}")
    
    try:
        response = agent.ask(query)
        print("\n--- AGENT RESPONSE ---")
        print(response)
        print("----------------------\n")
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR !!!")
        print(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_agent.py <YOUR_GOOGLE_API_KEY>")
    else:
        test_agent(sys.argv[1])
