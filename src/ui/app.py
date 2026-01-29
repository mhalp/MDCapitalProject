import streamlit as st
import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend API URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Page Config
st.set_page_config(
    page_title="MD Capital | AI Claims Agent",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 12px rgba(0,123,255,0.3);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    h1 {
        color: #1e3d59;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
st.sidebar.title("MD Capital AI")
st.sidebar.markdown("---")
api_key = st.sidebar.text_input("Google API Key", type="password", value=os.environ.get("GOOGLE_API_KEY", ""))

# Main UI
st.title("🏥 MD Capital AI Claims Agent")
st.markdown("#### Intelligent Analysis of Insurer Communications")

if not api_key:
    st.sidebar.warning("⚠️ Please enter your Google API Key to proceed.")
    st.stop()

# Helper to check if backend is up
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/summary", timeout=2)
        return response.status_code == 200
    except:
        return False

if not check_backend():
    st.error(f"🔌 Connection Error: Cannot reach Backend Server at {BACKEND_URL}")
    st.info("💡 **How to fix:** Run `python src/api/server.py` in a separate terminal window.")
    st.stop()

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
    st.warning("No data available from the backend.")
    st.stop()

# Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["💬 AI Agent", "📊 Data Overview", "📋 Raw Data"])

with tab1:
    st.markdown("### 💬 Ask the AI Agent")
    st.info("The agent analyzes all communication records to find patterns and insights.")
    
    # Sample Questions
    st.markdown("##### Quick Queries")
    cols = st.columns(3)
    if cols[0].button("🔍 Top 5 rejection reasons?"):
        st.session_state.query = "What are the top 5 reasons claims are being denied?"
    if cols[1].button("⚖️ Aetna vs UnitedHealthcare?"):
        st.session_state.query = "Compare Aetna vs. UnitedHealthcare on denial reasons."
    if cols[2].button("⏳ Slowest response times?"):
        st.session_state.query = "Which insurer has the slowest response times based on days_since_submission?"

    query = st.text_input("Enter your question:", key="query_input", value=st.session_state.get('query', ''))
    
    if st.button("🚀 Analyze"):
        if query:
            with st.spinner("🧠 Agent is thinking..."):
                try:
                    payload = {"question": query, "api_key": api_key}
                    response = requests.post(f"{BACKEND_URL}/ask", json=payload)
                    if response.status_code == 200:
                        st.markdown("---")
                        st.success("#### 🤖 Agent Response")
                        st.markdown(response.json()["response"])
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a question.")

with tab2:
    st.markdown("### 📊 Operational Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", summary["total_records"])
    col2.metric("Unique Insurers", len(summary["insurers"]))
    col3.metric("Avg Urgency", f"{summary['avg_urgency']:.1f}")
    col4.metric("Avg Days Pending", f"{summary['avg_days']:.1f}")
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("##### Claim Status Distribution")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(data=df, x='claim_status', hue='claim_status', palette='viridis', ax=ax, legend=False)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
    with col_b:
        st.markdown("##### Urgency by Insurer")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df, x='insurer_name', y='urgency', hue='insurer_name', palette='magma', ax=ax, legend=False)
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tab3:
    st.markdown("### 📋 Communication Records")
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("MD Capital AI Developer Take-Home Exercise | Built with ❤️ by Antigravity")
