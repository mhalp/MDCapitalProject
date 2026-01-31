# MD Capital AI Claims Agent 🏥

An intelligent AI-powered agent designed to analyze insurer communications for MD Capital. This tool allows management to ask natural language questions and receive data-driven insights from both structured data and unstructured communication text.

## 📁 Project Structure

```text
.
├── data/                   # Raw insurer communication data (CSV)
├── docs/                   # Documentation and sample outputs
├── scripts/                # Utility and debugging scripts
├── src/
│   ├── api/                # FastAPI Backend Server
│   ├── ui/                 # Streamlit Frontend Client
│   ├── agent.py            # Core AI Agent logic (Gemini)
│   └── utils.py            # Data processing utilities
├── .env.example            # Template for environment variables
├── requirements.txt        # Project dependencies
└── README.md               # You are here
```

## ✨ Features
- **Dual-Layer Analysis**: Processes structured metrics (status, urgency) alongside unstructured text.
- **Client-Server Architecture**: Separated Backend (FastAPI) and Frontend (Streamlit) for scalability and easier debugging.
- **Gemini Integration**: Powered by Google's Gemini 1.5 Flash for high-speed, intelligent reasoning.
- **Interactive Dashboard**: Premium UI with real-time charts and data exploration.
- **Deep Debugging**: Built-in logging and instrumentation to track AI reasoning steps.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google AI Studio API Key (Gemini)

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd md-capital-agent

# Install dependencies
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

**Step B: Start the Frontend Client**
```bash
streamlit run src/ui/app.py
```

The backend will run on `http://localhost:8000` and the frontend on `http://localhost:8501`

## 🛠️ Debugging & Testing
You can test the AI agent logic without the UI using the provided script:
```bash
python scripts/test_agent.py <YOUR_API_KEY>
```

## 🔒 PHI/PII & Compliance
For production use at MD Capital, the following enhancements are recommended:
- **De-identification**: Implement a PII scrubber (like Microsoft Presidio) before data reaches the LLM.
- **Enterprise AI**: Move to Vertex AI (Google Cloud) for enterprise-grade security and HIPAA compliance.
- **Audit Trails**: Enable comprehensive logging of all data access and AI generations.

---
*Built for the MD Capital AI Developer Take-Home Exercise.*
