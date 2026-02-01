# ReAct Agent Architecture Migration Guide

## Overview

Your project has been successfully transitioned from a **monolithic CSV agent** to a **ReAct (Reasoning + Acting) agent**. This document explains the new architecture and how to use it.

## 🎯 What is ReAct?

ReAct is an AI reasoning paradigm that makes LLMs **think step-by-step** and **choose their own tools**:

```
User Question
      ↓
[Thought] → Analyze what type of question this is
      ↓
[Action] → Choose appropriate tool(s)
      ↓
[Observation] → Review tool output
      ↓
[Repeat] → If more context needed, call another tool
      ↓
[Final Answer] → Synthesize insights for management
```

### Key Difference from Old Approach

**Before (Monolithic):**
- All data dumped into one giant prompt
- LLM processes everything at once
- Limited ability to reason about "which data matters"
- Slow for large datasets
- Can't verify calculations

**After (ReAct):**
- Agent chooses tools strategically
- Each tool does one job well
- Agent can verify its own reasoning
- Transparent decision-making (audit trail)
- Better handling of complex questions

---

## 🔧 New Architecture

### Two Specialized Tools

#### 1. **Analytics Tool** (The "Math Brain")
- **What it does:** Calculates statistics, counts, aggregations, filters
- **Technology:** Python REPL + Pandas
- **Use cases:**
  - "How many claims are overdue?"
  - "What's the average urgency across all insurers?"
  - "Compare claim volumes between Q1 and Q2"
  - Any COUNT, SUM, AVERAGE, or FILTER operation

```python
# Example: Agent internally calls this
df = load_data()
high_urgency = df[df['urgency'] > 8].shape[0]
print(f"High urgency claims: {high_urgency}")
```

#### 2. **Retrieval Tool** (The "Context Brain")
- **What it does:** Searches communication text for themes and patterns
- **Technology:** FAISS Vector Store + Google Embeddings
- **Use cases:**
  - "What patterns appear in denied claims?"
  - "Find communications about prior authorizations"
  - "What do high-urgency communications have in common?"
  - Any SEMANTIC SEARCH or THEME ANALYSIS

```python
# Example: Agent internally calls this
vector_db = FAISS.from_documents(communications)
results = vector_db.similarity_search("prior authorization")
# Returns top 5 most relevant communications
```

### System Message (The "Thinking Template")

The agent uses a ReAct system message that teaches it HOW to think:

```
Thought: What type of question is this? Quantitative? Qualitative? Both?
Action: Call analytics_query for math, retrieval_search for text patterns
Observation: Review what the tool returned
Repeat: Do I need more information? Call another tool.
Final Answer: Synthesis for management
```

---

## 📁 File Structure

```
src/
├── agent.py           # ← REFACTORED: Now builds ReAct agent with tools
├── tools.py           # ← NEW: Defines Analytics & Retrieval tools
├── utils.py           # ← UNCHANGED: Data loading utilities
├── api/
│   └── server.py      # ← UPDATED: Initializes agent with verbose=True
└── ui/
    └── app.py         # ← COMPATIBLE: Works with new agent

scripts/
└── test_react_agent.py  # ← NEW: Test ReAct behavior

data/
└── insurer_communications.csv  # ← Same format
    faiss_index/  # ← NEW: Vector store cache (auto-created)
```

---

## 🚀 Getting Started

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

**New packages added:**
- `langchain` - Agent orchestration
- `langchain-community` - Community integrations
- `langchain-experimental` - PythonAstREPLTool
- `langchain-text-splitters` - Text chunking for embeddings
- `faiss-cpu` - Vector similarity search
- `langgraph` - Agent framework
- `pydantic` - Data validation

### 2. Run the Backend Server

```bash
python3 -m src.api.server
```

You'll see verbose output showing:
- Tool initialization
- Agent reasoning steps (Thought/Action/Observation)
- Response synthesis

### 3. Run the Frontend UI

```bash
streamlit run src/ui/app.py
```

### 4. Ask Questions

Try different question types:

**Quantitative (Analytics Tool):**
- "How many claims are in pending status?"
- "What's the average days-since-submission?"

**Qualitative (Retrieval Tool):**
- "What communication themes appear in denied claims?"
- "Find examples of prior authorization discussions"

**Mixed (Both Tools):**
- "Which insurer has the most high-urgency claims and what are common patterns?"

---

## 🔍 Understanding Agent Reasoning

When you ask a question, watch the terminal for:

```
Entering new AgentExecutor...

Thought: This question asks for high-urgency claims AND communication patterns.
I need to use both tools.

Action: Call analytics_query to count high-urgency claims
Action Input: df[df['urgency'] > 8].groupby('insurer_name').size()

Observation: 
Insurer A: 15 high-urgency claims
Insurer B: 8 high-urgency claims

Thought: Now I need to find patterns in those communications.
Action: Call retrieval_search for high-urgency communication themes
Action Input: "urgent communication patterns high priority"

Observation:
[Found 5 relevant communications about urgent processing requirements]

Final Answer: Insurer A leads with 15 high-urgency claims...
[Full synthesis]
```

---

## 🛠️ Advanced Configuration

### Adjusting Agent Behavior

Edit `src/agent.py` to modify:

```python
# Max iterations before timeout
max_iterations=10

# Early stopping when confident answer found
early_stopping_method="generate"

# Parsing error handling
handle_parsing_errors=True

# Enable/disable verbose reasoning trace
verbose=True  # Set to False for production
```

### Customizing the System Message

Edit `REACT_SYSTEM_MESSAGE` in `src/agent.py` to:
- Add domain-specific guidance
- Change reasoning priorities
- Add compliance instructions

### Tuning Retrieval

In `src/tools.py`:

```python
# Number of similar documents to return
search_kwargs={"k": 5}  # Increase for broader context

# Change similarity metric
search_type="similarity"  # or "mmr" for diversity
```

---

## 📊 Example: How It Works End-to-End

**User asks:** "Are there patterns in why insurers deny claims?"

**Agent reasoning:**

1. **Thought:** This is asking for QUALITATIVE analysis (why/patterns).
   I should search communications for denial themes.

2. **Action:** Call `retrieval_search` with query "denial reasons patterns"

3. **Observation:** 
   - Returned 5 documents mentioning: insufficient documentation, policy exclusions, timeliness issues
   
4. **Thought:** I should quantify this. How many denials are there total?
   Call `analytics_query` to count denials.

5. **Action:** Execute `df[df['claim_status'] == 'denied'].shape[0]`

6. **Observation:** Total denials: 23

7. **Final Answer:** 
   "Analysis of 23 denied claims reveals three primary patterns:
   - Insufficient documentation (12/23 cases = 52%)
   - Policy exclusions (7/23 cases = 30%)
   - Timeliness requirements (4/23 cases = 17%)"

---

## 🐛 Troubleshooting

### Agent Hangs / Takes Too Long

- Reduce `max_iterations` in `agent.py`
- Check if vector store is too large
- Verify API quota not exceeded

### Tool Returns Errors

**Analytics Tool Errors:**
- Check DataFrame column names
- Verify pandas syntax

**Retrieval Tool Errors:**
- Check embedding API quota (Google)
- Verify `communication_text` column exists

### "No communication texts available"

- Ensure CSV has `communication_text` column
- Ensure text column is not empty
- Check for null/NaN values

---

## 📋 System Message (Full Reference)

The agent uses this template to think:

```
You are the MD Capital Operational Intelligence Agent. 

Your role is to analyze insurer communications and provide 
data-driven insights to management.

**ReAct Reasoning Cycle:**

1. **Thought**: Analyze request - quantitative? qualitative? both?
2. **Action**: Select tool - analytics_query or retrieval_search
3. **Observation**: Review tool output carefully
4. **Repeat**: Need more info? Call another tool
5. **Final Answer**: Concise professional summary

**Rules:**
- ALWAYS use tools (don't rely on training data)
- Be specific ("3 claims" not "several")
- Use both tools if needed
- Log reasoning for audit trail
```

---

## ✅ Validation Checklist

- [ ] New packages installed: `pip install -r requirements.txt`
- [ ] Backend starts: `python3 -m src.api.server`
- [ ] Frontend loads: `streamlit run src/ui/app.py`
- [ ] Test query works and shows Thought/Action/Observation logs
- [ ] Analytics tool calculates correctly
- [ ] Retrieval tool returns relevant communications
- [ ] Mixed queries use both tools appropriately

---

## 📚 References

- **LangChain Agents:** https://python.langchain.com/docs/modules/agents/
- **ReAct Paper:** https://arxiv.org/abs/2210.03629
- **FAISS:** https://ai.meta.com/tools/faiss/
- **Gemini API:** https://ai.google.dev/

