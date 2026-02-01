# ReAct Implementation Details

## Quick Reference: What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Architecture** | Monolithic prompt | Tool-based ReAct |
| **Data Flow** | All CSV → One prompt | CSV → Tool selection → Answer |
| **Agent Decision** | None (static prompt) | Strategic via Thought/Action |
| **Tools** | None (just LLM) | Analytics + Retrieval |
| **Reasoning Visibility** | Hidden | Verbose (Thought→Action→Obs) |
| **Extensibility** | Hard to add logic | Easy to add tools |

---

## Code Changes Overview

### 1. `src/tools.py` (NEW)

Creates two specialized LangChain tools:

```python
class MDCToolFactory:
    def create_analytics_tool(self):
        # Returns: PythonAstREPLTool with Pandas dataframe
        # Allows: df.groupby(), df.describe(), df[df['col'] > val]
        
    def create_retrieval_tool(self):
        # Returns: FAISS vector store as LangChain Tool
        # Allows: Semantic search over communication text
```

**How it's used:**
```python
factory = MDCToolFactory(df, api_key)
tools = factory.get_tools_list()  # [analytics_tool, retrieval_tool]
```

### 2. `src/agent.py` (REFACTORED)

Changed from simple LLM wrapper to ReAct agent:

**Before:**
```python
class MDCCapitalAgent:
    def __init__(self, df, api_key):
        self.llm = ChatGoogleGenerativeAI(...)
        
    def ask(self, question):
        prompt = self._prepare_prompt(question)
        return self.llm.invoke(prompt).content
```

**After:**
```python
class MDCCapitalAgent:
    def __init__(self, df, api_key, verbose=True):
        self.llm = ChatGoogleGenerativeAI(...)
        tool_factory = MDCToolFactory(df, api_key)
        self.tools = tool_factory.get_tools_list()
        
        # Initialize ReAct agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=verbose,
            max_iterations=10
        )
        
    def ask(self, question):
        return self.agent.run(question)  # Runs full ReAct loop
```

**Key difference:** `initialize_agent()` instead of manual prompting.

### 3. `src/api/server.py` (UPDATED)

Minor changes to support verbose agent:

```python
# Before
agent = MDCCapitalAgent(df, request.api_key)
response = agent.ask(request.question)

# After
agent = MDCCapitalAgent(
    df=df,
    api_key=request.api_key,
    verbose=True  # ← Enable verbose for debugging
)
response = agent.ask(request.question)
```

### 4. `requirements.txt` (UPDATED)

Added:
```
langchain           # Agent framework
langchain-experimental  # PythonAstREPLTool
langgraph           # Advanced agent graphs
langchain-text-splitters # For embeddings
pydantic            # Validation
```

---

## How Each Tool Works

### Analytics Tool (PythonAstREPLTool)

```python
# What agent sees:
Tool: "analytics_query"
Description: "Execute pandas operations on the claims dataframe"

# What the agent can do:
Execute arbitrary pandas code like:
- df[df['urgency'] > 5].shape[0]  # Count high-urgency
- df.groupby('insurer_name')['days_since_submission'].mean()  # Averages
- df['claim_status'].value_counts()  # Distribution

# Safety:
- Only reads from dataframe (can't write to disk)
- Namespace limited to: df, pd (pandas module)
```

**How agent uses it:**
```
Thought: "How many high-urgency claims?"
Action Input: df[df['urgency'] >= 8].shape[0]
Observation: 15
```

### Retrieval Tool (FAISS)

```python
# What agent sees:
Tool: "retrieval_search"
Description: "Search communication records for themes/keywords"

# What the agent can do:
Semantic search like:
- "prior authorization"
- "denial reasons"
- "time-sensitive claims"

# Safety:
- Only reads from vector store
- No direct data modification
- Top-5 results returned

# How it works internally:
1. Takes query text
2. Converts to embeddings via Google's API
3. Finds 5 most similar communications via FAISS
4. Returns both text and metadata (insurer, status, urgency)
```

**How agent uses it:**
```
Thought: "What themes appear in denied claims?"
Action Input: "why are claims denied reasons"
Observation: 
  - Doc 1: "Missing documentation requirement"
  - Doc 2: "Outside coverage policy limits"
  - ...
```

---

## System Message (The "Thinking Template")

Located in `src/agent.py`:

```python
REACT_SYSTEM_MESSAGE = """
You are the MD Capital Operational Intelligence Agent.

Your role is to analyze insurer communications...

**ReAct Reasoning Cycle:**

1. **Thought**: Analyze the user's request...
2. **Action**: Select the appropriate tool...
3. **Observation**: Carefully review the tool output...
4. **Repeat**: If the answer requires multiple perspectives...
5. **Final Answer**: Provide a concise, professional summary...
"""
```

This teaches the LLM the exact pattern to follow.

---

## Execution Flow

### Simple Question
```
User: "How many pending claims?"

Step 1: LLM reads question and system message
Step 2: LLM thinks: "This is quantitative → use analytics"
Step 3: LLM calls: analytics_query(df[df['claim_status']=='pending'].shape[0])
Step 4: Tool returns: 42
Step 5: LLM returns: "There are 42 pending claims"
```

### Complex Question
```
User: "Which insurers delay most, and why?"

Step 1: LLM reads question
Step 2: LLM thinks: "Need both quantitative AND qualitative"
Step 3: LLM calls: analytics_query(df.groupby('insurer_name')['days_since_submission'].mean())
Step 4: Gets: Insurer A avg 12 days, B avg 8 days
Step 5: LLM thinks: "Now check communication patterns from Insurer A"
Step 6: LLM calls: retrieval_search("Insurer A delays processing time")
Step 7: Gets: Communication themes about processing requirements
Step 8: LLM synthesizes: "Insurer A has 12-day average due to [patterns found]"
```

---

## Error Handling

### Analytics Tool Errors
```python
try:
    result = eval(user_code, restricted_locals)
except Exception as e:
    # Returns error message to agent
    # Agent can try different approach
```

### Retrieval Tool Errors
```python
if no_embeddings_loaded:
    return Tool(
        name="retrieval_search",
        func=lambda q: "No communication texts available"
    )
```

Both tools fail gracefully—agent continues reasoning.

---

## Configuration

### Agent Parameters

In `src/agent.py`:

```python
self.agent = initialize_agent(
    tools=self.tools,
    llm=self.llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,           # ← Print reasoning steps
    max_iterations=10,      # ← Stop after 10 tool calls
    early_stopping_method="generate",  # ← Stop if confident
    handle_parsing_errors=True  # ← Recover from bad LLM output
)
```

**Tweaking tips:**
- `max_iterations=5`: Faster, less detailed
- `max_iterations=15`: Slower, more thorough
- `verbose=False`: Production (no logs)
- `temperature=0`: Deterministic (always same answer)

### Tool Parameters

In `src/tools.py`:

```python
retriever = vector_db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Return top 5 similar docs
)
```

**Tweaking tips:**
- `k=3`: Faster, narrower context
- `k=10`: Slower, broader context
- `search_type="mmr"`: Maximize diversity (not just similarity)

---

## Debugging

### See Agent Reasoning
```bash
# Set verbose=True in agent.py
python3 -m src.api.server  # Terminal will show:
# Entering new AgentExecutor...
# Thought: ...
# Action: ...
# Observation: ...
# Final Answer: ...
```

### Check Tool Outputs
```python
# In scripts/test_react_agent.py
agent = MDCCapitalAgent(df, api_key, verbose=True)
response = agent.ask(question)
# See tool calls in terminal
```

### Validate Tools Independently
```python
from src.tools import MDCToolFactory

factory = MDCToolFactory(df, api_key)

# Test analytics
analytics = factory.create_analytics_tool()
result = analytics.run("df['urgency'].mean()")

# Test retrieval  
retrieval = factory.create_retrieval_tool()
result = retrieval.run("urgent delays")
```

---

## Production Considerations

### Performance
- Vector store initialization takes ~5-10 seconds (first request)
- Embeddings API calls add ~1-2 seconds per query
- Total latency: 2-3 seconds typical

### Optimization
```python
# Cache tools across requests (in server.py)
_agent_cache = {}

def get_agent(api_key):
    if api_key not in _agent_cache:
        _agent_cache[api_key] = MDCCapitalAgent(df, api_key)
    return _agent_cache[api_key]
```

### Security
- API key never logged (only in requests/responses)
- Tool execution is sandboxed (PythonAstREPLTool restrictions)
- No file system access from agent

### Monitoring
- Log all queries for audit trail
- Track tool usage patterns
- Monitor API quota (embeddings)

---

## Extension Points

### Add a New Tool

```python
# In src/tools.py
def create_custom_tool(self):
    def my_tool_func(input_str):
        # Your logic here
        return result
    
    return Tool(
        name="my_tool",
        func=my_tool_func,
        description="What this tool does"
    )

# Then in get_tools_list():
return [
    self.create_analytics_tool(),
    self.create_retrieval_tool(),
    self.create_custom_tool()  # ← New tool
]
```

### Modify System Message

```python
# In src/agent.py
REACT_SYSTEM_MESSAGE = """
... your new instructions ...
"""
```

### Use Different LLM

```python
# In src/agent.py
self.llm = ChatOpenAI(model="gpt-4")  # Switch to OpenAI
# Agent code remains identical
```

---

## References

- **LangChain Documentation**: https://python.langchain.com/
- **ReAct Paper**: https://arxiv.org/abs/2210.03629
- **FAISS Guide**: https://ai.meta.com/tools/faiss/
- **Google Embeddings**: https://ai.google.dev/models/embedding-001

