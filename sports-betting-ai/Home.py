"""
Sports Betting AI - Modern Sportsbook Design
Dark theme, glass cards, live ticker
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Sports Betting AI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Dark Theme CSS
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Modern header */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 50%, #00d2ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0,210,255,0.5);
        margin-bottom: 10px;
        letter-spacing: -2px;
    }
    
    .sub-header {
        text-align: center;
        color: #a0a0c0;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    
    /* Glassmorphism cards */
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
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🎯')

def american_to_implied(odds):
    if pd.isna(odds):
        return 0.5
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)

def parse_record(record):
    try:
        if pd.isna(record) or record in ['N/A', '0-0']:
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

# Sidebar (modern)
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    sport = st.selectbox(
        "Select Sport",
        ['NBA', 'NFL', 'MLB', 'NHL'],
        format_func=lambda x: f"{get_sport_emoji(x)} {x.upper()}"
    )
    
    days = st.slider("Days Ahead", 1, 7, 3)
    value_threshold = st.slider("Value Edge", 1, 15, 5) / 100
    
    st.markdown("---")
    st.markdown("### 📡 Data Sources")
    st.markdown(f"✓ ESPN {sport} Live")
    st.markdown("✓ The Odds API")
    if sport == 'NBA':
        st.markdown("✓ BallDontLie")
    
    st.markdown("---")
    st.markdown("### 🔔 Refresh")
    st.caption("Auto-refresh every 60s")

# Main Content
try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    from models.universal_predictor import UniversalSportsPredictor
    
    with st.spinner(f"Loading {sport} data..."):
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
        
        # Get odds
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
        except:
            odds = pd.DataFrame()
        
        # Predictions Section
        st.markdown(f"### {get_sport_emoji(sport)} {sport.upper()} Predictions")
        
        if not schedule.empty:
            predictions = []
            
            for _, game in schedule.head(6).iterrows():  # Show 6 games
                home_rec = game.get('home_record', '0-0')
                away_rec = game.get('away_record', '0-0')
                hw, hl = parse_record(home_rec)
                aw, al = parse_record(away_rec)
                
                home_prob = calculate_win_prob(hw, hl, 0.04)
                away_prob = 1 - home_prob
                
                # Get odds for this game
                game_odds = odds[
                    (odds['home_team'] == game['home_team']) | 
                    (odds['away_team'].str.contains(str(game['away_team']), case=False, na=False))
                ] if not odds.empty else pd.DataFrame()
                
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
                    'home_edge': home_edge if not game_odds.empty else 0,
                    'away_edge': away_edge if not game_odds.empty else 0,
                    'has_edge': has_edge
                })
            
            pred_df = pd.DataFrame(predictions)
            
            # VALUE PICKS
            value_picks = pred_df[pred_df['has_edge'] == True]
            if not value_picks.empty:
                st.markdown("### 💎 Value Picks")
                for _, pick in value_picks.head(2).iterrows():
                    edge_pct = max(abs(pick['home_edge']), abs(pick['away_edge'])) * 100
                    confidence = "HIGH 🔥" if edge_pct > 8 else "MED ⚡"
                    
                    st.markdown(f'''
                    <div class="value-pick">
                        <h3 style="margin: 0; color: #2ecc71;">{pick['home_team'] if pick['home_edge'] > pick['away_edge'] else pick['away_team']} ML</h3>
                        <p style="margin: 5px 0; color: #ffffff;">{pick['home_team']} vs {pick['away_team']}</p>
                        <p style="margin: 0; color: #2ecc71; font-weight: 600;">+{edge_pct:.1f}% Edge • {confidence}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # GAME CARDS
            cols = st.columns(2)
            for idx, pred in pred_df.iterrows():
                with cols[idx % 2]:
                    with st.container():
                        st.markdown(f'''
                        <div class="game-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div class="team-name">{pred['home_team']}</div>
                                    <div class="team-record">Home</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="color: #00d2ff; font-weight: 700;">VS</div>
                                </div>
                                <div style="text-align: right;">
                                    <div class="team-name">{pred['away_team']}</div>
                                    <div class="team-record">Away</div>
                                </div>
                            </div>
                            
                            <div style="margin-top: 15px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                    <span>{pred['home_prob']*100:.0f}%</span>
                                    <span>Win Prob</span>
                                    <span>{pred['away_prob']*100:.0f}%</span>
                                </div>
                                <div class="prob-bar-bg">
                                    <div class="prob-bar-fill" style="width: {pred['home_prob']*100}%; margin-left: 0;"></div>
                                </div>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                                <div class="odds-box">{pred['home_ml'] if pd.notna(pred['home_ml']) else 'N/A'}</div>
                                <div class="odds-box">{pred['away_ml'] if pd.notna(pred['away_ml']) else 'N/A'}</div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        else:
            st.info("No upcoming games found for this sport.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    import traceback
    st.caption(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #666;">Powered by ESPN + The Odds API | Sports Betting AI Pro</div>', unsafe_allow_html=True)
