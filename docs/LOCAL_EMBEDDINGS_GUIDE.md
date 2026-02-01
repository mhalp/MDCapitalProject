# Local Embeddings Guide

## Overview
The MD Capital ReAct Agent now supports **local embeddings** via SentenceTransformers + FAISS. This eliminates the need for:
- Google API keys (for embeddings)
- Network calls to embedding services
- Embedding quota limits
- API costs

## Why Local Embeddings?

| Aspect | Google Embeddings | Local Embeddings |
|--------|-------------------|------------------|
| **API Key Required** | ✅ Yes | ❌ No |
| **Network Calls** | ✅ Yes | ❌ No |
| **Quota Limits** | ✅ Yes | ❌ No |
| **Cost** | ✅ Per request | ❌ Free (one-time download) |
| **Data Privacy** | ⚠️ Sent to Google | ✅ Stays local |
| **Speed** | ⚠️ Network latency | ✅ Fast (local) |
| **Offline Support** | ❌ No | ✅ Yes (after first download) |

## Quick Start

### 1. Install Dependencies
```bash
pip install sentence-transformers faiss-cpu
```
(Already in `requirements.txt`)

### 2. Create Agent with Local Embeddings

```python
from src.utils import load_data
from src.agent import MDCCapitalAgent

# Load data
df = load_data('data/insurer_communications.csv')

# Create agent with local embeddings (default)
agent = MDCCapitalAgent(
    df=df,
    api_key='any-value',  # Still needed for Gemini LLM (not embeddings)
    embedding_mode='local'  # <-- This switches to local embeddings!
)

# Ask a question
result = agent.ask("Find communications with prior authorization denials")
print(result)
```

### 3. What Gets Logged

When using local embeddings, you'll see terminal output like:

```
[TOOL CALL] retrieval_search | Reason: qualitative (search for themes/phrases) | Input: prior authorization denial
```

The retrieval tool will search the local FAISS index instantly (no API calls).

## API Modes

### Local Mode (Default)
```python
agent = MDCCapitalAgent(
    df=df,
    api_key='dummy',
    embedding_mode='local'  # Uses SentenceTransformers + FAISS
)
```

- **Model**: `all-MiniLM-L6-v2` (lightweight, 90.9MB)
- **Speed**: ~40ms per query
- **Quality**: Good for general text similarity
- **Cost**: Free (one-time 90MB download)

### Google Mode (If you have API key + quota)
```python
agent = MDCCapitalAgent(
    df=df,
    api_key='YOUR_GOOGLE_API_KEY',
    embedding_mode='google'  # Uses Google Generative AI embeddings
)
```

- **Model**: `models/embedding-001` (Google's latest)
- **Speed**: ~500ms per query (includes network latency)
- **Quality**: Potentially higher but depends on your data
- **Cost**: ~$0.02 per million tokens (when quota available)

## Model Options (Local)

To use a different SentenceTransformer model, edit `src/tools.py`:

```python
# Line ~176: Change this
model = SentenceTransformer("all-MiniLM-L6-v2")

# To any model from HuggingFace, e.g.:
model = SentenceTransformer("all-mpnet-base-v2")  # Better quality, larger (438MB)
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")  # Multilingual
```

Popular choices:
| Model | Size | Dim | Quality | Speed |
|-------|------|-----|---------|-------|
| `all-MiniLM-L6-v2` | 90MB | 384 | Good | ✓ Fast |
| `all-mpnet-base-v2` | 438MB | 768 | Better | Slower |
| `all-roberta-large-v1` | 713MB | 1024 | Excellent | Slow |

## Terminal Logging

Both analytics and retrieval tools log their invocations:

```
[TOOL CALL] analytics_query | Reason: quantitative (pandas expression) | Input: len(df)
[TOOL CALL] retrieval_search | Reason: qualitative (search for themes/phrases) | Input: prior authorization denial
```

These are printed to stdout + logger.info for debugging.

## Performance Notes

### First Run (One-time)
- SentenceTransformer model downloads ~90MB (cached in `~/.cache/huggingface/hub/`)
- FAISS index built from 40 documents: ~1 second
- Total setup: ~2-5 seconds (depending on internet)

### Subsequent Runs
- Model loads from cache: ~0.5 seconds
- FAISS index in memory: instant
- Per-query retrieval: ~40ms

## Switching Between Modes

If you have both options:

```python
# Use local by default (no API needed)
agent_local = MDCCapitalAgent(df, "dummy", embedding_mode='local')

# Switch to Google if you want (needs valid API key)
agent_google = MDCCapitalAgent(df, os.getenv('GOOGLE_API_KEY'), embedding_mode='google')
```

## Troubleshooting

**Q: SentenceTransformers not found?**
```bash
pip install sentence-transformers
```

**Q: FAISS not found?**
```bash
pip install faiss-cpu  # or faiss-gpu if you have CUDA
```

**Q: Model download fails?**
Set Hugging Face token:
```bash
pip install --upgrade huggingface-hub
huggingface-cli login
```

**Q: Slow on first run?**
Normal. It's downloading the model. Subsequent runs use cache.

**Q: Similarity scores are low?**
Try a better model: `all-mpnet-base-v2` (larger but higher quality)

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         MDCCapitalAgent                     │
│  (ReAct + Gemini LLM for reasoning)         │
└────────────┬────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
   Tool 1        Tool 2
┌────────────┐ ┌──────────────┐
│ Analytics  │ │ Retrieval    │
│ (Pandas)   │ │ (Local FAISS)│
└────────────┘ └──────────────┘
                      │
             ┌────────┴─────────┐
             │                  │
      SentenceTransformer    FAISS Index
      (all-MiniLM-L6-v2)     (384-dim)
      (LOCAL, no API calls)
```

## Summary

✅ **Local embeddings are the new default** (`embedding_mode='local'`)  
✅ **No API key required for embeddings** (only for Gemini LLM)  
✅ **Faster, cheaper, more private than cloud embeddings**  
✅ **Drop-in replacement for Google embeddings**  

To use: just pass `embedding_mode='local'` when creating the agent!
