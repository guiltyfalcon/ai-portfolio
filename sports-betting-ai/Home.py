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
        # Map sport codes to ESPN API paths
        sport_paths = {
            "nba": "basketball/nba",
            "nfl": "football/nfl",
            "mlb": "baseball/mlb",
            "nhl": "hockey/nhl",
            "ncaab": "basketball/mens-college-basketball",
            "ncaaf": "football/college-football"
        }
        sport_path = sport_paths.get(sport.lower(), "basketball/nba")
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/scoreboard"
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

def get_available_sports():
    """Check ESPN API for which sports have active games today"""
    available = []
    sport_configs = [
        ("nba", "🏀 NBA", "basketball/nba"),
        ("nfl", "🏈 NFL", "football/nfl"),
        ("mlb", "⚾ MLB", "baseball/mlb"),
        ("nhl", "🏒 NHL", "hockey/nhl"),
        ("ncaab", "🏀 NCAAB", "basketball/mens-college-basketball"),
        ("ncaaf", "🏈 NCAAF", "football/college-football")
    ]
    
    for sport_code, display_name, api_path in sport_configs:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/{api_path}/scoreboard"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                # Only add sport if it has games today or upcoming
                if len(events) > 0:
                    available.append((sport_code, display_name))
        except Exception:
            pass
    
    # Fallback: if no sports available, return NBA at minimum
    if not available:
        return [("nba", "🏀 NBA")]
    
    return available

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
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Stats cards - Glass */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(0, 210, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 210, 255, 0.1);
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
    
    /* Buttons - Glass */
    .stButton > button {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        color: white !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(0, 210, 255, 0.15) !important;
        border-color: rgba(0, 210, 255, 0.4) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 210, 255, 0.15) !important;
    }
    
    /* Secondary button - Glass */
    .secondary-btn > button {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
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
    
    /* Game cards - Glass */
    .game-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .game-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(0, 210, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 210, 255, 0.1);
    }
    
    /* Odds display */
    .odds-box {
        background: rgba(11, 14, 20, 0.8);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-family: monospace;
        font-weight: 600;
    }
    
    /* AI recommendation - Glass */
    .ai-pick {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
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
    .ticker-container {
        width: 100%;
        overflow: hidden;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        padding: 0.5rem 0;
        -webkit-overflow-scrolling: touch;
    }
    .ticker-track {
        display: flex;
        width: max-content;
        animation: ticker-scroll 30s linear infinite;
        -webkit-animation: ticker-scroll 30s linear infinite;
        will-change: transform;
    }
    .ticker-container:hover .ticker-track,
    .ticker-container:active .ticker-track {
        animation-play-state: paused;
        -webkit-animation-play-state: paused;
    }
    @keyframes ticker-scroll {
        0% { transform: translateX(0); -webkit-transform: translateX(0); }
        100% { transform: translateX(-50%); -webkit-transform: translateX(-50%); }
    }
    @-webkit-keyframes ticker-scroll {
        0% { -webkit-transform: translateX(0); transform: translateX(0); }
        100% { -webkit-transform: translateX(-50%); transform: translateX(-50%); }
    }
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        white-space: nowrap;
        flex-shrink: 0;
    }
    
    /* Mobile optimization */
    @media (max-width: 768px) {
        .ticker-track {
            animation-duration: 20s;
            -webkit-animation-duration: 20s;
        }
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
def get_mock_games(sport="NBA"):
    mock_games = {
        "NBA": [
            {"id": "g1", "sport": "NBA", "home_team": "Lakers", "away_team": "Warriors", "home_odds": -140, "away_odds": 120, "spread": -3.5, "total": 228.5, "time": "7:30 PM ET", "status": "upcoming"},
            {"id": "g2", "sport": "NBA", "home_team": "Celtics", "away_team": "Heat", "home_odds": -180, "away_odds": 155, "spread": -5.5, "total": 218.5, "time": "8:00 PM ET", "status": "upcoming"},
            {"id": "g3", "sport": "NBA", "home_team": "Nuggets", "away_team": "Suns", "home_odds": -130, "away_odds": 110, "spread": -2.5, "total": 232.5, "time": "9:00 PM ET", "status": "live"},
            {"id": "g4", "sport": "NBA", "home_team": "Bucks", "away_team": "76ers", "home_odds": -150, "away_odds": 130, "spread": -4.0, "total": 225.5, "time": "7:00 PM ET", "status": "upcoming"},
        ],
        "NFL": [
            {"id": "n1", "sport": "NFL", "home_team": "Chiefs", "away_team": "Bills", "home_odds": -175, "away_odds": 150, "spread": -3.5, "total": 48.5, "time": "1:00 PM ET", "status": "upcoming"},
            {"id": "n2", "sport": "NFL", "home_team": "Eagles", "away_team": "Cowboys", "home_odds": -140, "away_odds": 120, "spread": -3.0, "total": 51.5, "time": "4:25 PM ET", "status": "upcoming"},
            {"id": "n3", "sport": "NFL", "home_team": "Ravens", "away_team": "Steelers", "home_odds": -200, "away_odds": 170, "spread": -4.5, "total": 44.5, "time": "8:20 PM ET", "status": "upcoming"},
            {"id": "n4", "sport": "NFL", "home_team": "49ers", "away_team": "Packers", "home_odds": -130, "away_odds": 110, "spread": -2.5, "total": 47.5, "time": "4:05 PM ET", "status": "live"},
        ],
        "MLB": [
            {"id": "m1", "sport": "MLB", "home_team": "Yankees", "away_team": "Red Sox", "home_odds": -150, "away_odds": 130, "spread": -1.5, "total": 8.5, "time": "7:05 PM ET", "status": "upcoming"},
            {"id": "m2", "sport": "MLB", "home_team": "Dodgers", "away_team": "Giants", "home_odds": -180, "away_odds": 155, "spread": -1.5, "total": 7.5, "time": "10:10 PM ET", "status": "upcoming"},
            {"id": "m3", "sport": "MLB", "home_team": "Astros", "away_team": "Rangers", "home_odds": -140, "away_odds": 120, "spread": -1.5, "total": 9.0, "time": "8:10 PM ET", "status": "live"},
            {"id": "m4", "sport": "MLB", "home_team": "Braves", "away_team": "Mets", "home_odds": -160, "away_odds": 140, "spread": -1.5, "total": 8.0, "time": "7:20 PM ET", "status": "upcoming"},
        ],
        "NHL": [
            {"id": "h1", "sport": "NHL", "home_team": "Lightning", "away_team": "Maple Leafs", "home_odds": -140, "away_odds": 120, "spread": -1.5, "total": 6.5, "time": "7:00 PM ET", "status": "upcoming"},
            {"id": "h2", "sport": "NHL", "home_team": "Avalanche", "away_team": "Blues", "home_odds": -170, "away_odds": 145, "spread": -1.5, "total": 6.0, "time": "9:00 PM ET", "status": "upcoming"},
            {"id": "h3", "sport": "NHL", "home_team": "Bruins", "away_team": "Canadiens", "home_odds": -200, "away_odds": 170, "spread": -1.5, "total": 5.5, "time": "7:00 PM ET", "status": "live"},
            {"id": "h4", "sport": "NHL", "home_team": "Rangers", "away_team": "Islanders", "home_odds": -130, "away_odds": 110, "spread": -1.5, "total": 6.0, "time": "7:00 PM ET", "status": "upcoming"},
        ],
        "NCAAB": [
            {"id": "c1", "sport": "NCAAB", "home_team": "Duke", "away_team": "UNC", "home_odds": -160, "away_odds": 140, "spread": -4.0, "total": 152.5, "time": "7:00 PM ET", "status": "upcoming"},
            {"id": "c2", "sport": "NCAAB", "home_team": "Kansas", "away_team": "Texas", "home_odds": -140, "away_odds": 120, "spread": -3.0, "total": 148.5, "time": "8:00 PM ET", "status": "upcoming"},
            {"id": "c3", "sport": "NCAAB", "home_team": "Kentucky", "away_team": "Florida", "home_odds": -180, "away_odds": 155, "spread": -5.0, "total": 155.5, "time": "9:00 PM ET", "status": "live"},
            {"id": "c4", "sport": "NCAAB", "home_team": "Purdue", "away_team": "Michigan State", "home_odds": -150, "away_odds": 130, "spread": -3.5, "total": 141.5, "time": "6:30 PM ET", "status": "upcoming"},
        ],
        "NCAAF": [
            {"id": "f1", "sport": "NCAAF", "home_team": "Alabama", "away_team": "Georgia", "home_odds": -150, "away_odds": 130, "spread": -3.5, "total": 54.5, "time": "3:30 PM ET", "status": "upcoming"},
            {"id": "f2", "sport": "NCAAF", "home_team": "Ohio State", "away_team": "Michigan", "home_odds": -180, "away_odds": 155, "spread": -4.5, "total": 48.5, "time": "12:00 PM ET", "status": "upcoming"},
            {"id": "f3", "sport": "NCAAF", "home_team": "Texas", "away_team": "Oklahoma", "home_odds": -140, "away_odds": 120, "spread": -3.0, "total": 61.5, "time": "7:00 PM ET", "status": "live"},
            {"id": "f4", "sport": "NCAAF", "home_team": "USC", "away_team": "Notre Dame", "home_odds": -130, "away_odds": 110, "spread": -2.5, "total": 58.5, "time": "7:30 PM ET", "status": "upcoming"},
        ],
    }
    return mock_games.get(sport.upper(), mock_games["NBA"])

# Old mock games - will be replaced
@st.cache_data
def get_mock_games_legacy():
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
def get_ai_predictions(games):
    """Generate AI predictions based on game odds and matchups"""
    if not games:
        return []
    
    predictions = []
    
    # Team stats database (simplified)
    team_stats = {
        "Lakers": {"home_win_pct": 0.65, "pace": 99.2, "recent_form": "WWLWW"},
        "Warriors": {"home_win_pct": 0.52, "pace": 102.5, "recent_form": "LWWLW"},
        "Celtics": {"home_win_pct": 0.78, "pace": 98.5, "recent_form": "WWWWW"},
        "Heat": {"home_win_pct": 0.58, "pace": 96.8, "recent_form": "LLWLW"},
        "Nuggets": {"home_win_pct": 0.72, "pace": 97.5, "recent_form": "WWWLL"},
        "Suns": {"home_win_pct": 0.60, "pace": 100.2, "recent_form": "LWLWW"},
        "Bucks": {"home_win_pct": 0.68, "pace": 101.5, "recent_form": "WWLWL"},
        "76ers": {"home_win_pct": 0.55, "pace": 98.0, "recent_form": "WLLWW"},
        "Chiefs": {"home_win_pct": 0.85, "pace": 68, "recent_form": "WWWWW"},
        "Bills": {"home_win_pct": 0.72, "pace": 72, "recent_form": "LWWLW"},
        "Eagles": {"home_win_pct": 0.75, "pace": 69, "recent_form": "WWLWW"},
        "Cowboys": {"home_win_pct": 0.68, "pace": 70, "recent_form": "WLWLW"},
        "Ravens": {"home_win_pct": 0.80, "pace": 71, "recent_form": "WWWWW"},
        "Steelers": {"home_win_pct": 0.60, "pace": 65, "recent_form": "LLLWL"},
        "49ers": {"home_win_pct": 0.70, "pace": 67, "recent_form": "LWWLW"},
        "Packers": {"home_win_pct": 0.65, "pace": 70, "recent_form": "WLWWL"},
    }
    
    for game in games[:3]:  # Generate predictions for first 3 games
        home_team = game['home_team']
        away_team = game['away_team']
        home_odds = game['home_odds']
        away_odds = game['away_odds']
        total = game['total']
        sport = game['sport']
        
        # Calculate implied probabilities
        def odds_to_prob(odds):
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        home_prob = odds_to_prob(home_odds)
        away_prob = odds_to_prob(away_odds)
        
        # Get team stats
        home_stats = team_stats.get(home_team, {"home_win_pct": 0.55, "recent_form": "WLWLW"})
        away_stats = team_stats.get(away_team, {"home_win_pct": 0.50, "recent_form": "LWLWL"})
        
        # Calculate confidence based on odds disparity and form
        form_factor = home_stats['recent_form'].count('W') / 5
        confidence = int((home_prob * 100) + (form_factor * 20) - 10)
        confidence = max(50, min(95, confidence))  # Clamp between 50-95
        
        # Determine EV (Expected Value)
        prob_edge = abs(home_prob - 0.5)
        ev = round(prob_edge * 10, 1)
        
        # Generate recommendation based on analysis
        picks = []
        
        # Moneyline pick
        if home_odds < -150:
            picks.append(f"{home_team} to cover")
        elif away_odds > 0:
            picks.append(f"{away_team} ML value play")
        else:
            picks.append(f"{home_team} ML")
        
        # Total pick based on pace
        if sport == "NBA":
            if total > 230:
                picks.append(f"Under {total}")
            elif total < 220:
                picks.append(f"Over {total}")
            else:
                picks.append(f"{home_team} first half")
        elif sport == "NFL":
            if total > 50:
                picks.append(f"Under {total}")
            elif total < 44:
                picks.append(f"Over {total}")
            else:
                picks.append(f"Both teams to score")
        else:
            picks.append(f"{home_team} to win")
        
        pick = picks[0]
        
        # Generate reasoning
        reasons = []
        if home_odds < -120:
            reasons.append(f"{home_team} favored by market")
        elif away_odds > 0:
            reasons.append(f"{away_team} offers value at plus money")
        
        if home_stats['recent_form'].count('W') >= 3:
            reasons.append(f"{home_team} has won {home_stats['recent_form'].count('W')} of last 5")
        
        if abs(home_odds - away_odds) > 50:
            reasons.append("Significant odds disparity detected")
        
        if sport == "NBA":
            if total > 225:
                reasons.append("High total suggests fast-paced matchup")
            elif total < 215:
                reasons.append("Low total favors defensive battle")
        
        reasoning = " | ".join(reasons[:2]) if reasons else f"Analyzing {home_team} vs {away_team} matchup data"
        
        predictions.append({
            "game": f"{home_team} vs {away_team}",
            "sport": sport,
            "pick": pick,
            "confidence": confidence,
            "ev": ev,
            "reasoning": reasoning,
            "home_odds": home_odds,
            "away_odds": away_odds,
            "total": total
        })
    
    return predictions

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
        # Get available sports from ESPN API (not mock data)
        available_sports = get_available_sports()
        sport_options = [name for _, name in available_sports]
        sport_codes = [code for code, _ in available_sports]
        
        # Default to first available or use session state
        default_index = 0
        current_sport = st.session_state.get('selected_sport', 'NBA').lower()
        if current_sport in sport_codes:
            default_index = sport_codes.index(current_sport)
        
        selected_idx = st.selectbox("Select Sport", range(len(sport_options)), 
                                     format_func=lambda i: sport_options[i],
                                     index=default_index)
        st.session_state.selected_sport = sport_codes[selected_idx].upper()
    
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
    
    # Fetch games first (needed for AI predictions)
    selected_sport_code = st.session_state.get('selected_sport', 'NBA').lower()
    games, source = fetch_games_with_fallback(selected_sport_code)
    
    # Generate AI predictions based on actual games
    predictions = get_ai_predictions(games)
    
    if not predictions:
        st.info("No AI predictions available for today's games")
    
    cols = st.columns(min(len(predictions), 3))
    
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
                    <span style="color: #8A8F98; font-size: 0.75rem;">Confidence: {pred['confidence']}%</span>
                    <span style="color: #00e701; font-size: 0.75rem;">+{pred['ev']}% EV</span>
                </div>
                <div class="confidence-bar" style="margin-top: 0.5rem;">
                    <div class="confidence-fill" style="width: {pred['confidence']}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Live Games (games already fetched above for predictions)
    st.markdown("<h3 style='margin: 2rem 0 1rem;'>🔴 Live & Upcoming Games</h3>", unsafe_allow_html=True)
    
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
    
    # Duplicate for seamless loop
    ticker_content = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏀&nbsp;&nbsp;&nbsp;&nbsp;".join(ticker_items * 6)
    
    # Live Odds Ticker - using st.container to avoid CSS parsing issues
    with st.container():
        st.markdown("---")
        st.caption("LIVE ODDS TICKER")
        
        # Animated marquee ticker
        ticker_html = f'''
        <div class="ticker-container">
            <div class="ticker-track">
                <div class="ticker-item" style="color: #00e701; font-weight: 600;">{ticker_content}</div>
                <div class="ticker-item" style="color: #00e701; font-weight: 600;">{ticker_content}</div>
            </div>
        </div>
        '''
        st.components.v1.html(ticker_html, height=50)

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
