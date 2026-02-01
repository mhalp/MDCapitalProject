# MD Capital Intelligence System

A premium AI-powered analytics platform for insurer communication analysis. This system leverages Large Language Models (Gemini 2.0) to provide data-driven insights into insurance claims, urgency levels, and turnaround times.

## 🚀 Overview

The MD Capital Intelligence System consists of a robust FastAPI backend and a sophisticated Streamlit frontend, providing a seamless bridge between raw data streams and actionable business intelligence.

### Key Features
- **AI-Powered Query Engine**: Natural language interface for complex data analysis.
- **Interactive Analytics Dashboard**: Visualizes claim status distributions and urgency variances.
- **Operational Metrics**: Real-time tracking of total records, insurer counts, and performance averages.
- **Enterprise-Ready Connectivity**: Built-in support for custom SSL environments and filtered network traffic.

## 🛠 Technology Stack
- **Frontend**: [Streamlit](https://streamlit.io/) (High-performance UI)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous API layer)
- **AI Engine**: [Google Gemini 2.0](https://deepmind.google/technologies/gemini/) (via LangChain)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [Seaborn](https://seaborn.pydata.org/)

## 📂 Project Structure
```text
MD/
├── src/
│   ├── api/            # FastAPI Backend
│   │   └── server.py
│   ├── ui/             # Streamlit Frontend
│   │   ├── app.py
│   │   └── assets/     # UI Assets (Logo, Icons)
│   ├── agent.py        # LangChain Agent Logic
│   └── utils.py        # Shared Utilities
├── data/               # Source Datasets
├── dev_tools/          # Diagnostic & Script Archive
├── requirements.txt    # System Dependencies
└── README.md
```

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
BACKEND_URL=http://localhost:8000
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Running the System
The system requires both the backend and frontend to be active.

**Start the Backend:**
```bash
python -m src.api.server
```

**Start the Frontend:**
```bash
streamlit run src/ui/app.py
```

## 🔒 Security & Connectivity
The system is designed to operate in restricted network environments. It automatically detects and uses custom SSL certificates (`combined.pem` or `etrog.crt`) to ensure secure communication with Google APIs.

---
© 2026 MD Capital | Proprietary AI Solutions
