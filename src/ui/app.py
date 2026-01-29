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
    initial_sidebar_state="expanded"
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
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(17, 34, 64, 0.4);
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(100, 255, 218, 0.05);
    }
    
    /* Chat message text - ensure visibility */
    .stChatMessage p, .stChatMessage div {
        color: #ccd6f6 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #64ffda !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(17, 34, 64, 0.5);
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #8892b0;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(100, 255, 218, 0.1);
        color: #64ffda !important;
        border-bottom: 2px solid #64ffda !important;
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
    .stTextInput>div>div>input {
        background-color: rgba(17, 34, 64, 0.8);
        color: #ccd6f6;
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 10px;
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
    </style>
    """, unsafe_allow_html=True)

# Sidebar
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    st.sidebar.title("⚡ MD Capital")

st.sidebar.markdown("### 🛠️ System Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GOOGLE_API_KEY", ""))

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Live Status")
status_placeholder = st.sidebar.empty()

# Main UI
st.title("⚡ MD Capital AI Intelligence")
st.markdown("<p style='color: #8892b0; font-size: 1.2rem;'>Advanced Claims Analysis & Insurer Communications Intelligence</p>", unsafe_allow_html=True)

if not api_key:
    st.sidebar.warning("🔑 API Key required to activate AI Agent.")
    st.info("Please enter your Google API Key in the sidebar to begin.")
    st.stop()

# Helper to check if backend is up
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/summary", timeout=2)
        return response.status_code == 200
    except:
        return False

if not check_backend():
    status_placeholder.error("🔴 Backend Offline")
    st.error(f"🔌 Connection Error: Cannot reach Intelligence Server at {BACKEND_URL}")
    st.info("💡 **System Admin:** Ensure `python src/api/server.py` is running.")
    st.stop()
else:
    status_placeholder.success("🟢 Backend Online")

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
    st.warning("📡 No data streams detected from backend.")
    st.stop()

# Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["💬 AI Agent", "📊 Analytics", "📋 Data Stream"])

with tab1:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "System initialized. I am ready to analyze your claims data. How can I assist you today?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about rejection patterns, insurer performance, or specific claims..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 *Analyzing data streams...*")
            
            try:
                payload = {"question": prompt, "api_key": api_key}
                response = requests.post(f"{BACKEND_URL}/ask", json=payload)
                
                if response.status_code == 200:
                    full_response = response.json()["response"]
                    # Simulate typing effect
                    displayed_text = ""
                    for char in full_response:
                        displayed_text += char
                        message_placeholder.markdown(displayed_text + "▌")
                        time.sleep(0.005)
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    error_msg = f"⚠️ System Error: {response.text}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"❌ Connection Failed: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

with tab2:
    st.markdown("### 📊 Operational Intelligence")
    
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
        st.markdown("##### 📈 Claim Status Distribution")
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
        st.markdown("##### 📉 Urgency Variance by Insurer")
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#0a192f')
        ax.set_facecolor('#0a192f')
        sns.boxplot(data=df, x='insurer_name', y='urgency', hue='insurer_name', palette='magma', ax=ax, legend=False)
        plt.xticks(rotation=45, color='#8892b0')
        plt.yticks(color='#8892b0')
        ax.spines['bottom'].set_color('#8892b0')
        ax.spines['left'].set_color('#8892b0')
        st.pyplot(fig)

with tab3:
    st.markdown("### 📋 Raw Communication Stream")
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "urgency": st.column_config.ProgressColumn("Urgency", min_value=0, max_value=10, format="%d"),
            "days_since_submission": st.column_config.NumberColumn("Days Pending", format="%d ⏳")
        }
    )

st.markdown("---")
st.caption("⚡ MD Capital Intelligence System | Powered by Advanced AI")

