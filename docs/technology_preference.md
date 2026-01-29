# Technology Preference Sheet

**Candidate Name**: Antigravity (AI Assistant)
**Position**: AI Developer

## Chosen Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.10 | Industry standard for AI/ML with extensive library support. |
| **LLM** | Google Gemini 1.5 Pro | State-of-the-art reasoning with a massive context window, ideal for complex medical claim analysis. |
| **Framework** | LangChain | Robust toolkit for building agentic workflows and tool integration. |
| **Vector DB** | FAISS | High-performance similarity search for semantic communication analysis. |
| **UI Framework** | Streamlit | Rapid development of professional, interactive data dashboards. |
| **Data Analysis** | Pandas | Powerful structured data manipulation and statistical analysis. |

## Implementation Approach
My solution uses a **Hybrid Agentic Architecture**. Instead of a simple RAG system, I implemented a **ReAct (Reasoning + Acting) Agent** that can choose between:
1. **Deterministic Analysis**: Using a Pandas Agent to execute precise Python code for quantitative questions (e.g., "What percentage of denials...").
2. **Semantic Analysis**: Using a Vector Retriever to find patterns in unstructured communication text (e.g., "What characterizes urgency 5...").

This approach ensures high accuracy for data-driven questions while maintaining the flexibility of natural language understanding for qualitative insights.
