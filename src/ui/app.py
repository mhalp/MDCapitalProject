import streamlit as st
import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Backend API URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
LOGO_PATH = "/home/aiuser/.gemini/antigravity/brain/a6948a49-d902-409c-b4b4-6cde70745235/md_capital_vector_logo_1769681768338.png"

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
        color: #e6f1ff;
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
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: rgba(100, 255, 218, 0.5);
    }
    
    /* Result box styling */
    .result-container {
        background: rgba(17, 34, 64, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(100, 255, 218, 0.3);
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #64ffda !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
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
        color: #ccd6f6;
        border: 1px solid rgba(100, 255, 218, 0.3);
        border-radius: 10px;
        font-size: 1rem;
        padding: 15px;
    }
    
    .stTextArea>div>div>textarea:focus {
        border-color: rgba(100, 255, 218, 0.6);
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #020c1b;
    }
    ::-webkit-scrollbar-thumb {
        background: #112240;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #233554;
    }

    /* Sidebar form inputs — lighter text for readability */
    section[data-testid="stSidebar"] .stTextInput>div>div>input,
    section[data-testid="stSidebar"] .stTextArea>div>div>textarea {
        background-color: rgba(20, 40, 70, 0.9);
        color: #e6f1ff !important;
        border: 1px solid rgba(100, 255, 218, 0.12) !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown div,
    section[data-testid="stSidebar"] .stCaption {
        color: #cfeeff !important;
    }
    section[data-testid="stSidebar"] input::placeholder,
    section[data-testid="stSidebar"] textarea::placeholder {
        color: #9fb3c8 !important;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)

# Hide Streamlit default header/footer/menu for a cleaner app surface
st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            /* Fallback: remove extra top padding for main content */
            .css-18e3th9 {padding-top: 0rem;}
        </style>
        """,
        unsafe_allow_html=True,
)

# Sidebar
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    st.sidebar.title("MD Capital")

st.sidebar.markdown("### System Configuration")
api_key = st.sidebar.text_input("API Key (Gemini)", type="password", value=os.environ.get("GOOGLE_API_KEY", ""))
st.sidebar.caption("Enter your Gemini API key. The key is used for LLM requests and kept in session state only.")

st.sidebar.markdown("---")
st.sidebar.markdown("Live Status")
status_placeholder = st.sidebar.empty()

# Helper to check if backend is up
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/summary", timeout=2)
        return response.status_code == 200
    except:
        return False

if not api_key:
    st.sidebar.warning("API key required to activate AI agent.")
    st.info("Please enter your Google API Key in the sidebar to begin.")
    st.stop()

if not check_backend():
    status_placeholder.error("Backend Offline")
    st.error(f"Connection Error: Cannot reach Intelligence Server at {BACKEND_URL}")
    st.info("System Admin: Ensure `python src/api/server.py` is running.")
    st.stop()
else:
    status_placeholder.success("Backend Online")

# Load Data from Backend
@st.cache_data(ttl=600)
def get_data_from_backend():
    try:
        summary = requests.get(f"{BACKEND_URL}/summary").json()
        raw_data = requests.get(f"{BACKEND_URL}/data").json()
        return summary, pd.DataFrame(raw_data)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return None, None

summary, df = get_data_from_backend()

if df is None or df.empty:
    st.warning("No data streams detected from backend.")
    st.stop()


# Main UI
st.title("MD Capital Intelligence")
st.markdown("<p style='color: #8892b0; font-size: 1.05rem;'>Submit a single, focused query for the LLM to analyze your claims data.</p>", unsafe_allow_html=True)

st.markdown("---")

# Initialize result state
if "current_result" not in st.session_state:
    st.session_state.current_result = None

# Query Input Section
st.markdown("### LLM Query (single request)")
user_question = st.text_area(
    "Provide a single, clear instruction for the LLM. Examples:\n- Summarize the top 5 reasons for claim rejections.\n- Which insurer has the fastest average turnaround time and why?\n- Recommend filters to investigate high-urgency claims.",
    placeholder="Compose one focused instruction for the model (avoid conversational multi-turn prompts).",
    height=120,
    label_visibility="collapsed"
)

col1, col2 = st.columns([0.2, 0.8])
with col1:
    submit_button = st.button("Run LLM Query", use_container_width=True)

# Process Query
if submit_button and user_question:
    try:
        with st.spinner("Running LLM analysis..."):
            payload = {"question": user_question, "api_key": api_key}
            response = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()["response"]
                st.session_state.current_result = result
            else:
                st.error(f"System error: {response.text}")
                st.session_state.current_result = None
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        st.session_state.current_result = None

# Display Result
if st.session_state.current_result:
    st.markdown("---")
    st.markdown("### LLM Response")
    st.markdown(f"""
    <div class="result-container" style="font-family: Inter, system-ui, sans-serif; line-height:1.45;">
    {st.session_state.current_result}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Dashboard Tabs
tab1, tab2 = st.tabs(["Analytics", "Data Stream"])

with tab1:
    st.markdown("### Operational Intelligence")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Records", summary["total_records"], delta=None)
    m_col2.metric("Active Insurers", len(summary["insurers"]), delta=None)
    m_col3.metric("Avg Urgency", f"{summary['avg_urgency']:.1f}", delta=None)
    m_col4.metric("Avg Days Pending", f"{summary['avg_days']:.1f}", delta=None)
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    # Set dark theme for plots
    plt.style.use('dark_background')
    
    with col_a:
        st.markdown("##### Claim Status Distribution")
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#0a192f')
        ax.set_facecolor('#0a192f')
        sns.countplot(data=df, x='claim_status', hue='claim_status', palette='viridis', ax=ax, legend=False)
        plt.xticks(rotation=45, color='#8892b0')
        plt.yticks(color='#8892b0')
        ax.spines['bottom'].set_color('#8892b0')
        ax.spines['left'].set_color('#8892b0')
        st.pyplot(fig)
        
    with col_b:
        st.markdown("##### Urgency Variance by Insurer")
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#0a192f')
        ax.set_facecolor('#0a192f')
        sns.boxplot(data=df, x='insurer_name', y='urgency', hue='insurer_name', palette='magma', ax=ax, legend=False)
        plt.xticks(rotation=45, color='#8892b0')
        plt.yticks(color='#8892b0')
        ax.spines['bottom'].set_color('#8892b0')
        ax.spines['left'].set_color('#8892b0')
        st.pyplot(fig)

with tab2:
    st.markdown("### Raw Communication Stream")
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "urgency": st.column_config.ProgressColumn("Urgency", min_value=0, max_value=10, format="%d"),
            "days_since_submission": st.column_config.NumberColumn("Days Pending", format="%d ⏳")
        }
    )

st.markdown("---")
st.caption("MD Capital Intelligence System | Powered by Advanced AI")

