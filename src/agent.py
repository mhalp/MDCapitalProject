import os
import ssl
import logging
import traceback
from typing import Optional, Dict, Any, Union
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Configure logger for the agent
logger = logging.getLogger("MDCCapital.Agent")

def setup_ssl_environment() -> None:
    """
    Configures the environment for SSL connectivity, handling custom 
    certificates often required in filtered corporate/production environments.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    # Search for custom certificate bundles
    combined_cert = os.path.join(project_root, "combined.pem")
    etrog_cert = os.path.join(project_root, "etrog.crt")
    
    cert_path = None
    if os.path.exists(combined_cert):
        cert_path = combined_cert
    elif os.path.exists(etrog_cert):
        cert_path = etrog_cert

    if cert_path:
        logger.info(f"Custom SSL certificate detected at: {cert_path}")
        os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = cert_path
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    elif os.environ.get('MDC_BYPASS_SSL') == '1':
        logger.warning("SSL verification is being bypassed (MDC_BYPASS_SSL=1)")
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

# Initialize SSL environment on module load
setup_ssl_environment()

class MDCCapitalAgent:
    """
    AI Agent responsible for analyzing insurer communication data using Gemini LLM.
    Uses a "Plan-and-Execute" workflow for reliable business insights.
    """
    
    def __init__(self, df: pd.DataFrame, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize the agent with data and API configuration.
        """
        self.df = df
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(
            model=model, 
            google_api_key=api_key, 
            temperature=0,
            transport="rest",
        )
        logger.info(f"Agent initialized with model: {model} (Plan-and-Execute Mode)")
        
    def _planner(self, question: str) -> str:
        """
        The Planner: LLM writes Python/Pandas code to solve the user's question.
        """
        schema_info = []
        for col, dtype in self.df.dtypes.items():
            sample = self.df[col].dropna().unique()[:3]
            schema_info.append(f"- {col} ({dtype}): e.g., {list(sample)}")
        
        schema_str = "\n".join(schema_info)
        
        prompt = f"""
        You are a Data Analyst for MD Capital. Write Python code using pandas to answer the question below.
        
        ### DATAFRAME SCHEMA (`df`) ###
        {schema_str}
        
        The DataFrame is already loaded as 'df'.
        Your code should calculate the answer and store it in a variable named 'result'.
        
        Rules:
        1. ONLY output the Python code block. No explanations.
        2. Use strictly pandas and standard Python.
        3. Do not assume any external variables (like 'stop_words') or libraries are available.
        4. If you need to analyze text, use simple pandas string operations (e.g., .str.contains, .value_counts).
        5. Focus on accuracy and business logic.
        
        User Question: {question}
        
        Python Code:
        """
        
        response = self.llm.invoke(prompt)
        code = str(response.content).strip()
        
        # Clean up Markdown formatting if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
            
        return code

    def _executor(self, code: str) -> Any:
        """
        The Executor: Runs the generated code against the dataframe.
        """
        logger.info(f"Executing Plan:\n{code}")
        
        # Use a localized scope for execution
        local_vars = {"df": self.df, "pd": pd}
        try:
            # We use exec() but only provide the df and necessary libs
            exec(code, {"__builtins__": __builtins__}, local_vars)
            result = local_vars.get("result", "No result variable set in code.")
            
            # Format result if it's a DF/Series
            if isinstance(result, (pd.DataFrame, pd.Series)):
                return result.to_string()
            return result
        except Exception as e:
            logger.error(f"Execution Error: {str(e)}\n{traceback.format_exc()}")
            return f"Error executing code: {str(e)}"

    def _reporter(self, question: str, raw_result: Any) -> str:
        """
        The Reporter: Turns raw Pandas output into a high-impact executive insight.
        """
        prompt = f"""
        You are a Senior Strategic Analyst at MD Capital. Provide a high-impact, data-driven response.

        USER QUERY: "{question}"
        RAW ANALYSIS DATA: {raw_result}

        INSTRUCTIONS:
        1. NO CONVERSATIONAL FILLER. Do not say "Good morning", "Here is the report", "Today we focus on", or "I hope this helps".
        2. START WITH THE DATA. Provide the direct answer first.
        3. BE CONCISE. Use bullet points for multiple findings.
        4. USE BOLDING for key metrics and insurers.
        5. ADD A "STRATEGIC IMPACT" sentence at the end explaining what this data means for MD Capital's bottom line.
        
        Response:
        """
        
        response = self.llm.invoke(prompt)
        return str(response.content).strip()

    def ask(self, question: str) -> str:
        """
        Processes a query using the Plan-and-Execute workflow.
        """
        logger.info(f"Agent received question: {question}")
        
        try:
            # 1. Plan
            code = self._planner(question)
            
            # 2. Execute
            raw_result = self._executor(code)
            
            # 3. Report
            final_answer = self._reporter(question, raw_result)
            
            return final_answer
        except Exception as e:
            logger.error(f"Workflow Exception: {str(e)}")
            return f"Strategic Analysis Failed: {str(e)}"
