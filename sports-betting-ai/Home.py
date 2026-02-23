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
import json
from pathlib import Path

# Import auth functions with premium support
from auth import (
    is_premium_user, 
    is_admin,
    can_make_prediction, 
    increment_prediction, 
    predictions_remaining,
    FREE_PREDICTIONS_LIMIT,
    STRIPE_CHECKOUT_URL
)

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

def load_cached_odds(sport="nba"):
    """Load odds from the cached JSON file updated by cron"""
    try:
        cache_path = Path(__file__).parent / "api" / "yahoo_odds_cache.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                data = json.load(f)
                sport_data = data.get('sports', {}).get(sport.lower(), [])
                if sport_data:
                    games = []
                    for game in sport_data[:8]:  # Limit to 8 games
                        games.append({
                            'id': game['game_id'],
                            'sport': game['sport'],
                            'home_team': game['home_team'],
                            'away_team': game['away_team'],
                            'home_odds': game.get('home_ml', -140),
                            'away_odds': game.get('away_ml', 120),
                            'spread': game.get('home_spread', -3.5),
                            'total': game.get('total', 228.5),
                            'time': game['commence_time'],
                            'status': 'upcoming',
                            'source': 'cached'
                        })
                    return games
    except Exception as e:
        print(f"Cache load error: {e}")
    return []

# Combined fetch with fallback
def fetch_games_with_fallback(sport="nba"):
    """Try cached odds first, then ESPN API, then Yahoo scraping, then mock data"""
    # Try cached odds first (updated every 2 hours by cron)
    games = load_cached_odds(sport)
    if games:
        return games, "Cached Odds"
    
    # Try ESPN API
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
    
    /* Prediction Details Styling */
    details {
        transition: all 0.3s ease;
    }
    details > summary {
        cursor: pointer;
        user-select: none;
        -webkit-user-select: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    details > summary::-webkit-details-marker {
        display: none;
    }
    details > summary::before {
        content: '▼';
        font-size: 0.6rem;
        transition: transform 0.2s;
        color: #00d2ff;
    }
    details[open] > summary::before {
        transform: rotate(180deg);
    }
    details[open] {
        animation: slideDown 0.3s ease;
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
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

def get_detailed_prediction_reasoning(game):
    """Generate detailed, game-specific prediction reasoning with rich contextual data"""
    home_team = game.get('home_team', '')
    away_team = game.get('away_team', '')
    sport = game.get('sport', 'NBA')
    home_odds = game.get('home_odds', -110)
    away_odds = game.get('away_odds', -110)
    spread = game.get('spread', 0)
    total = game.get('total', 220)
    game_time = game.get('time', 'TBD')
    
    # Use enriched data from scraper if available
    home_record = game.get('home_record', '18-18')
    away_record = game.get('away_record', '14-22')
    home_win_pct = game.get('home_win_pct', 0.5)
    away_win_pct = game.get('away_win_pct', 0.4)
    home_last_5 = game.get('home_last_5', 'LWLWL')
    away_last_5 = game.get('away_last_5', 'WLWLL')
    home_injuries = game.get('home_injuries_summary', '')
    away_injuries = game.get('away_injuries_summary', '')
    
    # Determine favorite
    if home_odds < 0 and (away_odds > 0 or home_odds < away_odds):
        favorite = home_team
        fav_odds = home_odds
        underdog = away_team
        spread_val = abs(spread) if spread else 1.5
    elif away_odds < 0 and (home_odds > 0 or away_odds < home_odds):
        favorite = away_team
        fav_odds = away_odds
        underdog = home_team
        spread_val = abs(spread) if spread else 1.5
    else:
        favorite = home_team
        fav_odds = home_odds
        underdog = away_team
        spread_val = 1.5
    
    # Calculate implied probability
    if fav_odds < 0:
        win_prob = round(abs(fav_odds) / (abs(fav_odds) + 100) * 100)
    else:
        win_prob = round(100 / (fav_odds + 100) * 100)
    
    # COMPREHENSIVE TEAM DATABASE - All Sports
    TEAM_DATABASE = {
        # NBA - All 30 Teams
        "Oklahoma City Thunder": {"sport": "nba", "arena": "Paycom Center", "conference": "West", "division": "Northwest", "star": "Shai Gilgeous-Alexander", "ppg": 32.1, "recent_form": "coming off a dominant stretch"},
        "Denver Nuggets": {"sport": "nba", "arena": "Ball Arena", "conference": "West", "division": "Northwest", "star": "Nikola Jokic", "ppg": 29.1, "recent_form": "starting to dominate at altitude again"},
        "Minnesota Timberwolves": {"sport": "nba", "arena": "Target Center", "conference": "West", "division": "Northwest", "star": "Anthony Edwards", "ppg": 27.2, "recent_form": "battling through a tough stretch"},
        "Portland Trail Blazers": {"sport": "nba", "arena": "Moda Center", "conference": "West", "division": "Northwest", "star": "Jerami Grant", "ppg": 21.8, "recent_form": "rebuilding with young talent"},
        "Utah Jazz": {"sport": "nba", "arena": "Delta Center", "conference": "West", "division": "Northwest", "star": "Lauri Markkanen", "ppg": 23.4, "recent_form": "competitive but inconsistent"},
        "Boston Celtics": {"sport": "nba", "arena": "TD Garden", "conference": "East", "division": "Atlantic", "star": "Jayson Tatum", "ppg": 27.8, "recent_form": "on a dominant five-game winning streak"},
        "Philadelphia 76ers": {"sport": "nba", "arena": "Wells Fargo Center", "conference": "East", "division": "Atlantic", "star": "Joel Embiid", "ppg": 0, "recent_form": "struggling without their MVP"},
        "New York Knicks": {"sport": "nba", "arena": "Madison Square Garden", "conference": "East", "division": "Atlantic", "star": "Jalen Brunson", "ppg": 26.4, "recent_form": "surging up the East standings"},
        "Brooklyn Nets": {"sport": "nba", "arena": "Barclays Center", "conference": "East", "division": "Atlantic", "star": "Mikal Bridges", "ppg": 21.2, "recent_form": "in transition mode"},
        "Toronto Raptors": {"sport": "nba", "arena": "Scotiabank Arena", "conference": "East", "division": "Atlantic", "star": "Scottie Barnes", "ppg": 19.8, "recent_form": "rebuilding phase"},
        "Milwaukee Bucks": {"sport": "nba", "arena": "Fiserv Forum", "conference": "East", "division": "Central", "star": "Giannis Antetokounmpo", "ppg": 30.2, "recent_form": "battling through inconsistency"},
        "Cleveland Cavaliers": {"sport": "nba", "arena": "Rocket Mortgage FieldHouse", "conference": "East", "division": "Central", "star": "Donovan Mitchell", "ppg": 28.4, "recent_form": "bouncing back strong after a rare loss"},
        "Indiana Pacers": {"sport": "nba", "arena": "Gainbridge Fieldhouse", "conference": "East", "division": "Central", "star": "Tyrese Haliburton", "ppg": 20.9, "recent_form": "high-powered offense clicking"},
        "Chicago Bulls": {"sport": "nba", "arena": "United Center", "conference": "East", "division": "Central", "star": "DeMar DeRozan", "ppg": 22.3, "recent_form": "trying to stay in playoff race"},
        "Detroit Pistons": {"sport": "nba", "arena": "Little Caesars Arena", "conference": "East", "division": "Central", "star": "Cade Cunningham", "ppg": 22.1, "recent_form": "showing flashes of future potential"},
        "Miami Heat": {"sport": "nba", "arena": "Kaseya Center", "conference": "East", "division": "Southeast", "star": "Jimmy Butler", "ppg": 21.5, "recent_form": "showing flashes of championship form"},
        "Orlando Magic": {"sport": "nba", "arena": "Kia Center", "conference": "East", "division": "Southeast", "star": "Paolo Banchero", "ppg": 25.1, "recent_form": "coming off a tough stretch with injuries mounting"},
        "Atlanta Hawks": {"sport": "nba", "arena": "State Farm Arena", "conference": "East", "division": "Southeast", "star": "Trae Young", "ppg": 26.7, "recent_form": "offense firing but defense lagging"},
        "Charlotte Hornets": {"sport": "nba", "arena": "Spectrum Center", "conference": "East", "division": "Southeast", "star": "LaMelo Ball", "ppg": 23.9, "recent_form": "competitive but coming up short"},
        "Washington Wizards": {"sport": "nba", "arena": "Capital One Arena", "conference": "East", "division": "Southeast", "star": "Jordan Poole", "ppg": 17.4, "recent_form": "in full rebuild mode"},
        "Phoenix Suns": {"sport": "nba", "arena": "Footprint Center", "conference": "West", "division": "Pacific", "star": "Kevin Durant", "ppg": 27.5, "recent_form": "finding rhythm at home after inconsistent road play"},
        "LA Clippers": {"sport": "nba", "arena": "Intuit Dome", "conference": "West", "division": "Pacific", "star": "Kawhi Leonard", "ppg": 23.5, "recent_form": "playing their best basketball of the season"},
        "Los Angeles Lakers": {"sport": "nba", "arena": "Crypto.com Arena", "conference": "West", "division": "Pacific", "star": "LeBron James", "ppg": 25.2, "recent_form": "struggling to find consistency"},
        "Golden State Warriors": {"sport": "nba", "arena": "Chase Center", "conference": "West", "division": "Pacific", "star": "Stephen Curry", "ppg": 26.8, "recent_form": "trying to climb back into playoff contention"},
        "Sacramento Kings": {"sport": "nba", "arena": "Golden 1 Center", "conference": "West", "division": "Pacific", "star": "De'Aaron Fox", "ppg": 27.1, "recent_form": "fighting for playoff positioning"},
        "Dallas Mavericks": {"sport": "nba", "arena": "American Airlines Center", "conference": "West", "division": "Southwest", "star": "Luka Dončić", "ppg": 33.9, "recent_form": "relying heavily on MVP-caliber production"},
        "Memphis Grizzlies": {"sport": "nba", "arena": "FedExForum", "conference": "West", "division": "Southwest", "star": "Ja Morant", "ppg": 0, "recent_form": "adjusting without their star"},
        "New Orleans Pelicans": {"sport": "nba", "arena": "Smoothie King Center", "conference": "West", "division": "Southwest", "star": "Zion Williamson", "ppg": 24.8, "recent_form": "when healthy, a tough out"},
        "Houston Rockets": {"sport": "nba", "arena": "Toyota Center", "conference": "West", "division": "Southwest", "star": "Alperen Şengün", "ppg": 21.2, "recent_form": "young core making strides"},
        "San Antonio Spurs": {"sport": "nba", "arena": "Frost Bank Center", "conference": "West", "division": "Southwest", "star": "Victor Wembanyama", "ppg": 24.5, "recent_form": "building around their generational talent"},
        
        # NFC Teams
        "San Francisco 49ers": {"sport": "nfl", "stadium": "Levi's Stadium", "conference": "NFC", "division": "West", "star": "Brock Purdy", "recent_form": "Super Bowl aspirations"},
        "Seattle Seahawks": {"sport": "nfl", "stadium": "Lumen Field", "conference": "NFC", "division": "West", "star": "Geno Smith", "recent_form": "fighting for playoff spot"},
        "Los Angeles Rams": {"sport": "nfl", "stadium": "SoFi Stadium", "conference": "NFC", "division": "West", "star": "Matthew Stafford", "recent_form": "defending their title"},
        "Arizona Cardinals": {"sport": "nfl", "stadium": "State Farm Stadium", "conference": "NFC", "division": "West", "star": "Kyler Murray", "recent_form": "rebuilding with young core"},
        "Dallas Cowboys": {"sport": "nfl", "stadium": "AT&T Stadium", "conference": "NFC", "division": "East", "star": "Dak Prescott", "recent_form": "looking to break through"},
        "Philadelphia Eagles": {"sport": "nfl", "stadium": "Lincoln Financial Field", "conference": "NFC", "division": "East", "star": "Jalen Hurts", "recent_form": " NFC powerhouse"},
        "New York Giants": {"sport": "nfl", "stadium": "MetLife Stadium", "conference": "NFC", "division": "East", "star": "Daniel Jones", "recent_form": "searching for consistency"},
        "Washington Commanders": {"sport": "nfl", "stadium": "FedEx Field", "conference": "NFC", "division": "East", "star": "Sam Howell", "recent_form": "new era beginning"},
        "Detroit Lions": {"sport": "nfl", "stadium": "Ford Field", "conference": "NFC", "division": "North", "star": "Jared Goff", "recent_form": "finally breaking through"},
        "Green Bay Packers": {"sport": "nfl", "stadium": "Lambeau Field", "conference": "NFC", "division": "North", "star": "Jordan Love", "recent_form": "post-Rodgers transition"},
        "Minnesota Vikings": {"sport": "nfl", "stadium": "U.S. Bank Stadium", "conference": "NFC", "division": "North", "star": "Kirk Cousins", "recent_form": "competitive but inconsistent"},
        "Chicago Bears": {"sport": "nfl", "stadium": "Soldier Field", "conference": "NFC", "division": "North", "star": "Justin Fields", "recent_form": "building around QB"},
        "Tampa Bay Buccaneers": {"sport": "nfl", "stadium": "Raymond James Stadium", "conference": "NFC", "division": "South", "star": "Baker Mayfield", "recent_form": "defending division title"},
        "New Orleans Saints": {"sport": "nfl", "stadium": "Caesars Superdome", "conference": "NFC", "division": "South", "star": "Derek Carr", "recent_form": "looking to reclaim division"},
        "Atlanta Falcons": {"sport": "nfl", "stadium": "Mercedes-Benz Stadium", "conference": "NFC", "division": "South", "star": "Desmond Ridder", "recent_form": "young QB developing"},
        "Carolina Panthers": {"sport": "nfl", "stadium": "Bank of America Stadium", "conference": "NFC", "division": "South", "star": "Bryce Young", "recent_form": "rebuilding with rookie QB"},
        
        # AFC Teams
        "Kansas City Chiefs": {"sport": "nfl", "stadium": "Arrowhead Stadium", "conference": "AFC", "division": "West", "star": "Patrick Mahomes", "recent_form": "defending champs"},
        "Las Vegas Raiders": {"sport": "nfl", "stadium": "Allegiant Stadium", "conference": "AFC", "division": "West", "star": "Jimmy Garoppolo", "recent_form": "new regime in place"},
        "Los Angeles Chargers": {"sport": "nfl", "stadium": "SoFi Stadium", "conference": "AFC", "division": "West", "star": "Justin Herbert", "recent_form": "talented but underperforming"},
        "Denver Broncos": {"sport": "nfl", "stadium": "Empower Field", "conference": "AFC", "division": "West", "star": "Russell Wilson", "recent_form": "looking for answers"},
        "Buffalo Bills": {"sport": "nfl", "stadium": "Highmark Stadium", "conference": "AFC", "division": "East", "star": "Josh Allen", "recent_form": "Super Bowl favorites"},
        "Miami Dolphins": {"sport": "nfl", "stadium": "Hard Rock Stadium", "conference": "AFC", "division": "East", "star": "Tua Tagovailoa", "recent_form": "high-powered offense"},
        "New England Patriots": {"sport": "nfl", "stadium": "Gillette Stadium", "conference": "AFC", "division": "East", "star": "Mac Jones", "recent_form": "post-Brady rebuild"},
        "New York Jets": {"sport": "nfl", "stadium": "MetLife Stadium", "conference": "AFC", "division": "East", "star": "Aaron Rodgers", "recent_form": "hype vs reality"},
        "Baltimore Ravens": {"sport": "nfl", "stadium": "M&T Bank Stadium", "conference": "AFC", "division": "North", "star": "Lamar Jackson", "recent_form": "MVP candidate"},
        "Cincinnati Bengals": {"sport": "nfl", "stadium": "Paycor Stadium", "conference": "AFC", "division": "North", "star": "Joe Burrow", "recent_form": "injury-plagued"},
        "Cleveland Browns": {"sport": "nfl", "stadium": "Cleveland Browns Stadium", "conference": "AFC", "division": "North", "star": "Deshaun Watson", "recent_form": "underachieving"},
        "Pittsburgh Steelers": {"sport": "nfl", "stadium": "Acrisure Stadium", "conference": "AFC", "division": "North", "star": "Kenny Pickett", "recent_form": "defense keeping them competitive"},
        "Jacksonville Jaguars": {"sport": "nfl", "stadium": "TIAA Bank Field", "conference": "AFC", "division": "South", "star": "Trevor Lawrence", "recent_form": "expected to take next step"},
        "Tennessee Titans": {"sport": "nfl", "stadium": "Nissan Stadium", "conference": "AFC", "division": "South", "star": "Ryan Tannehill", "recent_form": "rebuilding"},
        "Indianapolis Colts": {"sport": "nfl", "stadium": "Lucas Oil Stadium", "conference": "AFC", "division": "South", "star": "Anthony Richardson", "recent_form": "rookie QB era"},
        "Houston Texans": {"sport": "nfl", "stadium": "NRG Stadium", "conference": "AFC", "division": "South", "star": "C.J. Stroud", "recent_form": "surprising everyone"},
        
        # MLB - All 30 Teams
        "New York Yankees": {"sport": "mlb", "stadium": "Yankee Stadium", "league": "AL", "division": "East", "star": "Aaron Judge", "avg": 0.267, "era": 3.42, "recent_form": "World Series aspirations"},
        "Boston Red Sox": {"sport": "mlb", "stadium": "Fenway Park", "league": "AL", "division": "East", "star": "Rafael Devers", "avg": 0.271, "era": 4.12, "recent_form": "competitive in tough division"},
        "Toronto Blue Jays": {"sport": "mlb", "stadium": "Rogers Centre", "league": "AL", "division": "East", "star": "Vladimir Guerrero Jr.", "avg": 0.289, "era": 3.85, "recent_form": "playoff contenders"},
        "Tampa Bay Rays": {"sport": "mlb", "stadium": "Tropicana Field", "league": "AL", "division": "East", "star": "Wander Franco", "avg": 0.281, "era": 3.65, "recent_form": "small market excellence"},
        "Baltimore Orioles": {"sport": "mlb", "stadium": "Camden Yards", "league": "AL", "division": "East", "star": "Adley Rutschman", "avg": 0.275, "era": 3.92, "recent_form": "young core ascending"},
        "Chicago White Sox": {"sport": "mlb", "stadium": "Guaranteed Rate Field", "league": "AL", "division": "Central", "star": "Luis Robert Jr.", "avg": 0.268, "era": 4.25, "recent_form": "underperforming expectations"},
        "Cleveland Guardians": {"sport": "mlb", "stadium": "Progressive Field", "league": "AL", "division": "Central", "star": "José Ramírez", "avg": 0.279, "era": 3.72, "recent_form": "AL Central contenders"},
        "Detroit Tigers": {"sport": "mlb", "stadium": "Comerica Park", "league": "AL", "division": "Central", "star": "Spencer Torkelson", "avg": 0.241, "era": 4.55, "recent_form": "rebuilding phase"},
        "Kansas City Royals": {"sport": "mlb", "stadium": "Kauffman Stadium", "league": "AL", "division": "Central", "star": "Bobby Witt Jr.", "avg": 0.276, "era": 4.32, "recent_form": "young talent emerging"},
        "Minnesota Twins": {"sport": "mlb", "stadium": "Target Field", "league": "AL", "division": "Central", "star": "Carlos Correa", "avg": 0.265, "era": 3.95, "recent_form": "playoff hopefuls"},
        "Houston Astros": {"sport": "mlb", "stadium": "Minute Maid Park", "league": "AL", "division": "West", "star": "Jose Altuve", "avg": 0.283, "era": 3.48, "recent_form": "World Series contenders"},
        "Los Angeles Angels": {"sport": "mlb", "stadium": "Angel Stadium", "league": "AL", "division": "West", "star": "Mike Trout", "avg": 0.272, "era": 4.65, "recent_form": "wasting generational talent"},
        "Oakland Athletics": {"sport": "mlb", "stadium": "Oakland Coliseum", "league": "AL", "division": "West", "star": "Brent Rooker", "avg": 0.245, "era": 4.82, "recent_form": "rebuilding mode"},
        "Seattle Mariners": {"sport": "mlb", "stadium": "T-Mobile Park", "league": "AL", "division": "West", "star": "Julio Rodríguez", "avg": 0.281, "era": 3.78, "recent_form": "playoff drought ending"},
        "Texas Rangers": {"sport": "mlb", "stadium": "Globe Life Field", "league": "AL", "division": "West", "star": "Corey Seager", "avg": 0.278, "era": 4.15, "recent_form": "defending champions"},
        "Atlanta Braves": {"sport": "mlb", "stadium": "Truist Park", "league": "NL", "division": "East", "star": "Ronald Acuña Jr.", "avg": 0.292, "era": 3.62, "recent_form": "NL powerhouse"},
        "New York Mets": {"sport": "mlb", "stadium": "Citi Field", "league": "NL", "division": "East", "star": "Pete Alonso", "avg": 0.265, "era": 4.25, "recent_form": "spending big"},
        "Philadelphia Phillies": {"sport": "mlb", "stadium": "Citizens Bank Park", "league": "NL", "division": "East", "star": "Bryce Harper", "avg": 0.288, "era": 3.88, "recent_form": "World Series contenders"},
        "Washington Nationals": {"sport": "mlb", "stadium": "Nationals Park", "league": "NL", "division": "East", "star": "CJ Abrams", "avg": 0.258, "era": 4.42, "recent_form": "post-Soto rebuild"},
        "Miami Marlins": {"sport": "mlb", "stadium": "loanDepot park", "league": "NL", "division": "East", "star": "Jazz Chisholm Jr.", "avg": 0.252, "era": 4.35, "recent_form": "sneaky competitive"},
        "Chicago Cubs": {"sport": "mlb", "stadium": "Wrigley Field", "league": "NL", "division": "Central", "star": "Nico Hoerner", "avg": 0.271, "era": 3.95, "recent_form": "playoff hopefuls"},
        "Cincinnati Reds": {"sport": "mlb", "stadium": "Great American Ball Park", "league": "NL", "division": "Central", "star": "Elly De La Cruz", "avg": 0.259, "era": 4.18, "recent_form": "exciting young team"},
        "Milwaukee Brewers": {"sport": "mlb", "stadium": "American Family Field", "league": "NL", "division": "Central", "star": "Christian Yelich", "avg": 0.274, "era": 3.68, "recent_form": "NL Central favorites"},
        "Pittsburgh Pirates": {"sport": "mlb", "stadium": "PNC Park", "league": "NL", "division": "Central", "star": "Ke'Bryan Hayes", "avg": 0.263, "era": 4.45, "recent_form": "rebuilding"},
        "St. Louis Cardinals": {"sport": "mlb", "stadium": "Busch Stadium", "league": "NL", "division": "Central", "star": "Paul Goldschmidt", "avg": 0.276, "era": 3.85, "recent_form": "veteran contenders"},
        "Arizona Diamondbacks": {"sport": "mlb", "stadium": "Chase Field", "league": "NL", "division": "West", "star": "Corbin Carroll", "avg": 0.269, "era": 4.12, "recent_form": "surprise NLCS team"},
        "Colorado Rockies": {"sport": "mlb", "stadium": "Coors Field", "league": "NL", "division": "West", "star": "Nolan Jones", "avg": 0.281, "era": 5.25, "recent_form": "Coors Field effect"},
        "Los Angeles Dodgers": {"sport": "mlb", "stadium": "Dodger Stadium", "league": "NL", "division": "West", "star": "Shohei Ohtani", "avg": 0.295, "era": 3.22, "recent_form": "NL favorites"},
        "San Diego Padres": {"sport": "mlb", "stadium": "Petco Park", "league": "NL", "division": "West", "star": "Manny Machado", "avg": 0.275, "era": 3.75, "recent_form": "star-studded"},
        "San Francisco Giants": {"sport": "mlb", "stadium": "Oracle Park", "league": "NL", "division": "West", "star": "Matt Chapman", "avg": 0.268, "era": 3.95, "recent_form": "veteran savvy"},
        
        # NHL - All 32 Teams
        "Boston Bruins": {"sport": "nhl", "arena": "TD Garden", "conference": "Eastern", "division": "Atlantic", "star": "David Pastrnak", "goals": 45, "recent_form": "defending Presidents' Trophy"},
        "Buffalo Sabres": {"sport": "nhl", "arena": "KeyBank Center", "conference": "Eastern", "division": "Atlantic", "star": "Tage Thompson", "goals": 42, "recent_form": " playoff drought ending"},
        "Detroit Red Wings": {"sport": "nhl", "arena": "Little Caesars Arena", "conference": "Eastern", "division": "Atlantic", "star": "Alex DeBrincat", "goals": 38, "recent_form": "retooling"},
        "Florida Panthers": {"sport": "nhl", "arena": "Amerant Bank Arena", "conference": "Eastern", "division": "Atlantic", "star": "Matthew Tkachuk", "goals": 40, "recent_form": "defending East champs"},
        "Montreal Canadiens": {"sport": "nhl", "arena": "Bell Centre", "conference": "Eastern", "division": "Atlantic", "star": "Nick Suzuki", "goals": 28, "recent_form": "rebuilding"},
        "Ottawa Senators": {"sport": "nhl", "arena": "Canadian Tire Centre", "conference": "Eastern", "division": "Atlantic", "star": "Brady Tkachuk", "goals": 35, "recent_form": "young core ascending"},
        "Tampa Bay Lightning": {"sport": "nhl", "arena": "Amalie Arena", "conference": "Eastern", "division": "Atlantic", "star": "Nikita Kucherov", "goals": 44, "recent_form": "still contenders"},
        "Toronto Maple Leafs": {"sport": "nhl", "arena": "Scotiabank Arena", "conference": "Eastern", "division": "Atlantic", "star": "Auston Matthews", "goals": 58, "recent_form": "regular season dominance"},
        "Carolina Hurricanes": {"sport": "nhl", "arena": "PNC Arena", "conference": "Eastern", "division": "Metropolitan", "star": "Sebastian Aho", "goals": 32, "recent_form": "playoff threats"},
        "Columbus Blue Jackets": {"sport": "nhl", "arena": "Nationwide Arena", "conference": "Eastern", "division": "Metropolitan", "star": "Johnny Gaudreau", "goals": 26, "recent_form": "rebuilding"},
        "New Jersey Devils": {"sport": "nhl", "arena": "Prudential Center", "conference": "Eastern", "division": "Metropolitan", "star": "Jack Hughes", "goals": 43, "recent_form": "young and dangerous"},
        "New York Islanders": {"sport": "nhl", "arena": "UBS Arena", "conference": "Eastern", "division": "Metropolitan", "star": "Bo Horvat", "goals": 30, "recent_form": "defensive identity"},
        "New York Rangers": {"sport": "nhl", "arena": "Madison Square Garden", "conference": "Eastern", "division": "Metropolitan", "star": "Artemi Panarin", "goals": 41, "recent_form": "Presidents' Trophy favorites"},
        "Philadelphia Flyers": {"sport": "nhl", "arena": "Wells Fargo Center", "conference": "Eastern", "division": "Metropolitan", "star": "Travis Konecny", "goals": 33, "recent_form": "surprise success"},
        "Pittsburgh Penguins": {"sport": "nhl", "arena": "PPG Paints Arena", "conference": "Eastern", "division": "Metropolitan", "star": "Sidney Crosby", "goals": 36, "recent_form": "Crosby still elite"},
        "Washington Capitals": {"sport": "nhl", "arena": "Capital One Arena", "conference": "Eastern", "division": "Metropolitan", "star": "Alex Ovechkin", "goals": 42, "recent_form": "chasing Gretzky"},
        "Arizona Coyotes": {"sport": "nhl", "arena": "Mullett Arena", "conference": "Western", "division": "Central", "star": "Clayton Keller", "goals": 34, "recent_form": "relocation looming"},
        "Chicago Blackhawks": {"sport": "nhl", "arena": "United Center", "conference": "Western", "division": "Central", "star": "Connor Bedard", "goals": 38, "recent_form": "Bedard era begins"},
        "Colorado Avalanche": {"sport": "nhl", "arena": "Ball Arena", "conference": "Western", "division": "Central", "star": "Nathan MacKinnon", "goals": 48, "recent_form": "Cup contenders"},
        "Dallas Stars": {"sport": "nhl", "arena": "American Airlines Center", "conference": "Western", "division": "Central", "star": "Jason Robertson", "goals": 40, "recent_form": "deep and balanced"},
        "Minnesota Wild": {"sport": "nhl", "arena": "Xcel Energy Center", "conference": "Western", "division": "Central", "star": "Kirill Kaprizov", "goals": 44, "recent_form": "playoff regulars"},
        "Nashville Predators": {"sport": "nhl", "arena": "Bridgestone Arena", "conference": "Western", "division": "Central", "star": "Roman Josi", "goals": 22, "recent_form": "surging late"},
        "St. Louis Blues": {"sport": "nhl", "arena": "Enterprise Center", "conference": "Western", "division": "Central", "star": "Robert Thomas", "goals": 29, "recent_form": "retooling on the fly"},
        "Winnipeg Jets": {"sport": "nhl", "arena": "Canada Life Centre", "conference": "Western", "division": "Central", "star": "Kyle Connor", "goals": 37, "recent_form": "defensive juggernaut"},
        "Anaheim Ducks": {"sport": "nhl", "arena": "Honda Center", "conference": "Western", "division": "Pacific", "star": "Troy Terry", "goals": 27, "recent_form": "rebuilding"},
        "Calgary Flames": {"sport": "nhl", "arena": "Scotiabank Saddledome", "conference": "Western", "division": "Pacific", "star": "Jonathan Huberdeau", "goals": 25, "recent_form": "new core"},
        "Edmonton Oilers": {"sport": "nhl", "arena": "Rogers Place", "conference": "Western", "division": "Pacific", "star": "Connor McDavid", "goals": 62, "recent_form": "offensive powerhouse"},
        "Los Angeles Kings": {"sport": "nhl", "arena": "Crypto.com Arena", "conference": "Western", "division": "Pacific", "star": "Adrian Kempe", "goals": 36, "recent_form": "contenders again"},
        "San Jose Sharks": {"sport": "nhl", "arena": "SAP Center", "conference": "Western", "division": "Pacific", "star": "Tomas Hertl", "goals": 28, "recent_form": "rebuilding"},
        "Seattle Kraken": {"sport": "nhl", "arena": "Climate Pledge Arena", "conference": "Western", "division": "Pacific", "star": "Jared McCann", "goals": 35, "recent_form": "second-year surge"},
        "Vancouver Canucks": {"sport": "nhl", "arena": "Rogers Arena", "conference": "Western", "division": "Pacific", "star": "Elias Pettersson", "goals": 39, "recent_form": "surprise success"},
        "Vegas Golden Knights": {"sport": "nhl", "arena": "T-Mobile Arena", "conference": "Western", "division": "Pacific", "star": "Jack Eichel", "goals": 31, "recent_form": "defending champions"},
        
        # NCAAB - Major Programs
        "Connecticut Huskies": {"sport": "ncaab", "arena": "Harry A. Gampel Pavilion", "conference": "Big East", "star": "Donovan Clingan", "ppg": 13.0, "recent_form": "defending champs"},
        "Purdue Boilermakers": {"sport": "ncaab", "arena": "Mackey Arena", "conference": "Big Ten", "star": "Zach Edey", "ppg": 25.2, "recent_form": "national player of the year leading"},
        "Houston Cougars": {"sport": "ncaab", "arena": "Fertitta Center", "conference": "Big 12", "star": "Jamal Shead", "ppg": 18.5, "recent_form": "tough defensive identity"},
        "Alabama Crimson Tide": {"sport": "ncaab", "arena": "Coleman Coliseum", "conference": "SEC", "star": "Mark Sears", "ppg": 21.3, "recent_form": "fast-paced offense"},
        "Tennessee Volunteers": {"sport": "ncaab", "arena": "Thompson-Boling Arena", "conference": "SEC", "star": "Dalton Knecht", "ppg": 21.7, "recent_form": "Elite Eight run"},
        "Arizona Wildcats": {"sport": "ncaab", "arena": "McKale Center", "conference": "Pac-12", "star": "Caleb Love", "ppg": 18.2, "recent_form": "Pac-12 dominance"},
        "Illinois Fighting Illini": {"sport": "ncaab", "arena": "State Farm Center", "conference": "Big Ten", "star": "Terrence Shannon Jr.", "ppg": 23.0, "recent_form": "tournament dark horse"},
        "North Carolina Tar Heels": {"sport": "ncaab", "arena": "Dean Smith Center", "conference": "ACC", "star": "R.J. Davis", "ppg": 21.3, "recent_form": "ACC title favorites"},
        "Baylor Bears": {"sport": "ncaab", "arena": "Ferrell Center", "conference": "Big 12", "star": "Ja'Kobi Gillespie", "ppg": 17.8, "recent_form": "defensive minded"},
        "Creighton Bluejays": {"sport": "ncaab", "arena": "CHI Health Center", "conference": "Big East", "star": "Steven Ashworth", "ppg": 16.9, "recent_form": "offensive efficiency"},
        "Duke Blue Devils": {"sport": "ncaab", "arena": "Cameron Indoor Stadium", "conference": "ACC", "star": "Kyle Filipowski", "ppg": 16.7, "recent_form": "Coach K legacy"},
        "Kansas Jayhawks": {"sport": "ncaab", "arena": "Allen Fieldhouse", "conference": "Big 12", "star": "Kevin McCullar Jr.", "ppg": 18.2, "recent_form": "blue blood status"},
        "Gonzaga Bulldogs": {"sport": "ncaab", "arena": "McCarthey Athletic Center", "conference": "WCC", "star": "Graham Ike", "ppg": 16.5, "recent_form": "mid-major powerhouse"},
        "FAU Owls": {"sport": "ncaab", "arena": "Eleanor R. Baldwin Arena", "conference": "AAC", "star": "Johnell Davis", "ppg": 18.2, "recent_form": "Final Four Cinderella"},
    }
    
    # Get team data
    home_db = TEAM_DATABASE.get(home_team, {"sport": sport.lower(), "arena": "Home Venue", "star": "Key Player", "ppg": 20, "recent_form": "entering this matchup"})
    away_db = TEAM_DATABASE.get(away_team, {"sport": sport.lower(), "arena": "Away Venue", "star": "Key Player", "ppg": 18, "recent_form": "looking to bounce back"})
    
    # Determine venue type by sport
    venue_type = "arena" if sport.lower() == "nba" else "stadium"
    home_venue = home_db.get(venue_type, home_db.get("arena", "home"))
    
    # Build reasoning
    factors = []
    
    # 1. Context narrative
    context = f"<b>{home_team}</b> {home_db.get('recent_form', 'enters this game')} while <b>{away_team}</b> {away_db.get('recent_form', 'looks to get back on track')}."
    
    # 2. Home advantage
    if home_win_pct > 0.58:
        pct_str = f"{int(home_win_pct * 100)}%"
        factors.append(
            f"• <b>Home Field Advantage:</b> {home_team} are formidable at {home_venue}, "
            f"boasting a {home_record} record and winning {pct_str} of home games. "
            f"Their home dominance is a significant factor."
        )
    elif home_win_pct > 0.5:
        factors.append(
            f"• <b>Home Edge:</b> {home_team} have been solid at {home_venue} with a {home_record} record, "
            f"while {away_team} are {away_record} on the road."
        )
    
    # 3. Star power / Key players
    home_star = home_db.get("star", "their star player")
    away_star = away_db.get("star", "their key player")
    home_ppg = home_db.get("ppg", 20)
    away_ppg = away_db.get("ppg", 18)
    
    if home_ppg > away_ppg + 5:
        factors.append(
            f"• <b>Star Power:</b> {home_star} leads {home_team}, averaging {home_ppg} PPG, "
            f"giving them a clear offensive advantage over {away_star} ({away_ppg} PPG)."
        )
    elif away_ppg > home_ppg + 5:
        factors.append(
            f"• <b>Star Power Edge:</b> {away_star} ({away_ppg} PPG) provides {away_team} "
            f"with elite scoring ability that {home_team} will struggle to contain."
        )
    
    # 4. Recent form
    home_wins = home_last_5.count('W') if home_last_5 else 0
    away_wins = away_last_5.count('W') if away_last_5 else 0
    if home_wins >= 4:
        factors.append(f"• <b>Momentum:</b> {home_team} are hot, going {home_last_5} in their last 5 games.")
    elif away_wins >= 4:
        factors.append(f"• <b>Road Warriors:</b> Despite being away, {away_team} are {away_last_5} in their last 5.")
    
    # 5. Division context
    home_div = home_db.get('division', '')
    if home_div and sport.lower() in ['nba', 'nfl']:
        factors.append(f"• <b>Divisional Play:</b> This {home_div} division matchup carries extra weight.")
    
    # 6. Odds summary
    if spread_val <= 3:
        factors.append(f"• <b>Even Matchup:</b> Oddsmakers see this as tight — {favorite} favored by just {spread_val} points ({win_prob}% win probability).")
    else:
        factors.append(f"• <b>Favorite Status:</b> {favorite} are {spread_val}-point favorites with {win_prob}% implied win probability.")
    
    # Format output
    if factors:
        reasoning = f"<p style='margin-bottom: 0.5rem; color: #e0e0e0;'>{context}</p>" + "<br>".join(factors[:5])
    else:
        reasoning = f"<p>{context}</p><br>• <b>Matchup Analysis:</b> Two competitive teams face off with {favorite} holding a slight edge.</p>"
    
    return reasoning
    if home_div != 'N/A' and home_div:
        factors.append(
            f"• <b>Divisional Play:</b> {home_team} are {home_div} against {home_db.get('division', 'divisional')} opponents "
            f"and have historically performed well in conference matchups."
        )
    
    # 5. Odds Summary with Context
    if spread_val <= 3:
        factors.append(
            f"• <b>Tight Contest Expected:</b> Oddsmakers have {favorite} as {spread_val}-point favorites "
            f"with roughly {win_prob}% implied win probability, suggesting a competitive game."
        )
    else:
        factors.append(
            f"• <b>Favorite Status:</b> {favorite} are {spread_val}-point favorites "
            f"with roughly {win_prob}% implied win probability, reflecting their advantages in this matchup."
        )
    
    # Format the final output
    if factors:
        reasoning = f"<p style='margin-bottom: 0.75rem; color: #e0e0e0;'>{context}</p>" + "<br>".join(factors[:5])
    else:
        reasoning = f"<p>{context}</p>• <b>Head-to-Head:</b> Two evenly matched teams face off, with {favorite} getting slight favoritism.</p>"
    
    return reasoning

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
    
    # Premium Banner for Free Users (hide for admin)
    if not is_premium_user() and not is_admin():
        remaining = predictions_remaining()
        if remaining > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 140, 0, 0.1) 100%);
             border: 1px solid rgba(255, 215, 0, 0.3); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="margin: 0; color: #FFD700; font-weight: 600;">⭐ Free Tier: {remaining} prediction{'s' if remaining != 1 else ''} remaining</p>
                        <p style="margin: 0; color: #8A8F98; font-size: 0.75rem;">Upgrade to unlock unlimited predictions</p>
                    </div>
                    <a href="{STRIPE_CHECKOUT_URL}" target="_blank" style="background: linear-gradient(135deg, #f1c40f 0%, #e67e22 100%); color: #0B0E14; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.875rem;">Upgrade $5/mo</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Out of predictions - show paywall
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255, 75, 75, 0.1) 0%, rgba(255, 140, 140, 0.1) 100%);
             border: 1px solid rgba(255, 75, 75, 0.3); border-radius: 12px; padding: 2rem; margin-bottom: 1rem; text-align: center;">
                <p style="margin: 0 0 0.5rem 0; color: #ff6b6b; font-weight: 600; font-size: 1.25rem;">🔒 Limit Reached</p>
                <p style="margin: 0 0 1.5rem 0; color: #8A8F98;">You've used all {FREE_PREDICTIONS_LIMIT} free predictions. Upgrade to Pro for unlimited access.</p>
                <a href="{STRIPE_CHECKOUT_URL}" target="_blank" style="background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%); color: #0B0E14; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">Upgrade to Pro — $5/month</a>
            </div>
            """, unsafe_allow_html=True)
            st.stop()
    else:
        # Premium user badge
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(0, 210, 255, 0.1) 0%, rgba(0, 231, 1, 0.1) 100%); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 12px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.25rem;">💎</span>
                <span style="color: #00d2ff; font-weight: 600;">Pro Member</span>
                <span style="color: #8A8F98; font-size: 0.75rem; margin-left: auto;">Unlimited predictions</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Title row with Sport Selector and Refresh
    col_title, col_sport, col_refresh = st.columns([3, 1, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: 0.5rem;'>Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Track your performance and AI predictions</p>", unsafe_allow_html=True)
    with col_refresh:
        if st.button(" 🔄 Refresh Odds", use_container_width=True):
            with st.spinner("Reloading fresh odds..."):
                # Clear all cached data to force re-read from file
                st.cache_data.clear()
                st.success("✅ Odds refreshed!")
                st.rerun()
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
        # Get prediction reasoning for this game
        prediction_reasoning = get_detailed_prediction_reasoning(game)
        
        # Create unique key for this game's prediction view tracking
        prediction_key = f"pred_view_{game['id']}"
        
        # Check if prediction was already viewed
        viewed_predictions = st.session_state.get('viewed_predictions', set())
        is_viewed = prediction_key in viewed_predictions
        
        # Determine if this game should show prediction details
        if is_premium_user():
            can_view = True  # Premium users always can view
        elif is_viewed:
            can_view = True  # Already viewed, can re-open
        elif can_make_prediction():
            can_view = True  # Free user with predictions remaining
        else:
            can_view = False  # Out of free predictions
        
        live_badge = '<span class="live-badge">● LIVE</span>' if game['status'] == 'live' else ''
        score_display = game.get('time', 'TBD')
        if game['status'] == 'live' and 'score' in game:
            score_display = f"{game['score']['home']} - {game['score']['away']}"
        
        if can_view:
            # Use Streamlit's expander (tracks state automatically)
            with st.expander(f"🔮 View Prediction Analysis {'✓' if is_viewed else ''}", expanded=False):
                if not is_viewed and not is_premium_user():
                    # First time viewing - decrement counter
                    increment_prediction()
                    viewed_predictions.add(prediction_key)
                    st.session_state.viewed_predictions = viewed_predictions
                    st.toast(f"📊 Predictions remaining: {predictions_remaining()}")
                
                st.markdown(f"**📊 Analysis: {game['home_team']} vs {game['away_team']}**")
                st.markdown(prediction_reasoning)
        
        # Format time from commence_time to 12h AM/PM format
        commence_time = game.get('commence_time', '')
        if commence_time and commence_time != 'TBD':
            try:
                # Parse RFC 2822 format: "Sun, 22 Feb 2026 18:00:00 +0000"
                parts = commence_time.split(' ')
                time_part = parts[4]  # "18:00:00"
                hour_24 = int(time_part.split(':')[0])
                minute = int(time_part.split(':')[1])
                
                # Convert UTC to EST (UTC-5)
                hour_est = (hour_24 - 5) % 24
                
                # Convert to 12-hour format
                if hour_est == 0:
                    hour_12 = 12
                    ampm = 'AM'
                elif hour_est < 12:
                    hour_12 = hour_est
                    ampm = 'AM'
                elif hour_est == 12:
                    hour_12 = 12
                    ampm = 'PM'
                else:
                    hour_12 = hour_est - 12
                    ampm = 'PM'
                
                formatted_time = f"{hour_12}:{minute:02d} {ampm} EST"
            except Exception as e:
                formatted_time = game.get('time', 'TBD')
        else:
            formatted_time = game.get('time', 'TBD')
        
        card_html = f'''<div class="game-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <span style="color: #00d2ff; font-size: 0.875rem; font-weight: 500;">{game['sport']}</span>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="color: #FFD700; font-size: 0.75rem; font-weight: 500;">🕒 {formatted_time}</span>
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
</div>'''
        st.components.v1.html(card_html, height=200)
        
        # Show locked message if user can't view prediction
        if not can_view:
            st.error("🔒 View prediction analysis — Upgrade to Pro for unlimited access", icon="💎")
            # Only show upgrade button if user is not admin
            if not is_admin():
                st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0 2rem 0;">
                    <a href="{STRIPE_CHECKOUT_URL}" target="_blank" style="background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%); color: #0B0E14; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">Upgrade to Pro — $5/month</a>
                </div>
                """, unsafe_allow_html=True)
    
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
