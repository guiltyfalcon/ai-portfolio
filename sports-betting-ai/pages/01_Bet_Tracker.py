# AI Sports Betting App - Bet Tracker

import streamlit as st
import sys
sys.path.insert(0, '/Users/djryan/.openclaw/workspace/user_upload')
from auth import check_session, login_form, logout, is_admin

# Check authentication
session = check_session()
if not session:
    st.set_page_config(page_title="Login - Bet Tracker", page_icon="🔒")
    login_form()
    st.stop()

st.set_page_config(page_title="Bet Tracker", layout="wide")

# Sidebar configuration
st.sidebar.title("Bet Tracker")

# Authentication section
if session:
    st.sidebar.markdown("### 👤 User")
    st.sidebar.write(f"**{session['username']}**")
    if session.get('is_admin'):
        st.sidebar.markdown("`🛡️ ADMIN`")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.markdown("---")

# Navigation
nav = st.sidebar.radio("Navigation", options=["Home", "Live Odds", "Player Props", "Backtesting", "Parlay Builder"])

if nav == "Home":
    st.subheader("Home")
    st.write("Welcome to your AI sports betting dashboard")
elif nav == "Live Odds":
    st.subheader("Live Odds")
    st.write("Live betting markets and odds")
elif nav == "Player Props":
    st.subheader("Player Props")
    st.write("Player-specific betting options")
elif nav == "Backtesting":
    st.subheader("Backtesting")
    st.write("Historical performance analysis")
elif nav == "Parlay Builder":
    st.subheader("Parlay Builder")
    st.write("Create multi-leg parlays")

# Filter controls
st.sidebar.subheader("Filters")

# Team selector
teams = st.sidebar.selectbox("Select Team", options=["All", "Team A", "Team B", "Team C"])

# Probability slider
probability = st.sidebar.slider("Probability Threshold", 0.0, 1.0, 0.5, step=0.05)

# Display results
if nav == "Live Odds":
    st.subheader("Live Odds Results")
    st.write("Displaying odds for selected team and probability threshold")

# Add more features as needed
st.sidebar.subheader("Additional Features")
st.sidebar.button("Refresh Data")
st.sidebar.checkbox("Show Historical Data")

# Footer
st.sidebar.write("© 2026 AI Sports