"""
Sports Betting AI Pro - Main Entry Point
Fixed navigation, improved error handling, modern UI
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Import authentication module
sys.path.insert(0, '/Users/djryan/.openclaw/workspace/user_upload')
from auth import check_session, login_form, logout, is_admin, require_auth

# Check authentication first
session = check_session()
if not session:
    st.set_page_config(page_title="Login - Sports Betting AI Pro", page_icon="🔒")
    login_form()
    st.stop()

# Page config MUST be first Streamlit command after auth check
st.set_page_config(
    page_title="Sports Betting AI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Dark Theme CSS - Enhanced
def load_css():
    st.markdown("""
    <style>
        /* Dark theme base with animated gradient */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            background-attachment: fixed;
        }
        
        /* Modern header with glow effect */
        .main-header {
            font-size: 4rem;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 50%, #00d2ff 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0,210,255,0.5);
            margin-bottom: 10px;
            letter-spacing: -2px;
            animation: gradient-shift 3s ease infinite;
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .sub-header {
            text-align: center;
            color: #a0a0c0;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        
        /* Glassmorphism cards - enhanced */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px 0 rgba(31, 38, 135, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        /* Game cards */
        .game-card {
            background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        
        .game-card:hover {
            background: linear-gradient(145deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.05) 100%);
            border-color: rgba(0,210,255,0.3);
        }
        
        /* Value pick - glowing green */
        .value-pick {
            background: linear-gradient(135deg, rgba(46,204,113,0.2) 0%, rgba(39,174,96,0.15) 50%, rgba(46,204,113,0.2) 100%);
            border: 1px solid rgba(46,204,113,0.4);
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            position: relative;
            overflow: hidden;
        }
        
        .value-pick::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(46,204,113,0.1), transparent);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }
        
        /* Live badge */
        .live-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,0,0,0.2);
            border: 1px solid rgba(255,0,0,0.5);
            padding: 8px 16px;
            border-radius: 50px;
            font-weight: 600;
            color: #ff4444;
            font-size: 0.9rem;
        }
        
        .live-dot {
            width: 8px;
            height: 8px;
            background: #ff4444;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        /* Probability bars */
        .prob-bar-bg {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .prob-bar-fill {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        }
        
        /* Team names */
        .team-name {
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .team-record {
            color: #a0a0c0;
            font-size: 0.9rem;
        }
        
        /* Stats */
        .stat-box {
            background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Odds display */
        .odds-box {
            background: rgba(0,210,255,0.1);
            border: 1px solid rgba(0,210,255,0.3);
            border-radius: 12px;
            padding: 12px 20px;
            text-align: center;
            font-weight: 700;
            color: #00d2ff;
            font-size: 1.2rem;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15,12,41,0.95) 0%, rgba(48,43,99,0.95) 100%);
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 12px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
        }
        
        /* Select boxes */
        div[data-baseweb="select"] {
            background: rgba(255,255,255,0.1) !important;
            border-radius: 12px !important;
        }
        
        /* Slider */
        .stSlider {
            padding-top: 15px !important;
        }
        
        /* Tables */
        .stDataFrame {
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Error/Success messages */
        .stAlert {
            border-radius: 12px !important;
        }
        
        /* Navigation pills */
        .nav-pill {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 10px 20px;
            margin: 5px;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .nav-pill:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(0,210,255,0.3);
        }
        
        /* Metric cards */
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
        }
        
        [data-testid="stMetric"] > div {
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Helper functions
def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🎯')

def american_to_implied(odds):
    if pd.isna(odds) or odds is None:
        return 0.5
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)

def parse_record(record):
    try:
        if pd.isna(record) or record in ['N/A', '0-0', None, '']:
            return 0, 0
        wins, losses = map(int, str(record).split('-'))
        return wins, losses
    except:
        return 0, 0

def calculate_win_prob(wins, losses, home_adv=0.03):
    total = wins + losses
    if total == 0:
        return 0.5
    return min(max((wins / total) + home_adv, 0.1), 0.9)

def format_odds(odds):
    """Format odds for display"""
    if pd.isna(odds) or odds is None:
        return "N/A"
    if odds > 0:
        return f"+{int(odds)}"
    return f"{int(odds)}"

# Header with Live Badge
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<div class="main-header">🎯 BET AI PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Machine Learning Sports Predictions</div>', unsafe_allow_html=True)
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f'''
    <div style="text-align: center; margin-top: -10px;">
        <span class="live-badge">
            <span class="live-dot"></span>
            LIVE • {current_time}
        </span>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("---")

# Sidebar with improved settings and authentication
with st.sidebar:
    # Authentication section
    session = check_session()
    if session:
        st.markdown("### 👤 User")
        st.write(f"**{session['username']}**")
        if session.get('is_admin'):
            st.markdown("`🛡️ ADMIN`")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.markdown("---")
    
    st.markdown("### ⚙️ Settings")
    
    sport = st.selectbox(
        "Select Sport",
        ['NBA', 'NFL', 'MLB', 'NHL'],
        format_func=lambda x: f"{get_sport_emoji(x)} {x.upper()}"
    )
    
    days = st.slider("Days Ahead", 1, 7, 3)
    value_threshold = st.slider("Value Edge %", 1, 20, 5) / 100
    
    st.markdown("---")
    st.markdown("### 📡 Data Sources")
    
    # Check API status
    odds_api_key = os.getenv('THEODDS_API_KEY')
    if odds_api_key:
        st.markdown("✅ The Odds API (Configured)")
    else:
        st.markdown("⚠️ The Odds API (No API Key)")
        st.caption("Set THEODDS_API_KEY in secrets for live odds")
    
    st.markdown("✅ ESPN API (Free)")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    # Show mini bet tracker stats
    try:
        from data.bet_tracker import BetTracker
        tracker = BetTracker()
        stats = tracker.get_stats()
        
        if stats['total_bets'] > 0:
            st.metric("Total Bets", stats['total_bets'])
            st.metric("Win Rate", f"{stats['win_rate']*100:.1f}%")
            profit_color = "normal" if stats['total_profit'] >= 0 else "inverse"
            st.metric("Profit", f"${stats['total_profit']:.2f}", delta_color=profit_color)
        else:
            st.caption("No bets tracked yet")
    except Exception as e:
        st.caption("Bet tracker unavailable")

# Main Content
api_error = None
odds_error = None

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    
    with st.spinner(f"Loading {sport} data..."):
        # Get ESPN data (free, always works)
        espn = ESPNAPI()
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Stats Row
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-number">{len(teams)}</div>
                <div style="color: #a0a0c0;">Teams</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-number">{len(schedule)}</div>
                <div style="color: #a0a0c0;">Upcoming</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-number">99%</div>
                <div style="color: #a0a0c0;">Uptime</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-number">{datetime.now().strftime("%H:%M")}</div>
                <div style="color: #a0a0c0;">Updated</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Try to get odds from multiple sources
        odds = pd.DataFrame()
        yahoo_cache_loaded = False
        
        # 1. Try OddsAPI first
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
        except Exception as e:
            odds_error = str(e)
            pass
        
        # 2. Fallback to Yahoo cache if OddsAPI failed or returned empty
        if odds.empty:
            try:
                # Try multiple possible paths for Yahoo cache
                yahoo_cache_paths = [
                    'api/yahoo_odds_cache.json',  # Relative to app root
                    '/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/yahoo_odds_cache.json',  # Local dev
                    os.path.join(os.path.dirname(__file__), 'api', 'yahoo_odds_cache.json'),  # Same dir as Home.py
                ]
                
                yahoo_data = None
                yahoo_cache_path = None
                
                for path in yahoo_cache_paths:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            yahoo_data = json.load(f)
                        yahoo_cache_path = path
                        break
                
                # Convert Yahoo cache to odds DataFrame format
                yahoo_games = []
                if yahoo_data:
                    sport_key = sport.lower()
                    if sport_key in yahoo_data.get('sports', {}):
                        for game in yahoo_data['sports'][sport_key]:
                            yahoo_games.append({
                                'home_team': game.get('home_team', ''),
                                'away_team': game.get('away_team', ''),
                                'home_ml': game.get('home_ml'),
                                'away_ml': game.get('away_ml'),
                                'home_spread': game.get('home_spread'),
                                'away_spread': game.get('away_spread'),
                                'total': game.get('total'),
                                'over_odds': game.get('over_odds'),
                                'under_odds': game.get('under_odds'),
                                'commence_time': game.get('commence_time'),
                                'bookmaker': game.get('bookmaker', 'Yahoo Sports')
                            })
                        
                        if yahoo_games:
                            odds = pd.DataFrame(yahoo_games)
                            yahoo_cache_loaded = True
                        
            except Exception as e:
                st.warning(f"Could not load Yahoo cache: {e}")
                pass
        
        # Show odds source info
        if odds_error and not yahoo_cache_loaded:
            with st.expander("⚠️ Odds API Issue (Click for details)"):
                st.warning("Live odds unavailable. Using estimated probabilities only.")
                st.caption(f"Error: {odds_error}")
                st.info("To get live odds, add THEODDS_API_KEY to your Streamlit secrets.")
        elif yahoo_cache_loaded:
            st.success("✅ Using Yahoo Sports odds (cached)")
            st.caption(f"Last updated: {yahoo_data.get('timestamp', 'Unknown')}")
        
        # Predictions Section
        st.markdown(f"### {get_sport_emoji(sport)} {sport.upper()} Predictions")
        
        if not schedule.empty:
            predictions = []
            
            for _, game in schedule.head(8).iterrows():  # Show 8 games
                home_rec = game.get('home_record', '0-0')
                away_rec = game.get('away_record', '0-0')
                hw, hl = parse_record(home_rec)
                aw, al = parse_record(away_rec)
                
                home_prob = calculate_win_prob(hw, hl, 0.04)
                away_prob = 1 - home_prob
                
                # Get odds for this game
                game_odds = pd.DataFrame()
                if not odds.empty:
                    game_odds = odds[
                        (odds['home_team'].str.contains(str(game['home_team']), case=False, na=False)) | 
                        (odds['away_team'].str.contains(str(game['away_team']), case=False, na=False))
                    ]
                
                if not game_odds.empty:
                    gm = game_odds.iloc[0]
                    home_ml = gm.get('home_ml')
                    away_ml = gm.get('away_ml')
                    home_implied = american_to_implied(home_ml) if pd.notna(home_ml) else home_prob
                    away_implied = american_to_implied(away_ml) if pd.notna(away_ml) else away_prob
                    
                    home_edge = home_prob - home_implied
                    away_edge = away_prob - away_implied
                    has_edge = abs(home_edge) > value_threshold or abs(away_edge) > value_threshold
                else:
                    home_ml = away_ml = None
                    home_edge = away_edge = 0
                    has_edge = False
                
                predictions.append({
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'home_prob': home_prob,
                    'away_prob': away_prob,
                    'home_ml': home_ml,
                    'away_ml': away_ml,
                    'home_edge': home_edge,
                    'away_edge': away_edge,
                    'has_edge': has_edge,
                    'game_date': game.get('date', '')
                })
            
            pred_df = pd.DataFrame(predictions)
            
            # VALUE PICKS Section
            value_picks = pred_df[pred_df['has_edge'] == True]
            if not value_picks.empty:
                st.markdown("### 💎 Value Picks")
                for _, pick in value_picks.head(3).iterrows():
                    edge_pct = max(abs(pick['home_edge']), abs(pick['away_edge'])) * 100
                    confidence = "HIGH 🔥" if edge_pct > 8 else "MED ⚡"
                    best_pick = pick['home_team'] if pick['home_edge'] > pick['away_edge'] else pick['away_team']
                    best_odds = pick['home_ml'] if pick['home_edge'] > pick['away_edge'] else pick['away_ml']
                    
                    value_pick_html = f'''
                    <div class="value-pick">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="margin: 0; color: #2ecc71;">{best_pick} ML</h3>
                                <p style="margin: 5px 0; color: #ffffff;">{pick['home_team']} vs {pick['away_team']}</p>
                            </div>
                            <div style="text-align: right;">
                                <div class="odds-box" style="font-size: 1.5rem;">{format_odds(best_odds)}</div>
                                <p style="margin: 5px 0; color: #2ecc71; font-weight: 600;">+{edge_pct:.1f}% Edge • {confidence}</p>
                            </div>
                        </div>
                    </div>
                    '''
                    components.html(value_pick_html, height=120, scrolling=False)
            
            # GAME CARDS Section
            st.markdown("### 📋 All Games")
            cols = st.columns(2)
            for idx, pred in pred_df.iterrows():
                with cols[idx % 2]:
                    with st.container():
                        # Use native Streamlit components for reliable rendering
                        with st.container(border=True):
                            # Teams header
                            t1, t2, t3 = st.columns([2, 1, 2])
                            with t1:
                                st.markdown(f"**{pred['home_team']}**")
                                st.caption("Home")
                            with t2:
                                st.markdown("<div style='text-align: center; color: #00d2ff; font-weight: bold;'>VS</div>", unsafe_allow_html=True)
                            with t3:
                                st.markdown(f"<div style='text-align: right;'><b>{pred['away_team']}</b></div>", unsafe_allow_html=True)
                                st.markdown("<div style='text-align: right;'><small>Away</small></div>", unsafe_allow_html=True)
                            
                            # Win probability
                            st.markdown("---")
                            p1, p2, p3 = st.columns([1, 2, 1])
                            with p1:
                                st.markdown(f"**{int(round(pred['home_prob']*100))}%**")
                            with p2:
                                st.markdown("<div style='text-align: center; color: #888;'>Win Probability</div>", unsafe_allow_html=True)
                            with p3:
                                st.markdown(f"<div style='text-align: right;'><b>{int(round(pred['away_prob']*100))}%</b></div>", unsafe_allow_html=True)
                            
                            # Progress bar
                            st.progress(float(pred['home_prob']))
                            
                            # Odds
                            st.markdown("---")
                            o1, o2 = st.columns(2)
                            with o1:
                                home_odds = format_odds(pred.get('home_ml', None))
                                st.metric("Home ML", home_odds if home_odds != "N/A" else "—")
                            with o2:
                                away_odds = format_odds(pred.get('away_ml', None))
                                st.metric("Away ML", away_odds if away_odds != "N/A" else "—")
                        
                        # Quick add to bet tracker
                        if st.button(f"➕ Track This Game", key=f"track_{idx}", use_container_width=True):
                            st.session_state['track_game'] = {
                                'home': pred['home_team'],
                                'away': pred['away_team'],
                                'sport': sport
                            }
                            st.info("Go to Bet Tracker to add your pick!")
        else:
            st.info("No upcoming games found for this sport.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    import traceback
    with st.expander("Debug Info"):
        st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #666;">Powered by ESPN API | Sports Betting AI Pro</div>', unsafe_allow_html=True)
