# ReAct Agent: Visual Reference Guide

A quick visual guide to understand the ReAct architecture at a glance.

---

## 1. The ReAct Loop (How Agent Thinks)

```
┌─────────────────────────────────────────┐
│         USER QUESTION                   │
│  "Which insurer has most pending        │
│   claims and what's causing delays?"    │
└──────────────┬──────────────────────────┘
               │
               ↓
   ┌────────────────────────┐
   │  THOUGHT               │
   │  "I need both:        │
   │   - Counts (math)     │
   │   - Themes (reasons)" │
   └────────────┬───────────┘
                │
         ┌──────┴──────┐
         │             │
         ↓             ↓
   [ACTION 1]     [ACTION 2]
   Analytics      Retrieval
   Tool Call      Tool Call
         │             │
         ↓             ↓
   [OBSERVATION 1] [OBSERVATION 2]
   Insurer A:      Communication
   42 pending      themes found
         │             │
         └──────┬──────┘
                │
                ↓
   ┌─────────────────────────┐
   │  FINAL ANSWER           │
   │  Insurer A has 42 of    │
   │  pending, primarily due │
   │  to [themes found]      │
   └─────────────────────────┘
                │
                ↓
           USER SEES ANSWER
```

---

## 2. Tool Selection Decision Tree

```
                    QUESTION
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ↓             ↓             ↓
      "HOW MANY?"  "WHAT ARE?"   "WHY DO?"
      "WHAT'S THE  "FIND"        "COMPARE
       AVERAGE?"   "THEMES?"     & EXPLAIN"
         │             │             │
         ↓             ↓             ↓
   [ANALYTICS]  [RETRIEVAL]     [BOTH]
   ✓ Counts     ✓ Text search   ✓ Analytics
   ✓ Averages   ✓ Patterns      + Retrieval
   ✓ Statistics ✓ Explanations  = Synthesis

   EXAMPLES:           EXAMPLES:         EXAMPLES:
   "How many          "What themes      "Which insurer
    pending?"          appear in         & why do they
                       urgent?"          have delays?"
   "What's the
    average days?"     "Find examples
                        of denials"
```

---

## 3. Tool Capabilities Matrix

```
┌──────────────────────────────────────────────────────────────┐
│                    ANALYTICS TOOL                             │
│                  (Pandas REPL)                                │
├──────────────────────────────────────────────────────────────┤
│ INPUT:  "df[df['status']=='pending'].shape[0]"              │
│ OUTPUT: 45                                                    │
│                                                                │
│ CAN DO:                    CAN'T DO:                          │
│ ✓ Count rows               ✗ Semantic understanding          │
│ ✓ Calculate averages       ✗ Explain "why"                   │
│ ✓ Group and filter         ✗ Find patterns in text           │
│ ✓ Compare metrics          ✗ Understand context              │
│ ✓ Handle time series       ✗ Access external info            │
├──────────────────────────────────────────────────────────────┤
│                    RETRIEVAL TOOL                              │
│                  (FAISS Vector Search)                         │
├──────────────────────────────────────────────────────────────┤
│ INPUT:  "prior authorization denials"                        │
│ OUTPUT: Top 5 similar communication texts                    │
│                                                                │
│ CAN DO:                    CAN'T DO:                          │
│ ✓ Semantic search          ✗ Calculate statistics            │
│ ✓ Find similar text        ✗ Count occurrences               │
│ ✓ Identify themes          ✗ Compare numerical values        │
│ ✓ Retrieve context         ✗ Precise filtering               │
│ ✓ Explain patterns         ✗ Do math operations              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Diagram

```
START
 │
 ├─ Load CSV Data
 │   ├─ insurer_communications.csv
 │   └─ 100+ records
 │
 ├─ Initialize Tools
 │   ├─ Analytics Tool (Pandas)
 │   │  └─ Ready for math queries
 │   └─ Retrieval Tool (FAISS)
 │      ├─ Create embeddings
 │      ├─ Build vector store
 │      └─ Ready for search queries
 │
 ├─ User asks question
 │   └─ "Why do urgent claims..."
 │
 ├─ Agent thinks & decides
 │   ├─ Quantitative? → Use Analytics
 │   ├─ Qualitative?  → Use Retrieval
 │   └─ Both?         → Use Both
 │
 ├─ Execute tools
 │   ├─ Tool 1 → Data/Results
 │   ├─ Tool 2 → More Data/Results
 │   └─ Combine → Synthesis
 │
 └─ Return answer
    └─ User gets response
```

---

## 5. Query Routing Examples

```
┌─────────────────────────────┐
│  "How many claims pending?" │
└──────────────┬──────────────┘
               │
               ├─→ Identify: COUNTING/QUANTITATIVE
               │
               ├─→ Decision: Use Analytics Tool
               │
               ├─→ Execute: df[df['status']=='pending'].shape[0]
               │
               └─→ Return: "42 claims pending"

┌──────────────────────────────────────────┐
│  "What patterns in high-urgency claims?" │
└──────────────┬─────────────────────────┘
               │
               ├─→ Identify: PATTERN/THEME/QUALITATIVE
               │
               ├─→ Decision: Use Retrieval Tool
               │
               ├─→ Execute: Search "urgent claims patterns"
               │
               └─→ Return: [Communication texts + themes]

┌────────────────────────────────────────────────────┐
│  "Which insurer has most claims & why the delays?" │
└──────────────┬─────────────────────────────────────┘
               │
               ├─→ Identify: HYBRID (Count + Reason)
               │
               ├─→ Decision: Use BOTH Tools
               │
               ├─→ Execute Tool 1: df.groupby('insurer').size()
               │   → Result: Insurer A has 45 claims
               │
               ├─→ Execute Tool 2: Search "Insurer A delays"
               │   → Result: 5 communication themes
               │
               └─→ Return: Synthesis of both findings
```

---

## 6. System Message Structure

```
┌──────────────────────────────────────────────────────┐
│    YOU ARE MD CAPITAL OPERATIONAL AGENT              │
│                                                       │
│  YOUR ROLE: Analyze insurer communications          │
│  YOUR GOAL: Provide data-driven insights            │
│                                                       │
│  YOUR METHOD: The ReAct Cycle                        │
│  ┌──────────────────────────────────────────────┐   │
│  │ 1. THOUGHT                                    │   │
│  │    Analyze request:                          │   │
│  │    - Quantitative? (math/counts)             │   │
│  │    - Qualitative? (themes/reasons)           │   │
│  │    - Both?                                    │   │
│  │                                               │   │
│  │ 2. ACTION                                     │   │
│  │    Choose tool:                              │   │
│  │    - Analytics for numbers                   │   │
│  │    - Retrieval for text/patterns             │   │
│  │                                               │   │
│  │ 3. OBSERVATION                                │   │
│  │    Review tool output                        │   │
│  │    Extract key insights                      │   │
│  │                                               │   │
│  │ 4. REPEAT (if needed)                        │   │
│  │    Call another tool for completeness        │   │
│  │                                               │   │
│  │ 5. FINAL ANSWER                              │   │
│  │    Synthesize for management                 │   │
│  └──────────────────────────────────────────────┘   │
│                                                       │
│  YOUR RULES:                                         │
│  ✓ Always use tools (don't guess)                   │
│  ✓ Be specific ("3" not "several")                  │
│  ✓ Support with data/evidence                       │
│  ✓ Log your reasoning steps                         │
└──────────────────────────────────────────────────────┘
```

---

## 7. Code Architecture

```
MD Capital Project
│
├─ src/
│  │
│  ├─ agent.py ──────────────┬──────────────────────────┐
│  │  ├─ ChatGoogleGenerativeAI (LLM)                  │
│  │  ├─ initialize_agent (ReAct setup)                │
│  │  ├─ ReAct System Message                          │
│  │  └─ Agent reasoning loop                          │
│  │
│  ├─ tools.py (NEW) ────────┬──────────────────────────┐
│  │  └─ MDCToolFactory                                │
│  │     ├─ create_analytics_tool()                    │
│  │     │  └─ PythonAstREPLTool + Pandas              │
│  │     └─ create_retrieval_tool()                    │
│  │        └─ FAISS + GoogleEmbeddings                │
│  │
│  ├─ utils.py ──────────────┬──────────────────────────┐
│  │  ├─ load_data()          # Load CSV               │
│  │  └─ get_data_summary()   # Get stats              │
│  │
│  ├─ api/
│  │  └─ server.py ────────────┬──────────────────────┐
│  │     ├─ Initialize agent (with tools)             │
│  │     ├─ /ask endpoint → agent.run(question)       │
│  │     └─ Verbose output → Shows reasoning          │
│  │
│  └─ ui/
│     └─ app.py ──────────────┬──────────────────────┐
│        ├─ Streamlit UI                              │
│        ├─ Send queries to /ask endpoint             │
│        └─ Display results                           │
│
├─ data/
│  └─ insurer_communications.csv
│     ├─ Loaded by agent on startup
│     └─ Used by both tools
│
└─ scripts/
   ├─ test_react_agent.py (NEW)
   │  ├─ Test quantitative queries
   │  ├─ Test qualitative queries
   │  └─ Test mixed queries
   └─ ... other scripts
```

---

## 8. Performance Characteristics

```
RESPONSE TIME BREAKDOWN:

Simple Quantitative Question (e.g., "How many pending?")
────────────────────────────────────────────────────
0ms    Agent reads question
100ms  LLM analyzes → "Use analytics tool"
200ms  Execute Pandas query
300ms  LLM formats answer
────────────────────────────────────────────────────
~2-3 seconds TOTAL

Simple Qualitative Question (e.g., "What patterns?")
────────────────────────────────────────────────────
0ms    Agent reads question
100ms  LLM analyzes → "Use retrieval tool"
1000ms Vector search (embedding API call)
200ms  LLM formats results
────────────────────────────────────────────────────
~3-4 seconds TOTAL

Complex Mixed Question (Both tools)
────────────────────────────────────────────────────
0ms    Agent reads question
100ms  LLM analyzes → "Need both tools"
200ms  Execute Tool 1 (Analytics)
1000ms Execute Tool 2 (Retrieval)
300ms  LLM synthesizes both
────────────────────────────────────────────────────
~5-7 seconds TOTAL

First Request (Vector Store Initialization)
────────────────────────────────────────────────────
~5-10 seconds EXTRA (one-time setup)
```

---

## 9. Tool Execution Example (Verbose View)

```
User Input:
─────────────────────────────────────────────────
"Which insurers have most high-urgency claims?"
─────────────────────────────────────────────────

Agent Reasoning (Shown in Backend Terminal):
─────────────────────────────────────────────────
Entering new AgentExecutor...

Thought: The user is asking which insurers have the most 
high-urgency claims. This is a QUANTITATIVE question that 
requires:
1) Filtering for high urgency (urgency > 7)
2) Grouping by insurer
3) Counting

I should use the analytics_query tool.

Action: Use analytics_query to count high-urgency claims by insurer

Action Input: df[df['urgency'] > 7].groupby('insurer_name').size().sort_values(ascending=False)

Observation: 
Insurer A    12
Insurer B     8
Insurer C     5

Thought: I have the answer.

Final Answer:
─────────────────────────────────────────────────
Insurer A has the most high-urgency claims with 12, 
followed by Insurer B with 8, and Insurer C with 5.
─────────────────────────────────────────────────
```

---

## 10. Decision Quality Indicators

```
GOOD AGENT DECISIONS:

Question: "How many pending claims?"
Agent decides: "Use Analytics" ✓ CORRECT
(Quantitative → Math tool)

Question: "What themes in urgent communications?"
Agent decides: "Use Retrieval" ✓ CORRECT
(Qualitative → Text search tool)

Question: "Which insurer delays most and why?"
Agent decides: "Use both tools" ✓ CORRECT
(Hybrid → Analytics for counts + Retrieval for why)


POOR AGENT DECISIONS:

Question: "How many pending claims?"
Agent decides: "Use Retrieval" ✗ WRONG
(Should use Analytics for counting)

Question: "What themes?"
Agent decides: "Use only Analytics" ✗ WRONG
(Should use Retrieval for pattern finding)
```

---

## 11. Error Handling Flow

```
Agent tries to execute query
│
├─ Success
│  └─ Return result to user
│
└─ Failure
   ├─ Tool returns error message
   │  └─ Agent sees error
   │     ├─ Tries different approach? (Retry)
   │     └─ Gives up gracefully (Fallback)
   │
   └─ LLM returns error
      └─ Return error to user
         ├─ "Dataframe is empty"
         ├─ "Tool not available"
         └─ "Query timeout"
```

---

## 12. Quick Reference: When to Use Which Tool

```
ANALYTICS TOOL                  RETRIEVAL TOOL
(Pandas Math)                   (FAISS Search)
─────────────────────────────────────────────────
✓ Count rows                     ✓ Find themes
✓ Calculate average              ✓ Find reasons
✓ Group data                      ✓ Search patterns
✓ Filter records                  ✓ Get examples
✓ Compare metrics                 ✓ Semantic search
✓ Statistical analysis            ✓ Understand context
✓ Distribution analysis           ✓ Find similar cases

KEYWORDS:                        KEYWORDS:
- "how many"                     - "what themes"
- "average/mean"                 - "why"
- "total/sum"                    - "patterns"
- "which insurer"                - "find"
- "compare"                      - "examples"
- "percent"                      - "reasons"
- "count"                        - "common"
```

---

## Summary

The **ReAct Agent** is your data assistant that:

1. 🧠 **THINKS** about what you're asking
2. 🎯 **CHOOSES** the right tool(s)
3. 🔍 **OBSERVES** what the tools return
4. 🔄 **REPEATS** if needed for complete answer
5. 📝 **ANSWERS** with data-driven insights

All thinking is transparent—you see every step in the verbose logs!

