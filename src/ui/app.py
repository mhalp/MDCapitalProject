import streamlit as st
import pandas as pd
import os
import requests
import seaborn as sns
import logging
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Configure logging for the UI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MDCCapital.UI")

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
# Assets are relative to the project root
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

# Page Config
st.set_page_config(
    page_title="MD Capital | AI Claims Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for High-Tech Premium Look
st.markdown("""
<style>
/* Main background and text */
.stApp {
    background: radial-gradient(circle at top right, #0a192f, #020c1b);
    color: #ffffff; /* Brighter white for main text */
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: rgba(10, 25, 47, 0.95);
    border-right: 1px solid rgba(100, 255, 218, 0.1);
}

/* Glassmorphism for cards and metrics */
div[data-testid="stMetric"] {
    background: rgba(17, 34, 64, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100, 255, 218, 0.2);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: transform 0.3s ease;
}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    color: #64ffda !important; /* Brighter teal for labels */
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important; /* Pure white for values */
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    border-color: rgba(100, 255, 218, 0.5);
}

/* Result box styling - maintained for legacy or custom containers */
.result-container {
    background: rgba(17, 34, 64, 0.5);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100, 255, 218, 0.3);
    border-radius: 15px;
    padding: 30px;
    margin-top: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    color: #ffffff !important;
}

/* Chat message styling for agent responses */
section[data-testid="stChatMessageContainer"] {
    background: transparent !important;
}

div[data-testid="stChatMessage"] {
    background: rgba(22, 45, 80, 0.6) !important; /* Slightly lighter background */
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100, 255, 218, 0.3);
    border-radius: 15px;
    margin-bottom: 20px;
    padding: 15px;
}

div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] li {
    color: #ffffff !important; /* Pure white for response text */
    font-size: 1.05rem;
}

/* Headers */
h1, h2, h3 {
    color: #64ffda !important;
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
}

h4, h5, h6 {
    color: #ffffff !important; /* Bright white for subheaders */
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(45deg, #64ffda, #48d1cc);
    color: #0a192f;
    font-weight: 700;
    border: none;
    box-shadow: 0 4px 15px rgba(100, 255, 218, 0.2);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 20px rgba(100, 255, 218, 0.4);
    color: #0a192f;
}

/* Input fields */
.stTextArea>div>div>textarea {
    background-color: rgba(17, 34, 64, 0.8);
    color: #e6f1ff; /* Brighter off-white */
    border: 1px solid rgba(100, 255, 218, 0.3);
    border-radius: 10px;
    font-size: 1rem;
    padding: 15px;
}

.stTextArea>div>div>textarea:focus {
    border-color: rgba(100, 255, 218, 0.6);
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
}

/* Sidebar form inputs */
section[data-testid="stSidebar"] .stTextInput>div>div>input,
section[data-testid="stSidebar"] .stTextArea>div>div>textarea {
    background-color: rgba(20, 40, 70, 0.9);
    color: #ffffff !important;
    border: 1px solid rgba(100, 255, 218, 0.3) !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown div,
section[data-testid="stSidebar"] .stCaption {
    color: #ffffff !important; /* Pure white for sidebar labels */
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: #020c1b;
}
::-webkit-scrollbar-thumb {
    background: #112240;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Hide Streamlit default UI elements
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar initialization
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    st.sidebar.title("MD Capital")

st.sidebar.markdown("### System Configuration")
api_key = st.sidebar.text_input("API Key (Gemini)", type="password", value=os.environ.get("GOOGLE_API_KEY", ""))
st.sidebar.caption("Provide your Gemini API key to activate AI agent features.")

st.sidebar.markdown("---")
st.sidebar.markdown("Network Status")
status_placeholder = st.sidebar.empty()

def check_backend_health():
    """Verify backend connectivity."""
    try:
        response = requests.get(f"{BACKEND_URL}/summary", timeout=3)
        return response.status_code == 200
    except Exception:
        return False

# App Guardrails
if not api_key:
    st.sidebar.warning("API key required.")
    st.info("👋 Welcome! Please enter your Google Gemini API Key in the sidebar to activate the Intelligence Engine.")
    st.stop()

if not check_backend_health():
    status_placeholder.error("Backend Offline")
    st.error(f"Connectivity Issue: Remote Intelligence Server at {BACKEND_URL} is currently unreachable.")
    st.info("Troubleshooting: Ensure the backend process is active (`python -m src.api.server`).")
    st.stop()
else:
    status_placeholder.success("Backend Online")

# Data Synchronization
@st.cache_data(ttl=300)
def fetch_intelligence_data():
    """Fetch analytics and raw data from the backend."""
    try:
        summary_resp = requests.get(f"{BACKEND_URL}/summary")
        data_resp = requests.get(f"{BACKEND_URL}/data")
        return summary_resp.json(), pd.DataFrame(data_resp.json())
    except Exception as e:
        logger.error(f"Synchronization failed: {e}")
        return None, None

summary, df = fetch_intelligence_data()

if df is None or df.empty:
    st.warning("Intelligence streams are currently empty.")
    st.stop()

# Main Application Interface
st.title("MD Capital Intelligence")
st.markdown("<p style='color: #8892b0; font-size: 1.1rem;'>Strategic claims analysis powered by Gemini 2.0.</p>", unsafe_allow_html=True)
st.markdown("---")

# Session State for persistency and UI locking
if "current_ai_response" not in st.session_state:
    st.session_state.current_ai_response = None
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Query Interface
st.markdown("### Model Instruction")
user_query = st.text_area(
    "Instruction",
    placeholder="Ask anything about the claims data (e.g., 'Identify patterns in delayed approvals')",
    height=100,
    label_visibility="collapsed",
    disabled=st.session_state.is_processing
)

# Button with processing lock
if st.button("Execute Intelligence Query", use_container_width=True, disabled=st.session_state.is_processing) and user_query:
    st.session_state.is_processing = True
    st.rerun()

# Processing block triggered by the click
if st.session_state.is_processing:
    try:
        with st.spinner("Analyzing data streams..."):
            payload = {"question": user_query, "api_key": api_key}
            response = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=90)
            
            if response.status_code == 200:
                st.session_state.current_ai_response = response.json()["response"]
            else:
                st.error(f"Analysis failed: {response.text}")
    except Exception as e:
        st.error(f"Communication error: {str(e)}")
    finally:
        st.session_state.is_processing = False
        st.rerun()

# Results Display
if st.session_state.current_ai_response:
    st.markdown("---")
    st.markdown("### 🤖 Strategic Insight")
    
    # Using st.chat_message as it natively and reliably renders Markdown
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown(st.session_state.current_ai_response)

st.markdown("---")

# Data Visualization Section
tab_viz, tab_raw = st.tabs(["📊 Analytics Dashboard", "📋 Raw Data Stream"])

with tab_viz:
    st.markdown("### Operational Metrics")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Communications", summary["total_records"])
    col_m2.metric("Insurers Tracked", len(summary["insurers"]))
    col_m3.metric("Avg Urgency Score", f"{summary['avg_urgency']:.1f}")
    col_m4.metric("Avg Latency (Days)", f"{summary['avg_days']:.1f}")
    
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    # Global visual styling
    plt.style.use('dark_background')
    
    with col_left:
        st.markdown("##### Distribution of Claim States")
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        fig1.patch.set_facecolor('#0a192f')
        ax1.set_facecolor('#0a192f')
        sns.countplot(data=df, x='claim_status', palette='viridis', ax=ax1)
        plt.xticks(rotation=45, color='#ffffff') # Pure white
        plt.yticks(color='#ffffff') # Pure white
        ax1.xaxis.label.set_color('#ffffff')
        ax1.yaxis.label.set_color('#ffffff')
        st.pyplot(fig1)
        
    with col_right:
        st.markdown("##### Urgency Distribution by Provider")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        fig2.patch.set_facecolor('#0a192f')
        ax2.set_facecolor('#0a192f')
        sns.boxplot(data=df, x='insurer_name', y='urgency', palette='magma', ax=ax2)
        plt.xticks(rotation=45, color='#ffffff') # Pure white
        plt.yticks(color='#ffffff') # Pure white
        ax2.xaxis.label.set_color('#ffffff')
        ax2.yaxis.label.set_color('#ffffff')
        st.pyplot(fig2)

with tab_raw:
    st.markdown("### Communication Logs")
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "urgency": st.column_config.ProgressColumn("Urgency Level", min_value=0, max_value=10),
            "days_since_submission": st.column_config.NumberColumn("Days Elapsed", format="%d ⏳")
        }
    )

st.markdown("---")
st.caption("MD Capital | Proprietary Intelligence System")

