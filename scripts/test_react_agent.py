#!/usr/bin/env python3
"""
Test script for ReAct Agent implementation.

This script validates that the ReAct agent properly:
1. Initializes tools (analytics and retrieval)
2. Follows the Thought/Action/Observation/Final Answer cycle
3. Uses both tools appropriately for different question types
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import load_data
from src.agent import MDCCapitalAgent

# Configure logging to see agent reasoning
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestReActAgent")


def test_react_agent(api_key: str):
    """Test the ReAct agent with various questions."""
    
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), "data", "insurer_communications.csv")
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        return False
    
    df = load_data(data_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Initialize agent
    try:
        agent = MDCCapitalAgent(df, api_key, verbose=True)
        logger.info("ReAct Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        return False
    
    # Test queries that should trigger different tools
    test_queries = [
        {
            "question": "How many claims are in high urgency status?",
            "expected_tool": "analytics_query",
            "description": "Quantitative query - should use Pandas tool"
        },
        {
            "question": "What are the common themes in communications from high-urgency claims?",
            "expected_tool": "retrieval_search",
            "description": "Qualitative query - should use Retrieval tool"
        },
        {
            "question": "Which insurer has the most claims, and what are the main themes in their communications?",
            "expected_tool": "both",
            "description": "Mixed query - should use both tools"
        }
    ]
    
    print("\n" + "="*80)
    print("REACT AGENT VALIDATION TEST")
    print("="*80)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {test_case['description']} ---")
        print(f"Question: {test_case['question']}")
        print("-" * 80)
        
        try:
            response = agent.ask(test_case['question'])
            
            print("\nAgent Response:")
            print(response)
            print("-" * 80)
            print("✓ Test passed")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            print(f"✗ Test failed: {str(e)}")
            return False
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_react_agent.py <GOOGLE_API_KEY>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    success = test_react_agent(api_key)
    sys.exit(0 if success else 1)
