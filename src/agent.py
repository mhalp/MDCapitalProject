import os
import ssl
import logging

# Configure logging
logger = logging.getLogger("MDCCapitalAgent")

# SSL Configuration - Run immediately
# Check for custom certificate (e.g. for Etrog/NetFree filters)
# Resolve path relative to this file to ensure it works regardless of CWD
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Prefer combined bundle if it exists (contains standard roots + custom CA)
combined_cert_path = os.path.join(project_root, "combined.pem")
etrog_cert_path = os.path.join(project_root, "etrog.crt")

cert_path = None
if os.path.exists(combined_cert_path):
    cert_path = combined_cert_path
elif os.path.exists(etrog_cert_path):
    cert_path = etrog_cert_path

if cert_path:
    os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = cert_path
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
elif os.environ.get('MDC_BYPASS_SSL') == '1':
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd

class MDCCapitalAgent:
    def __init__(self, df, api_key, model="gemini-2.5-flash"):
        self.df = df
        self.api_key = api_key
        # Initialize Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=model, 
            google_api_key=api_key, 
            temperature=0,
            transport="rest",
        )
        logger.info(f"Agent initialized with model: {model}")
        
    def _prepare_prompt(self, question):
        """Construct the prompt with data context."""
        context_header = "You are an AI Agent for MD Capital. Use the following insurer communications data to answer the user's question.\n\n"
        
        # Add basic statistics
        stats = self.df.describe(include='all').to_string()
        
        # Add all communication records
        records = ""
        for _, row in self.df.iterrows():
            records += f"Insurer: {row['insurer_name']} | Status: {row['claim_status']} | Urgency: {row['urgency']} | Days: {row['days_since_submission']} | Text: {row['communication_text']}\n"
        
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

    def ask(self, question):
        logger.info(f"Processing query: {question[:50]}...")
        
        prompt = self._prepare_prompt(question)
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            response = self.llm.invoke(prompt)
            logger.info("Successfully received LLM response")
            return response.content
        except Exception as e:
            logger.error(f"LLM Error: {type(e).__name__} - {str(e)}")
            return f"Error communicating with Gemini: {str(e)}"
