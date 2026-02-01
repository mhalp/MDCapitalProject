"""
ReAct Tools for MD Capital AI Agent

This module defines the two specialized tools:
1. Analytics Tool (Pandas REPL) - For quantitative queries (math, counts, averages)
2. Retrieval Tool (FAISS Vector Store) - For qualitative queries (text search, themes)

Supports two embedding modes:
- local: SentenceTransformers + FAISS (no API key required, runs locally)
- google: Google Generative AI embeddings (requires API key)
"""

import os
import logging
import pandas as pd
from typing import Any, Optional
import numpy as np

from langchain_experimental.tools import PythonAstREPLTool
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.tools import Tool

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

logger = logging.getLogger("MDCCapitalTools")


class MDCToolFactory:
    """Factory for creating ReAct tools for the MD Capital Agent."""
    
    def __init__(self, df: pd.DataFrame, api_key: str, embedding_mode: str = "local"):
        """
        Initialize the tool factory with data.
        
        Args:
            df: The insurer communications dataframe
            api_key: Google API key for embeddings (only needed if embedding_mode='google')
            embedding_mode: 'local' (SentenceTransformers, no key) or 'google' (Google embeddings, requires key)
        """
        self.df = df
        self.api_key = api_key
        self.embedding_mode = embedding_mode
        self._analytics_tool = None
        self._retrieval_tool = None
        self._local_embedder = None
        self._local_index = None
        self._local_texts = None
        self._local_metadatas = None
        
        # Validate embedding mode and dependencies
        if embedding_mode == "local":
            if not HAS_SENTENCE_TRANSFORMERS:
                logger.warning("SentenceTransformers not installed. Local embeddings unavailable.")
            if not HAS_FAISS:
                logger.warning("FAISS not installed. Local embeddings unavailable.")
        
        logger.info(f"MDCToolFactory initialized with embedding_mode={embedding_mode}")
        
    def create_analytics_tool(self) -> Tool:
        """
        Create the Analytics Tool (Pandas REPL).
        
        This tool allows the agent to:
        - Calculate averages, counts, and statistics
        - Filter and group data
        - Perform conditional logic on structured metrics
        
        Returns:
            Tool wrapping PythonAstREPLTool configured with the dataframe
        """
        if self._analytics_tool is not None:
            return self._analytics_tool

        # Create local namespace with the dataframe and common imports
        local_ns = {
            "df": self.df,
            "pd": pd,
        }

        # Create the underlying Python AST REPL tool
        python_repl = PythonAstREPLTool(locals=local_ns)

        # Wrap the REPL as a named LangChain Tool so the agent can call it
        # The agent's system message expects a tool named "analytics_query"
        def _determine_reason_for_query(query: str, tool_hint: str = None) -> str:
            """Very small heuristic to explain why the tool is being used."""
            q = (query or "").lower()
            if any(token in q for token in ["df[", "df.", "groupby", "value_counts", "mean(", "sum(", "len("]):
                return "quantitative (pandas expression)"
            if any(word in q for word in ["count", "average", "mean", "sum", "percent", "percentage", "how many"]):
                return "quantitative (explicit ask)"
            if tool_hint == "retriever":
                return "qualitative (text search)"
            # default fallback
            return "qualitative (text/semantic search)"

        def _analytics_runner(query, repl=python_repl, df=self.df):
            reason = _determine_reason_for_query(query, tool_hint="analytics")
            # Log to terminal for debugging: which tool, input, and heuristic reason
            logger.info(f"Tool Call -> analytics_query | Reason: {reason} | Input: {query}")
            print(f"[TOOL CALL] analytics_query | Reason: {reason} | Input: {query}")

            try:
                if hasattr(repl, "run"):
                    result = repl.run(query)
                else:
                    result = repl(query)

                # Some REPL implementations return exception messages as strings
                if isinstance(result, str) and ("KeyError" in result or "Column not found" in result or "column not found" in result.lower()):
                    cols = sorted(list(df.columns))
                    return (
                        f"Column not found or invalid column referenced. Available columns: {cols}. "
                        "Please adjust your query to use an existing column."
                    )

                return result
            except KeyError as ke:
                # Column missing in dataframe
                cols = sorted(list(df.columns))
                return (
                    f"Column not found: {ke}. Available columns: {cols}. "
                    "Please adjust your query to use an existing column."
                )
            except Exception as exc:
                # Generic fallback with helpful context
                msg = str(exc)
                if "Column not found" in msg or "column not found" in msg.lower() or "KeyError" in msg:
                    cols = sorted(list(df.columns))
                    return f"Column not found. Available columns: {cols}."
                return f"Analytics tool error: {msg}"

        self._analytics_tool = Tool(
            name="analytics_query",
            func=_analytics_runner,
            description=(
                "Execute pandas/python expressions against the dataset. "
                "Use for quantitative queries (counts, averages, grouping). "
                "Provide valid pandas expressions or short python snippets."
            ),
        )

        logger.info("Analytics Tool (Pandas REPL) initialized as 'analytics_query'")

        return self._analytics_tool
    
    def _build_local_retriever(self, texts: list, metadatas: list):
        """
        Build a local FAISS retriever using SentenceTransformers.
        
        Args:
            texts: List of text strings to embed and index
            metadatas: List of metadata dicts corresponding to texts
            
        Returns:
            Tuple of (model, index, texts, metadatas) for retrieval
        """
        if not HAS_SENTENCE_TRANSFORMERS or not HAS_FAISS:
            logger.error("SentenceTransformers or FAISS not installed")
            return None, None, None, None
        
        try:
            # Load embedding model (lightweight but effective)
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Encode all texts (batch processing)
            logger.info(f"Encoding {len(texts)} texts...")
            embeddings = model.encode(texts, batch_size=64, show_progress_bar=False, convert_to_numpy=True)
            
            # Normalize embeddings for cosine similarity via inner product
            faiss.normalize_L2(embeddings)
            
            # Create FAISS index
            dim = embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)  # Inner product on normalized vectors = cosine similarity
            index.add(embeddings)
            
            logger.info(f"Local FAISS index created: {len(texts)} documents, dimension={dim}")
            return model, index, texts, metadatas
            
        except Exception as e:
            logger.error(f"Failed to build local retriever: {e}")
            return None, None, None, None
    
    def _retrieve_local(self, query: str, k: int = 5) -> list:
        """
        Retrieve documents using local FAISS index.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of dicts with 'content' and 'metadata' keys
        """
        if self._local_embedder is None or self._local_index is None:
            return []
        
        try:
            # Encode query
            q_embedding = self._local_embedder.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(q_embedding)
            
            # Search index
            scores, indices = self._local_index.search(q_embedding, k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._local_texts):
                    continue
                results.append({
                    "content": self._local_texts[idx],
                    "metadata": self._local_metadatas[idx] if idx < len(self._local_metadatas) else {},
                    "score": float(score)
                })
            
            return results
        except Exception as e:
            logger.error(f"Local retrieval error: {e}")
            return []
    
    def create_retrieval_tool(self) -> Tool:
        """
        Create the Retrieval Tool (FAISS Vector Store).
        
        This tool allows the agent to:
        - Search for communication themes (prior authorization, denials, etc.)
        - Find similar communication patterns
        - Retrieve contextual text snippets
        
        Supports two modes:
        - 'local': SentenceTransformers + FAISS (no API key required)
        - 'google': Google Generative AI embeddings (requires API key)
        
        Returns:
            LangChain Tool wrapping FAISS retriever
        """
        if self._retrieval_tool is not None:
            return self._retrieval_tool
        
        try:
            # Extract communication texts from dataframe
            if 'communication_text' not in self.df.columns:
                logger.warning("'communication_text' column not found in dataframe")
                texts = []
                metadata = []
            else:
                texts = self.df['communication_text'].dropna().tolist()
                # Create metadata for each text
                metadata = [
                    {
                        "insurer": row.get('insurer_name', 'Unknown'),
                        "status": row.get('claim_status', 'Unknown'),
                        "urgency": row.get('urgency', 'Unknown'),
                        "days_since_submission": row.get('days_since_submission', 0)
                    }
                    for _, row in self.df[self.df['communication_text'].notna()].iterrows()
                ]
            
            if not texts:
                logger.warning("No communication texts found for vectorization")
                # Return a dummy tool that explains the issue and logs calls
                def _empty_retrieval(query):
                    reason = "qualitative (no texts available)"
                    logger.info(f"Tool Call -> retrieval_search | Reason: {reason} | Input: {query}")
                    print(f"[TOOL CALL] retrieval_search | Reason: {reason} | Input: {query}")
                    return "No communication texts available for retrieval."

                return Tool(
                    name="retrieval_search",
                    func=_empty_retrieval,
                    description="Search communication records for themes and patterns (No data available)"
                )
            
            # Build retriever based on embedding mode
            if self.embedding_mode == "local":
                logger.info("Using local embeddings (SentenceTransformers + FAISS)")
                model, index, texts_stored, metadatas_stored = self._build_local_retriever(texts, metadata)
                
                if model is None or index is None:
                    raise RuntimeError("Failed to initialize local embeddings. Install: pip install sentence-transformers faiss-cpu")
                
                # Store for use in _retrieve_local
                self._local_embedder = model
                self._local_index = index
                self._local_texts = texts_stored
                self._local_metadatas = metadatas_stored
                
                # Create a small heuristic for retrieval reasoning
                def _determine_reason_for_retrieval(query: str) -> str:
                    q = (query or "").lower()
                    if any(word in q for word in ["prior authorization", "denial", "denied", "why", "reason", "themes", "tone", "patterns"]):
                        return "qualitative (search for themes/phrases)"
                    return "qualitative (semantic search)"

                def _retrieval_runner_local(query, self_ref=self):
                    reason = _determine_reason_for_retrieval(query)
                    logger.info(f"Tool Call -> retrieval_search | Reason: {reason} | Input: {query}")
                    print(f"[TOOL CALL] retrieval_search | Reason: {reason} | Input: {query}")
                    try:
                        results = self_ref._retrieve_local(query, k=5)
                        if not results:
                            return "No relevant documents found."
                        
                        formatted = "Found relevant communications:\n"
                        for i, res in enumerate(results, 1):
                            formatted += f"\n--- Result {i} (score: {res['score']:.3f}) ---\n"
                            formatted += f"Content: {res['content']}\n"
                            if res['metadata']:
                                formatted += f"Metadata: {res['metadata']}\n"
                        return formatted
                    except Exception as exc:
                        err = str(exc)
                        logger.error(f"Local retrieval error: {err}")
                        return f"Retrieval error: {err}"
                
                self._retrieval_tool = Tool(
                    name="retrieval_search",
                    func=_retrieval_runner_local,
                    description="""Search communication records for specific themes, keywords, or patterns.
Use this for qualitative queries like:
- "Find instances of prior authorization denials"
- "Search for communication patterns with specific insurers"
- "Look for high-urgency communication themes"
Returns the top 5 most relevant communication excerpts with similarity scores."""
                )
            
            else:  # embedding_mode == "google"
                logger.info("Using Google Generative AI embeddings")
                # Initialize embeddings with Google's generative AI
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self.api_key
                )
                
                # Create FAISS vector store
                vector_db = FAISS.from_texts(
                    texts=texts,
                    embedding=embeddings,
                    metadatas=metadata
                )
                
                # Create retriever
                retriever = vector_db.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}  # Return top 5 most relevant documents
                )
                
                # Create a small heuristic for retrieval reasoning
                def _determine_reason_for_retrieval_google(query: str) -> str:
                    q = (query or "").lower()
                    if any(word in q for word in ["prior authorization", "denial", "denied", "why", "reason", "themes", "tone", "patterns"]):
                        return "qualitative (search for themes/phrases)"
                    return "qualitative (semantic search)"

                def _retrieval_runner_google(query, retr=retriever):
                    reason = _determine_reason_for_retrieval_google(query)
                    logger.info(f"Tool Call -> retrieval_search | Reason: {reason} | Input: {query}")
                    print(f"[TOOL CALL] retrieval_search | Reason: {reason} | Input: {query}")
                    try:
                        results = retr.invoke(query)
                    except Exception as exc:
                        err = str(exc)
                        logger.error(f"Retrieval error: {err}")
                        return f"Retrieval tool error: {err}"
                    return MDCToolFactory._format_retrieval_results(results)

                # Wrap retriever as a LangChain Tool
                self._retrieval_tool = Tool(
                    name="retrieval_search",
                    func=_retrieval_runner_google,
                    description="""Search communication records for specific themes, keywords, or patterns.
Use this for qualitative queries like:
- "Find instances of prior authorization denials"
- "Search for communication patterns with specific insurers"
- "Look for high-urgency communication themes"
Returns the top 5 most relevant communication excerpts."""
                )
            
            logger.info(f"Retrieval Tool ({self.embedding_mode} mode) initialized with {len(texts)} documents")
            return self._retrieval_tool
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to create retrieval tool: {error_msg}")
            # Return a fallback tool
            return Tool(
                name="retrieval_search",
                func=lambda query, msg=error_msg: f"Retrieval tool unavailable: {msg}",
                description="Search communication records (currently unavailable)"
            )
    
    @staticmethod
    def _format_retrieval_results(docs) -> str:
        """Format retrieval results for agent consumption."""
        if not docs:
            return "No relevant documents found."
        
        formatted = "Found relevant communications:\n"
        for i, doc in enumerate(docs, 1):
            formatted += f"\n--- Result {i} ---\n"
            formatted += f"Content: {doc.page_content}\n"
            if hasattr(doc, 'metadata') and doc.metadata:
                formatted += f"Metadata: {doc.metadata}\n"
        
        return formatted
    
    def get_tools_list(self) -> list:
        """
        Get list of all tools for the agent.
        
        Returns:
            List of Tool objects [analytics_tool, retrieval_tool]
        """
        return [
            self.create_analytics_tool(),
            self.create_retrieval_tool()
        ]
