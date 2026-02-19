"""
Sports Betting AI - For multi-page Streamlit app
This is the main entry file that redirects to the dashboard
"""

import streamlit as st

st.set_page_config(
    page_title="Sports Betting AI 🏆",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<div style="text-align: center;">
    <h1>🏆 Sports Betting AI</h1>
    <p>Machine Learning Powered Value Bet Detection</p>
    <p>Select a page from the sidebar to get started:</p>
    <ul style="list-style: none; font-size: 1.2em;">
        <li>🏠 <b>Home</b> - Dashboard with games and picks</li>
        <li>📊 <b>Live Odds</b> - Real-time odds comparison</li>
        <li>📈 <b>Performance</b> - ROI tracking</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.sidebar.success("Select a page from above")
