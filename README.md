# MD Capital AI Claims Agent 🏥

An intelligent **ReAct (Reasoning + Acting) AI-powered agent** designed to analyze insurer communications for MD Capital. This tool allows management to ask natural language questions and receive data-driven insights from both structured data and unstructured communication text.

**🆕 ARCHITECTURE UPDATE:** Transitioned from monolithic CSV agent to a dual-tool ReAct system for better reasoning and transparency.

## 📁 Project Structure

```text
.
├── data/                   # Raw insurer communication data (CSV)
├── docs/
│   ├── sample_queries_outputs.md
│   ├── technology_preference.md
│   └── REACT_ARCHITECTURE.md        # ← NEW: ReAct design documentation
├── scripts/
│   ├── check_key.py
│   ├── debug_ssl.py
│   ├── test_agent.py
│   ├── test_direct.py
│   └── test_react_agent.py          # ← NEW: ReAct validation tests
├── src/
│   ├── agent.py            # ← REFACTORED: Now uses ReAct + tools
│   ├── tools.py            # ← NEW: Analytics & Retrieval tools
│   ├── utils.py            # Data processing utilities
│   ├── api/
│   │   └── server.py       # ← UPDATED: Initializes ReAct agent
│   └── ui/
│       └── app.py          # Streamlit Frontend (compatible)
├── .env.example
├── requirements.txt        # ← UPDATED: Added ReAct libraries
└── README.md               # You are here
```

## ✨ Features (Now with ReAct!)

- **Dual-Layer ReAct Analysis**: Agent automatically chooses between:
  - **Analytics Tool** (Pandas REPL): For quantitative queries (counts, averages, statistics)
  - **Retrieval Tool** (FAISS): For qualitative queries (themes, patterns, context)
  
- **Transparent Reasoning**: See agent's Thought→Action→Observation→Answer cycle
- **Client-Server Architecture**: FastAPI backend + Streamlit frontend for scalability
- **Gemini Integration**: Powered by Google's Gemini for high-speed reasoning
- **Interactive Dashboard**: Real-time charts and data exploration
- **Deep Debugging**: Verbose logging shows agent decision-making steps

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google AI Studio API Key (Gemini)

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd md-capital-agent

# Install dependencies (includes new ReAct packages)
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Running the Application
The app requires two separate processes (run in separate terminal windows):

**Step A: Start the Backend Server**
```bash
python3 -m src.api.server
```
You'll see verbose output showing agent reasoning steps (Thought/Action/Observation).

**Step B: Start the Frontend Client**
```bash
streamlit run src/ui/app.py
```

The backend will run on `http://localhost:8000` and the frontend on `http://localhost:8501`

## 🧠 ReAct Agent Architecture

### How It Works

Instead of dumping all data into a prompt, the ReAct agent **thinks strategically**:

1. **Thought** → "Is this a math question or a context question?"
2. **Action** → "I'll use the analytics tool for counts" or "I'll use retrieval for patterns"
3. **Observation** → "Here's what the tool returned"
4. **Repeat** → "Do I need another tool for context?"
5. **Final Answer** → "Here's the synthesized insight"

### The Two Tools

#### Analytics Tool (Quantitative)
```python
# Examples of questions it handles:
"How many claims are overdue?"
"What's the average urgency by insurer?"
"Count pending claims in each status"

# Uses: Python REPL + Pandas
```

#### Retrieval Tool (Qualitative)
```python
# Examples of questions it handles:
"What themes appear in denied claims?"
"Find communications about prior authorizations"
"What do high-urgency messages have in common?"

# Uses: FAISS Vector Store + Google Embeddings
```

### Example Reasoning Trace

**User:** "Which insurers have the most claims, and what's the communication tone?"

**Agent reasoning:**
```
Thought: Need counts (quantitative) AND theme analysis (qualitative)
Action 1: Call analytics_query to count claims per insurer
  → Insurer A: 45 claims, Insurer B: 32 claims
Observation: Insurer A leads. Now check communication tone.
Action 2: Call retrieval_search for tone in Insurer A communications
  → Found patterns: urgent, professional, collaborative
Final Answer: Insurer A (45 claims) communications show urgent but professional tone...
```

For detailed documentation, see [REACT_ARCHITECTURE.md](docs/REACT_ARCHITECTURE.md).

## 🛠️ Testing & Debugging

### Test the ReAct Agent
```bash
python scripts/test_react_agent.py <YOUR_API_KEY>
```

This script validates:
- Tool initialization
- Quantitative queries (analytics)
- Qualitative queries (retrieval)
- Mixed queries (both tools)

### See Agent Reasoning
Watch the backend terminal for verbose output:
```
Entering new AgentExecutor...
Thought: This is a quantitative question...
Action: I'll use analytics_query
Observation: [tool output]
Final Answer: ...
```

## 🔄 Migration from Old Agent

**What changed:**
- ❌ Old: Monolithic prompt with all data
- ✅ New: Strategic tool selection via ReAct

**What stayed the same:**
- Same CSV data format
- Same backend/frontend split
- Same Gemini model
- Same FastAPI/Streamlit tech stack

**What's new:**
- `src/tools.py` - Defines Analytics & Retrieval tools
- `scripts/test_react_agent.py` - ReAct validation
- `docs/REACT_ARCHITECTURE.md` - Complete guide
- New dependencies: LangChain, LangGraph, langchain-experimental

## 🔒 PHI/PII & Compliance
For production use at MD Capital, the following enhancements are recommended:
- **De-identification**: Implement PII scrubber (Microsoft Presidio) before LLM sees data
- **Enterprise AI**: Move to Vertex AI (Google Cloud) for HIPAA compliance
- **Audit Trails**: Log all data access and AI generation steps
- **Access Control**: Restrict API key access, use service accounts

## 📖 Documentation
- [ReAct Architecture Guide](docs/REACT_ARCHITECTURE.md) - Deep dive into dual-tool system
- [Sample Queries](docs/sample_queries_outputs.md) - Example questions and responses
- [Technology Preferences](docs/technology_preference.md) - Why these tools were chosen

---
*Built for the MD Capital AI Developer Take-Home Exercise. Updated with ReAct architecture.*
