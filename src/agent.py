import os
import ssl
import logging
from typing import List, Dict, Any

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
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import pandas as pd

from .tools import MDCToolFactory


# System message that governs the ReAct loop
REACT_SYSTEM_MESSAGE = """You are the MD Capital Operational Intelligence Agent. 

Your role is to analyze insurer communications and provide data-driven insights to management.

**ReAct Reasoning Cycle:**

Follow this structured approach for EVERY question:

1. **Thought**: Analyze the user's request carefully:
   - Is this a QUANTITATIVE question (counts, averages, statistics, comparisons)?
   - Is this a QUALITATIVE question (themes, patterns, reasons, specific communications)?
   - Does it need BOTH types of analysis?

2. **Action**: Select the appropriate tool:
   - Use "analytics_query" for math, counts, aggregations, filtering
   - Use "retrieval_search" for text patterns, themes, specific communication content
   - Make MULTIPLE tool calls if needed to build a complete answer

3. **Observation**: Carefully review the tool output:
   - Extract key numbers/patterns
   - Note any limitations or edge cases
   - Identify if you need additional context

4. **Repeat**: If the answer requires multiple perspectives (e.g., comparing two insurers):
   - Call the tool again with a new query
   - Combine results systematically

5. **Final Answer**: Provide a concise, professional summary:
   - Start with the most important finding
   - Support with specific data/evidence
   - Include any caveats or limitations
   - Keep language clear for executive decision-making

**Important Rules:**
- ALWAYS use tools to answer questions — do NOT rely on your training data
- Be specific: "3 claims" is better than "several claims"
- When in doubt, use both tools to triangulate the answer
- Log your reasoning steps clearly for audit trail
- Format numbers consistently (percentages, counts, averages)

Begin."""


class MDCCapitalAgent:
    """ReAct Agent for MD Capital Claims Intelligence."""
    
    def __init__(self, df: pd.DataFrame, api_key: str, model: str = "gemini-2.5-flash", verbose: bool = True, embedding_mode: str = "local"):
        """
        Initialize the ReAct Agent with tools.
        
        Args:
            df: The insurer communications dataframe
            api_key: Google API key for Gemini and embeddings (only needed if embedding_mode='google')
            model: Gemini model to use (default: 2.5-flash)
            verbose: Enable verbose logging of agent reasoning
            embedding_mode: 'local' (SentenceTransformers, no key) or 'google' (Google embeddings, requires key)
        """
        self.df = df
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        self.embedding_mode = embedding_mode
        
        # Initialize LLM with high reasoning capability
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0,  # Deterministic for consistent reasoning
            transport="rest",
        )
        logger.info(f"LLM initialized: {model}")
        
        # Initialize tools with specified embedding mode
        tool_factory = MDCToolFactory(df, api_key, embedding_mode=embedding_mode)
        self.tools = tool_factory.get_tools_list()
        
        logger.info(f"Agent initialized with {len(self.tools)} tools")
        
        # Initialize the ReAct agent
        self._initialize_react_agent()
        
    def _initialize_react_agent(self):
        """Initialize the LangChain ReAct agent with tools."""
        try:
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=self.verbose,
                max_iterations=10,
                early_stopping_method="generate",
                handle_parsing_errors=True,
                agent_kwargs={
                    "system_message": REACT_SYSTEM_MESSAGE,
                },
            )
            
            logger.info("ReAct agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ReAct agent: {str(e)}")
            raise
    
    def ask(self, question: str) -> str:
        """
        Process a user question through the ReAct agent.
        
        The agent will:
        1. Analyze the question
        2. Choose appropriate tools (analytics or retrieval)
        3. Observe tool outputs
        4. Synthesize a comprehensive answer
        
        Args:
            question: User's natural language question
            
        Returns:
            AI-generated answer based on tool interactions
        """
        logger.info(f"Processing query: {question[:80]}...")
        
        try:
            # Run the agent with chat_history for conversational context
            response = self.agent.run(input=question, chat_history=[])
            
            logger.info(f"Agent completed successfully. Response length: {len(response)} chars")
            return response
            
        except Exception as e:
            error_msg = f"Agent Error: {type(e).__name__} - {str(e)}"
            logger.error(error_msg)
            return f"An error occurred while processing your question: {str(e)}"
    
    def get_reasoning_trace(self, question: str) -> Dict[str, Any]:
        """
        Get detailed reasoning trace for debugging/audit purposes.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing agent reasoning steps
        """
        # This would be enhanced with LangChain's debugging tools
        # For now, return basic info
        return {
            "question": question,
            "model": self.model_name,
            "tools_available": [tool.name for tool in self.tools],
            "agent_type": "CHAT_CONVERSATIONAL_REACT_DESCRIPTION"
        }
