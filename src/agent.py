import os
import ssl
import logging
from typing import Optional
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI

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
    """
    
    def __init__(self, df: pd.DataFrame, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize the agent with data and API configuration.
        
        Args:
            df (pd.DataFrame): The insurer data to analyze.
            api_key (str): Google Gemini API key.
            model (str): Gemini model identifier.
        """
        self.df = df
        self.api_key = api_key
        # Initialize Gemini with REST transport to improve reliability in some environments
        self.llm = ChatGoogleGenerativeAI(
            model=model, 
            google_api_key=api_key, 
            temperature=0,
            transport="rest",
        )
        logger.info(f"Agent initialized with model: {model}")
        
    def _prepare_prompt(self, question: str) -> str:
        """
        Construct a detailed prompt by injecting data context into the template.
        
        Args:
            question (str): User's natural language question.
            
        Returns:
            str: Full prompt for the LLM.
        """
        context_header = "You are an AI Agent for MD Capital. Use the following insurer communications data to answer the user's question.\n\n"
        
        # Add basic statistics summary
        stats = self.df.describe(include='all').to_string()
        
        # Format individual communication records for context
        records_list = []
        for _, row in self.df.iterrows():
            records_list.append(
                f"Insurer: {row['insurer_name']} | Status: {row['claim_status']} | "
                f"Urgency: {row['urgency']} | Days: {row['days_since_submission']} | "
                f"Text: {row['communication_text']}"
            )
        records = "\n".join(records_list)
        
        prompt = f"""
{context_header}

### DATA STATISTICS ###
{stats}

### COMMUNICATION RECORDS ###
{records}

### USER QUESTION ###
{question}

Provide a detailed, data-driven answer based ONLY on the data provided above.
"""
        return prompt

    def ask(self, question: str) -> str:
        """
        Processes a query and returns the LLM response.
        
        Args:
            question (str): User's question about the claims data.
            
        Returns:
            str: The AI's response or an error message.
        """
        logger.info(f"Processing query: {question[:50]}...")
        
        prompt = self._prepare_prompt(question)
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            response = self.llm.invoke(prompt)
            logger.info("Successfully received LLM response")
            return str(response.content)
        except Exception as e:
            logger.error(f"LLM Error: {type(e).__name__} - {str(e)}")
            return f"Error communicating with Gemini: {str(e)}"
