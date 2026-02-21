import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import re

# Page config
st.set_page_config(
    page_title="Sports Betting AI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Dark Theme CSS matching React app
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Inter', system-ui, sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0B0E14 0%, #151A26 50%, #0B0E14 100%);
}

/* Main header with breathing glow */
.main-header {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #00D2FF 0%, #3A7BD5 50%, #00D2FF 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 3s ease infinite, breathe-glow 2s ease-in-out infinite;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes breathe-glow {
    0%, 100% { 
        text-shadow: 0 0 20px rgba(0,210,255,0.4), 0 0 40px rgba(0,210,255,0.2);
        filter: brightness(1);
    }
    50% { 
        text-shadow: 0 0 40px rgba(0,210,255,0.8), 0 0 80px rgba(0,210,255,0.4);
        filter: brightness(1.2);
    }
}

/* Sub header */
.sub-header {
    text-align: center;
    color: #8A8F98;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Glass card */
.glass-card {
    background: rgba(21, 26, 38, 0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 1rem;
    padding: 2rem;
}

/* Game cards with breathing glow */
.game-card {
    border: 2px solid rgba(0, 210, 255, 0.6);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0 20px 0;
    background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
    box-shadow: 
        0 4px 15px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 210, 255, 0.3),
        inset 0 0 20px rgba(0, 210, 255, 0.1);
    color: white;
    font-family: 'Inter', sans-serif;
    animation: card-breathe 2s ease-in-out infinite;
}

@keyframes card-breathe {
    0%, 100% { 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 210, 255, 0.3), inset 0 0 20px rgba(0, 210, 255, 0.1);
        border-color: rgba(0, 210, 255, 0.6);
    }
    50% { 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 210, 255, 0.6), inset 0 0 30px rgba(0, 210, 255, 0.2);
        border-color: rgba(0, 210, 255, 0.9);
    }
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Custom button styling */
.stButton > button {
    background: linear-gradient(135deg, #00D2FF 0%, #00E701 100%) !important;
    color: #0B0E14 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 0.75rem !important;
    padding: 0.875rem 1.5rem !important;
    transition: all 0.3s !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 20px rgba(0, 210, 255, 0.3) !important;
}

/* Input styling */
.stTextInput > div > div > input {
    background: #0B0E14 !important;
    border: 1px solid #2A3142 !important;
    border-radius: 0.75rem !important;
    color: white !important;
    padding: 0.875rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #00D2FF !important;
    box-shadow: 0 0 0 3px rgba(0, 210, 255, 0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'auth_session' not in st.session_state:
    st.session_state.auth_session = None
if 'auth_tab' not in st.session_state:
    st.session_state.auth_tab = "Login"

# Authentication functions
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(username, is_admin=False):
    import time
    session = {
        'username': username,
        'is_admin': is_admin,
        'created_at': time.time(),
        'expires_at': time.time() + (24 * 60 * 60)
    }
    st.session_state['auth_session'] = session
    return session

def check_session():
    import time
    if 'auth_session' not in st.session_state or st.session_state['auth_session'] is None:
        return None
    session = st.session_state['auth_session']
    if time.time() > session.get('expires_at', 0):
        st.session_state['auth_session'] = None
        return None
    return session

def logout():
    st.session_state['auth_session'] = None
    st.rerun()

# Check authentication
session = check_session()

if not session:
    # Show login page
    st.markdown('<h1 class="main-header">Sports Betting AI Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered predictions & analytics</p>', unsafe_allow_html=True)
    
    # Tab selection
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True, 
                    type="primary" if st.session_state.auth_tab == "Login" else "secondary"):
            st.session_state.auth_tab = "Login"
            st.rerun()
    with col2:
        if st.button("Sign Up", use_container_width=True,
                    type="primary" if st.session_state.auth_tab == "Signup" else "secondary"):
            st.session_state.auth_tab = "Signup"
            st.rerun()
    
    # Form
    with st.form("auth_form"):
        if st.session_state.auth_tab == "Signup":
            username = st.text_input("Username", placeholder="Choose a username")
        
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submit = st.form_submit_button(
            "Sign In" if st.session_state.auth_tab == "Login" else "Create Account",
            use_container_width=True
        )
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            elif st.session_state.auth_tab == "Signup":
                if len(password) < 5:
                    st.error("Password must be at least 5 characters")
                else:
                    st.success("✅ Account created! Please sign in.")
                    st.session_state.auth_tab = "Login"
                    st.rerun()
            else:
                # Demo login - accept any email/password
                session = create_session(email.split('@')[0], is_admin=False)
                st.success(f"✅ Welcome back!")
                st.rerun()
    
    st.stop()

# Main app content (after login)
# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, #00D2FF 0%, #00E701 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
        ">
            <span style="font-size: 24px;">🎯</span>
        </div>
        <h3 style="margin: 0; color: white; font-size: 1rem;">Sports Betting AI</h3>
        <p style="margin: 0; color: #8A8F98; font-size: 0.75rem;">Pro</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    
    pages = {
        "dashboard": "🏠 Dashboard",
        "predictions": "📊 Predictions", 
        "bet_tracker": "💰 Bet Tracker",
        "live_odds": "📈 Live Odds",
        "player_props": "👤 Player Props",
        "parlay_builder": "🔗 Parlay Builder"
    }
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    for page_id, page_label in pages.items():
        if st.button(page_label, use_container_width=True, 
                    type="primary" if st.session_state.current_page == page_id else "secondary"):
            st.session_state.current_page = page_id
            st.rerun()
    
    st.markdown("---")
    
    # User info
    session = check_session()
    if session:
        st.markdown(f"**👤 {session['username']}**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

# Main content area
st.markdown(f"""
<style>
.main-content {{
    background: linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
    border-radius: 1rem;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
}}
</style>
""", unsafe_allow_html=True)

# Render current page
page = st.session_state.current_page

if page == "dashboard":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your betting dashboard overview</p>', unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, rgba(0,210,255,0.1) 0%, rgba(0,210,255,0.05) 100%);
            border: 1px solid rgba(0,210,255,0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; font-weight: 700; color: #00D2FF;">+12.5%</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">ROI This Month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, rgba(0,231,1,0.1) 0%, rgba(0,231,1,0.05) 100%);
            border: 1px solid rgba(0,231,1,0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; font-weight: 700; color: #00E701;">68%</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, rgba(139,92,246,0.1) 0%, rgba(139,92,246,0.05) 100%);
            border: 1px solid rgba(139,92,246,0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; font-weight: 700; color: #8B5CF6;">24</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Active Bets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, rgba(249,115,22,0.1) 0%, rgba(249,115,22,0.05) 100%);
            border: 1px solid rgba(249,115,22,0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; font-weight: 700; color: #F97316;">$1,250</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Total Profit</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📊 Recent Predictions")
        st.info("Select 'Predictions' from the sidebar to see today's games")
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        if st.button("➕ Add New Bet", use_container_width=True):
            st.session_state.current_page = "bet_tracker"
            st.rerun()
        if st.button("📈 View Live Odds", use_container_width=True):
            st.session_state.current_page = "live_odds"
            st.rerun()

elif page == "predictions":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Predictions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered game predictions and analysis</p>', unsafe_allow_html=True)
    
    # Sport selector
    sport = st.selectbox("Select Sport", ["NBA", "NFL", "MLB", "NHL"], key="pred_sport")
    
    st.info("🔄 Loading predictions... This may take a moment.")
    
    # Placeholder for predictions
    st.markdown("### Today's Games")
    for i in range(3):
        with st.container():
            st.markdown(f"""
            <div class="game-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; font-size: 1.1rem;">Team {i*2+1}</div>
                        <div style="color: #8A8F98; font-size: 0.8rem;">Home</div>
                    </div>
                    <div style="color: #00D2FF; font-weight: 700;">VS</div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600; font-size: 1.1rem;">Team {i*2+2}</div>
                        <div style="color: #8A8F98; font-size: 0.8rem;">Away</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif page == "bet_tracker":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Bet Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Track your bets and analyze performance</p>', unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bets", "0", "+0")
    with col2:
        st.metric("Win Rate", "0%", "+0%")
    with col3:
        st.metric("Profit", "$0", "$0")
    with col4:
        st.metric("ROI", "0%", "+0%")
    
    st.markdown("---")
    
    # Add bet form
    with st.expander("➕ Add New Bet"):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
            st.text_input("Your Pick")
        with col2:
            st.number_input("Odds", value=-110)
            st.number_input("Stake ($)", value=10.0)
        st.button("Add Bet", use_container_width=True)

elif page == "live_odds":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Live Odds</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time odds from multiple bookmakers</p>', unsafe_allow_html=True)
    
    st.info("📊 Live odds data will appear here")
    
    # Sample odds table
    sample_data = {
        'Game': ['Lakers vs Warriors', 'Celtics vs Heat', 'Nets vs Bucks'],
        'Home ML': ['-150', '-200', '+120'],
        'Away ML': ['+130', '+170', '-140'],
        'Spread': ['LAL -3.5', 'BOS -5.5', 'BKN +3.5'],
        'Total': ['225.5', '218.5', '230.5']
    }
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True, hide_index=True)

elif page == "player_props":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Player Props</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Player-specific betting markets</p>', unsafe_allow_html=True)
    
    st.info("👤 Player prop data will appear here")

elif page == "parlay_builder":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Parlay Builder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Build and analyze multi-leg parlays</p>', unsafe_allow_html=True)
    
    st.info("🔗 Parlay builder will appear here")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #5A6070; font-size: 0.75rem; padding: 1rem;">
    <b>18+ Only</b> • Please Gamble Responsibly
</div>
""", unsafe_allow_html=True)
