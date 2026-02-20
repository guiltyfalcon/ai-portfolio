import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="RPA AI News Summarizer",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📰 AI-Powered News Summarizer")
st.markdown("### Intelligent RPA & Information Extraction Engine")

# Sidebar
st.sidebar.header("Summarizer Settings")
topic = st.sidebar.selectbox(
    "Select Topic",
    ["AI & Machine Learning", "Robotic Process Automation", "Finance & Fintech", "Cybersecurity", "Custom Query"]
)

if topic == "Custom Query":
    custom_topic = st.sidebar.text_input("Enter Topic", "Space Exploration")
else:
    custom_topic = topic

summary_length = st.sidebar.slider("Summary Length (sentences)", 1, 5, 3)
auto_refresh = st.sidebar.checkbox("Auto-update Content", value=True)

# Main Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"#### Latest News: {custom_topic}")
    
    # Simulated news data (In production, this would use a web scraper/RPA tool)
    news_items = [
        {
            "title": "New Breakthrough in LLM Efficiency",
            "source": "TechCrunch",
            "summary": "Researchers have developed a way to reduce model size by 40% without losing accuracy.",
            "sentiment": "Neutral",
            "date": "2 hours ago"
        },
        {
            "title": "RPA Market Projected to Reach $25B by 2028",
            "source": "Forbes",
            "summary": "The shift towards hyper-automation is driving massive growth in the RPA sector as companies look to automate complex workflows.",
            "sentiment": "Positive",
            "date": "5 hours ago"
        },
        {
            "title": "NVIDIA Unveils Next-Gen AI Accelerators",
            "source": "Ars Technica",
            "summary": "The new Blackwell architecture promises a 10x performance boost for inference tasks in data centers.",
            "sentiment": "Positive",
            "date": "Yesterday"
        }
    ]

    for item in news_items:
        with st.container():
            st.markdown(f"""
            <div class="stCard">
                <span style="color: #666; font-size: 0.8rem;">{item['date']} | {item['source']}</span>
                <h5>{item['title']}</h5>
                <p>{item['summary']}</p>
                <code style="background: #eef2f6; padding: 2px 5px; border-radius: 3px;">{item['sentiment']}</code>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("#### RPA Control Center")
    st.info("System status: ACTIVE")
    
    st.metric("Sources Tracked", "124")
    st.metric("Daily Summaries", "1,452")
    st.metric("Accuracy Rate", "98.2%")
    
    st.subheader("Process Tasks")
    if st.button("Trigger Full Scan"):
        st.write("Scan initiated...")
        st.success("Analysis complete!")

    st.subheader("Export Center")
    st.download_button("Export Daily Report (JSON)", "{}", "daily_report.json")
    st.download_button("Export Excel Summary", "Summary data", "news_summary.csv")

st.divider()
st.markdown("built by guiltyfalcon | AI Portfolio Project 2026")
