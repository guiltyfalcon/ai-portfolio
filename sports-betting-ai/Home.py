"""
Sports Betting AI Pro - Modernized Streamlit App
Main entry point with authentication and dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# Page config MUST be first
st.set_page_config(
    page_title="Sports Betting AI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESPN API Function
def fetch_espn_games(sport="nba"):
    """Fetch live games from ESPN API"""
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/{sport}/scoreboard"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = []
            for event in data.get('events', [])[:4]:  # Get first 4 games
                home_team = event['competitions'][0]['competitors'][0]['team']['displayName']
                away_team = event['competitions'][0]['competitors'][1]['team']['displayName']
                status = event.get('status', {}).get('type', {}).get('state', 'pre')
                
                games.append({
                    'id': event['id'],
                    'sport': sport.upper(),
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_odds': -140,
                    'away_odds': 120,
                    'spread': -3.5,
                    'total': 228.5,
                    'time': event.get('status', {}).get('shortDetail', 'TBD'),
                    'status': 'live' if status == 'in' else 'upcoming'
                })
            return games
    except Exception as e:
        print(f"Error fetching ESPN data: {e}")
    return []

# Yahoo Sports Scraping Fallback
def fetch_yahoo_games(sport="nba"):
    """Fetch games from Yahoo Sports as fallback"""
    try:
        from bs4 import BeautifulSoup
        sport_codes = {"nba": "basketball/nba", "nfl": "football/nfl", "mlb": "baseball/mlb", "nhl": "hockey/nhl"}
        sport_path = sport_codes.get(sport.lower(), "basketball/nba")
        url = f"https://sports.yahoo.com/{sport_path}/scoreboard/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            games = []
            
            # Find game containers
            game_containers = soup.find_all('div', class_=lambda x: x and 'scoreboard' in x.lower() if x else False)
            
            for idx, container in enumerate(game_containers[:4]):
                teams = container.find_all('span', class_=lambda x: x and 'team' in x.lower() if x else False)
                if len(teams) >= 2:
                    home_team = teams[0].text.strip() if teams[0] else f"Team {idx*2+1}"
                    away_team = teams[1].text.strip() if teams[1] else f"Team {idx*2+2}"
                    
                    # Try to find time
                    time_elem = container.find('span', class_=lambda x: x and ('time' in x.lower() or 'status' in x.lower()) if x else False)
                    game_time = time_elem.text.strip() if time_elem else "7:00 PM"
                    
                    games.append({
                        'id': f'yahoo_{idx}',
                        'sport': sport.upper(),
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_odds': -140,
                        'away_odds': 120,
                        'spread': -3.5,
                        'total': 228.5,
                        'time': game_time,
                        'status': 'upcoming'
                    })
            
            if games:
                return games
    except Exception as e:
        print(f"Error fetching Yahoo data: {e}")
    return []

# Combined fetch with fallback
def fetch_games_with_fallback(sport="nba"):
    """Try ESPN first, then Yahoo, then mock data"""
    # Try ESPN API first
    games = fetch_espn_games(sport)
    if games:
        return games, "ESPN API"
    
    # Try Yahoo Sports scraping
    games = fetch_yahoo_games(sport)
    if games:
        return games, "Yahoo Sports"
    
    # Fallback to mock data
    return get_mock_games(), "Sample Data"

# Page config MUST be first
st.set_page_config(
    page_title="Sports Betting AI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'bets' not in st.session_state:
    st.session_state.bets = []
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0

# Modern Dark Theme CSS
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Base styles */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(21, 26, 38, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(145deg, rgba(0, 210, 255, 0.1) 0%, rgba(0, 231, 1, 0.05) 100%);
        border: 1px solid rgba(0, 210, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border-color: rgba(0, 210, 255, 0.4);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #8A8F98;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d2ff 0%, #00a8cc 100%) !important;
        color: #0B0E14 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 210, 255, 0.3) !important;
    }
    
    /* Secondary button */
    .secondary-btn > button {
        background: rgba(30, 37, 50, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(21, 26, 38, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.875rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00d2ff !important;
        box-shadow: 0 0 0 3px rgba(0, 210, 255, 0.1) !important;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-163ttbj {
        background: rgba(15, 18, 30, 0.95) !important;
        backdrop-filter: blur(20px);
    }
    
    /* Sidebar navigation */
    .nav-item {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background: rgba(0, 210, 255, 0.1);
    }
    
    .nav-item.active {
        background: rgba(0, 210, 255, 0.15);
        border-left: 3px solid #00d2ff;
    }
    
    /* Live badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.75rem;
        background: rgba(0, 231, 1, 0.15);
        color: #00e701;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Status badges */
    .badge-win {
        background: rgba(0, 231, 1, 0.15);
        color: #00e701;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-loss {
        background: rgba(255, 77, 77, 0.15);
        color: #ff4d4d;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-pending {
        background: rgba(0, 210, 255, 0.15);
        color: #00d2ff;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Game cards */
    .game-card {
        background: rgba(21, 26, 38, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .game-card:hover {
        border-color: rgba(0, 210, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Odds display */
    .odds-box {
        background: rgba(11, 14, 20, 0.8);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-family: monospace;
        font-weight: 600;
    }
    
    /* AI recommendation */
    .ai-pick {
        background: linear-gradient(145deg, rgba(0, 210, 255, 0.1) 0%, rgba(0, 231, 1, 0.05) 100%);
        border: 1px solid rgba(0, 210, 255, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Confidence bar */
    .confidence-bar {
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #00d2ff 0%, #00e701 100%);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Ticker */
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        white-space: nowrap;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Mock data
@st.cache_data
def get_mock_games():
    return [
        {
            "id": "g1",
            "sport": "NBA",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "home_odds": -140,
            "away_odds": 120,
            "spread": -3.5,
            "total": 228.5,
            "time": "7:30 PM ET",
            "status": "upcoming"
        },
        {
            "id": "g2",
            "sport": "NBA",
            "home_team": "Celtics",
            "away_team": "Nuggets",
            "home_odds": -180,
            "away_odds": 155,
            "spread": -4.5,
            "total": 224.5,
            "time": "8:00 PM ET",
            "status": "upcoming"
        },
        {
            "id": "g3",
            "sport": "NFL",
            "home_team": "Chiefs",
            "away_team": "49ers",
            "home_odds": -165,
            "away_odds": 140,
            "spread": -3,
            "total": 47.5,
            "time": "6:30 PM ET",
            "status": "upcoming"
        },
        {
            "id": "g4",
            "sport": "NHL",
            "home_team": "Maple Leafs",
            "away_team": "Avalanche",
            "home_odds": -130,
            "away_odds": 110,
            "spread": -1.5,
            "total": 6.5,
            "time": "LIVE",
            "status": "live",
            "score": {"home": 2, "away": 1}
        },
    ]

@st.cache_data
def get_mock_predictions():
    return [
        {
            "game": "Lakers vs Warriors",
            "pick": "Lakers +3.5",
            "confidence": 78,
            "ev": 5.2,
            "reasoning": "Lakers have covered in 7 of last 10 home games"
        },
        {
            "game": "Celtics vs Nuggets",
            "pick": "Over 224.5",
            "confidence": 72,
            "ev": 3.8,
            "reasoning": "Both teams rank top 10 in pace"
        },
        {
            "game": "Chiefs vs 49ers",
            "pick": "Chiefs ML",
            "confidence": 68,
            "ev": 2.5,
            "reasoning": "Mahomes undefeated in playoff rematches"
        },
    ]

@st.cache_data
def get_mock_bets():
    return [
        {"id": 1, "event": "Lakers vs Warriors", "selection": "Lakers +3.5", "odds": -110, "stake": 100, "status": "win", "profit": 90.91, "sport": "NBA"},
        {"id": 2, "event": "Celtics vs Nuggets", "selection": "Celtics ML", "odds": -145, "stake": 145, "status": "loss", "profit": -145, "sport": "NBA"},
        {"id": 3, "event": "Chiefs vs 49ers", "selection": "Over 47.5", "odds": -110, "stake": 110, "status": "win", "profit": 100, "sport": "NFL"},
        {"id": 4, "event": "Ravens vs Lions", "selection": "Ravens -3", "odds": -105, "stake": 105, "status": "win", "profit": 100, "sport": "NFL"},
        {"id": 5, "event": "Yankees vs Dodgers", "selection": "Yankees ML", "odds": 135, "stake": 100, "status": "loss", "profit": -100, "sport": "MLB"},
    ]

# Authentication functions
def login_user(email, password):
    """Simple demo authentication"""
    if "@" in email and len(password) >= 5:
        st.session_state.authenticated = True
        st.session_state.user = {"email": email, "username": email.split("@")[0]}
        return True
    return False

def signup_user(username, email, password):
    """Simple demo signup"""
    if len(username) >= 3 and "@" in email and len(password) >= 5:
        st.session_state.authenticated = True
        st.session_state.user = {"email": email, "username": username}
        return True
    return False

def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None

# Login/Signup Page
def show_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="
                width: 80px; 
                height: 80px; 
                margin: 0 auto 1rem;
                background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5rem;
            ">🎯</div>
            <h1 class="gradient-text" style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                Sports Betting AI Pro
            </h1>
            <p style="color: #8A8F98; font-size: 1.1rem;">
                AI-powered predictions & analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Login/Signup
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if login_user(email, password):
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
        
        with tab2:
            with st.form("signup_form"):
                username = st.text_input("Username", placeholder="johndoe")
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif signup_user(username, email, password):
                        st.rerun()
                    else:
                        st.error("Please check your information and try again")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #8A8F98; font-size: 0.875rem;">
            Demo: Use any email with @ and password (5+ chars)
        </div>
        """, unsafe_allow_html=True)

# Dashboard Page
def show_dashboard():
    # Top Navigation Menu - Glass Background
    with st.container():
        st.markdown("""
        <style>
        .glass-nav {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 0.5rem 1rem;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container(border=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("⊕  Bets", use_container_width=True):
                    st.switch_page("pages/Bet_Tracker.py")
            with col2:
                if st.button("◈  Odds", use_container_width=True):
                    st.switch_page("pages/Live_Odds.py")
            with col3:
                if st.button("❖  Props", use_container_width=True):
                    st.switch_page("pages/Player_Props.py")
            with col4:
                if st.button("⛓  Parlay", use_container_width=True):
                    st.switch_page("pages/Parlay_Builder.py")
            with col5:
                if st.button("○  Exit", use_container_width=True, type="secondary"):
                    logout_user()
                    st.rerun()
    
    # Logo and App Name (Below Menu)
    with st.container():
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="
                width: 50px; 
                height: 50px; 
                background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
            ">🎯</div>
            <div>
                <h2 style="margin: 0; color: white; font-size: 1.5rem;">Sports Betting AI</h2>
                <p style="margin: 0; color: #8A8F98; font-size: 0.75rem;">Pro Analytics</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Title row with Sport Selector
    col_title, col_sport = st.columns([3, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: 0.5rem;'>Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Track your performance and AI predictions</p>", unsafe_allow_html=True)
    with col_sport:
        sports = ["🏀 NBA", "🏈 NFL", "⚾ MLB", "🏒 NHL", "🏀 NCAAB", "🏈 NCAAF"]
        selected_sport = st.selectbox("Select Sport", sports, index=0)
        st.session_state.selected_sport = selected_sport.split()[-1]  # Store sport code
    
    # Stats Row - Use user's actual bets from session state
    bets = st.session_state.bets
    wins = len([b for b in bets if b.get("status") == "win"])
    losses = len([b for b in bets if b.get("status") == "loss"])
    pending = len([b for b in bets if b.get("status") == "pending"])
    total_profit = sum(b.get("profit", 0) for b in bets)
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    active_bets = pending
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Win Rate</div>
            <div class="stat-value gradient-text">{win_rate:.1f}%</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">{wins}W - {losses}L</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        profit_color = "#00e701" if total_profit >= 0 else "#ff4d4d"
        profit_sign = "+" if total_profit >= 0 else ""
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Profit</div>
            <div class="stat-value" style="color: {profit_color};">{profit_sign}${total_profit:.2f}</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">+12.5% ROI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Active Bets</div>
            <div class="stat-value" style="color: #F97316;">{active_bets}</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">{len(bets)} Total Bets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calculate current streak
        recent_bets = sorted(bets, key=lambda x: x.get('id', 0), reverse=True)
        streak = 0
        streak_type = None
        for bet in recent_bets:
            if bet.get('status') == 'win':
                if streak_type is None or streak_type == 'win':
                    streak_type = 'win'
                    streak += 1
                else:
                    break
            elif bet.get('status') == 'loss':
                if streak_type is None or streak_type == 'loss':
                    streak_type = 'loss'
                    streak -= 1
                else:
                    break
        
        streak_display = f"+{streak}" if streak > 0 else str(streak)
        streak_color = "#00e701" if streak > 0 else ("#ff4d4d" if streak < 0 else "#8A8F98")
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Current Streak</div>
            <div class="stat-value" style="color: {streak_color};">{streak_display}</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Recent Performance</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='margin-bottom: 1rem;'>Profit Trend</h3>", unsafe_allow_html=True)
        
        # Calculate actual cumulative profit from user's bets
        if bets:
            sorted_bets = sorted(bets, key=lambda x: x.get('id', 0))
            daily_profits = []
            cumulative = 0
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, bet in enumerate(sorted_bets[:7]):
                cumulative += bet.get('profit', 0)
                daily_profits.append(cumulative)
            # Pad with zeros if less than 7 bets
            while len(daily_profits) < 7:
                daily_profits.append(cumulative)
            profit_values = daily_profits[-7:]
        else:
            profit_values = [0, 0, 0, 0, 0, 0, 0]
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Profit chart using actual data
        profit_data = pd.DataFrame({
            'Day': days,
            'Profit': profit_values
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=profit_data['Day'],
            y=profit_data['Profit'],
            fill='tozeroy',
            line=dict(color='#00e701', width=2),
            fillcolor='rgba(0, 231, 1, 0.2)'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(l=40, r=40, t=20, b=40),
            height=250,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3 style='margin-bottom: 1rem;'>Win/Loss Distribution</h3>", unsafe_allow_html=True)
        
        # Use actual bet data with pending
        labels = ['Wins', 'Losses', 'Pending']
        values = [wins, losses, pending]
        colors = ['#00e701', '#ff4d4d', '#00d2ff']
        
        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color='#0B0E14', width=2)),
            textinfo='label+percent',
            textfont=dict(color='white', size=12)
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2),
            margin=dict(l=20, r=20, t=20, b=60),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Predictions
    st.markdown("<h3 style='margin: 2rem 0 1rem;'>🤖 AI Predictions</h3>", unsafe_allow_html=True)
    
    predictions = get_mock_predictions()
    cols = st.columns(len(predictions))
    
    for idx, (col, pred) in enumerate(zip(cols, predictions)):
        with col:
            st.markdown(f"""
            <div class="ai-pick">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600; color: white;">{pred['pick']}</span>
                    <span style="background: rgba(0, 210, 255, 0.2); color: #00d2ff; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem;">BUY</span>
                </div>
                <p style="color: #8A8F98; font-size: 0.875rem; margin-bottom: 0.75rem;">{pred['reasoning']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #8A8F98; font-size: 0.75rem;">🎯 {pred['confidence']}% confidence</span>
                    <span style="color: #00e701; font-size: 0.75rem;">+{pred['ev']}% EV</span>
                </div>
                <div class="confidence-bar" style="margin-top: 0.5rem;">
                    <div class="confidence-fill" style="width: {pred['confidence']}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Live Games
    st.markdown("<h3 style='margin: 2rem 0 1rem;'>🔴 Live & Upcoming Games</h3>", unsafe_allow_html=True)
    
    # Fetch live games with fallback
    games, source = fetch_games_with_fallback("nba")
    if source == "Sample Data":
        st.info("⚠️ Showing sample data - ESPN API and Yahoo Sports temporarily unavailable")
    elif source == "Yahoo Sports":
        st.info("ℹ️ Data from Yahoo Sports (ESPN API unavailable)")
    
    for game in games:
        live_badge = '<span class="live-badge">● LIVE</span>' if game['status'] == 'live' else ''
        score_display = game.get('time', 'TBD')
        if game['status'] == 'live' and 'score' in game:
            score_display = f"{game['score']['home']} - {game['score']['away']}"
        
        card_html = f'''
        <div class="game-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="color: #00d2ff; font-size: 0.875rem; font-weight: 500;">{game['sport']}</span>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    {live_badge}
                    <span style="color: #8A8F98; font-size: 0.875rem;">{score_display}</span>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: white; font-weight: 500;">{game['home_team']}</span>
                <span class="odds-box" style="color: #00d2ff;">{game['home_odds']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: white; font-weight: 500;">{game['away_team']}</span>
                <span class="odds-box" style="color: #00d2ff;">{game['away_odds']}</span>
            </div>
            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between;">
                <span style="color: #8A8F98; font-size: 0.75rem;">Spread: {game['spread']}</span>
                <span style="color: #8A8F98; font-size: 0.75rem;">Total: {game['total']}</span>
            </div>
        </div>
        '''
        st.html(card_html)
    
    # Live Odds Ticker
    st.markdown("---")
    
    # Generate ticker items from games
    ticker_items = []
    for game in games:
        ticker_items.append(f"{game['home_team']} {game['home_odds']} vs {game['away_team']} {game['away_odds']}")
    
    ticker_content = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏀&nbsp;&nbsp;&nbsp;&nbsp;".join(ticker_items)
    
    st.markdown(f"""
    <style>
    .ticker-wrap {{
        width: 100%;
        overflow: hidden;
        background: linear-gradient(90deg, rgba(0,210,255,0.1) 0%, rgba(0,231,1,0.1) 100%);
        padding: 0.75rem 0;
        border-top: 1px solid rgba(255,255,255,0.1);
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .ticker {{
        display: inline-block;
        white-space: nowrap;
        animation: ticker 30s linear infinite;
    }}
    @keyframes ticker {{
        0% {{ transform: translate3d(0, 0, 0); }}
        100% {{ transform: translate3d(-50%, 0, 0); }}
    }}
    .ticker-item {{
        display: inline-block;
        padding: 0 2rem;
        color: white;
        font-size: 0.9rem;
        font-weight: 500;
    }}
    .ticker-odds {{
        color: #00d2ff;
        font-weight: 600;
    }}
    </style>
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">🔴 LIVE ODDS: &nbsp;&nbsp;{ticker_content}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏀&nbsp;&nbsp;&nbsp;&nbsp;{ticker_content}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏀&nbsp;&nbsp;&nbsp;&nbsp;{ticker_content}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏀</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Navigation
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="
                width: 60px; 
                height: 60px; 
                margin: 0 auto 0.75rem;
                background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.75rem;
            ">🎯</div>
            <h3 style="margin: 0; color: white;">Sports Betting AI</h3>
            <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Pro Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User info
        if st.session_state.user:
            st.markdown(f"""
            <div style="background: rgba(0, 210, 255, 0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;">
                <p style="color: white; margin: 0; font-weight: 500;">{st.session_state.user['username']}</p>
                <p style="color: #8A8F98; margin: 0; font-size: 0.75rem;">Pro Member</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()

# Main App
if not st.session_state.authenticated:
    show_auth_page()
else:
    show_sidebar()
    show_dashboard()
