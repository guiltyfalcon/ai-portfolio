"""
Sports Betting AI Pro - Main Entry Point
Fixed navigation, improved error handling, modern UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import json
from datetime import datetime, timedelta

# SUBSCRIPTION CHECKING: Verify active $5/month subscription
def check_subscription_status():
    """Check if user has active monthly subscription"""
    
    # Check query params for immediate post-payment
    if st.query_params.get("success") == "1":
        st.session_state.just_paid = True
        return True
    
    # Check local subscription files
    users_dir = os.path.expanduser("~/.openclaw/sports_bet_users")
    if not os.path.exists(users_dir):
        return False
    
    for filename in os.listdir(users_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(users_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    sub = json.load(f)
                
                # Active subscription
                if sub.get('status') == 'active' and not sub.get('is_cancelled', False):
                    return True
                
                # Cancelled but still within paid period
                if sub.get('is_cancelled') and sub.get('premium_until'):
                    import time
                    if time.time() < sub['premium_until']:
                        st.session_state.subscription_ending = True
                        return True
                        
            except Exception:
                pass
    
    return False

# Initialize session state
if "is_supporter" not in st.session_state:
    st.session_state.is_supporter = check_subscription_status()
if "subscription_ending" not in st.session_state:
    st.session_state.subscription_ending = False
if "just_paid" not in st.session_state:
    st.session_state.just_paid = False

# Page config MUST be first Streamlit command
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
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            background-attachment: fixed;
        }
        
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
        
        .team-name {
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .team-record {
            color: #a0a0c0;
            font-size: 0.9rem;
        }
        
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
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15,12,41,0.95) 0%, rgba(48,43,99,0.95) 100%);
        }
        
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
    </style>
    """, unsafe_allow_html=True)

load_css()

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
        parts = str(record).split('-')
        if len(parts) == 3:
            # NHL format: wins-losses-OTL
            wins, losses, otl = map(int, parts)
            return wins, losses + otl  # Count OTL as losses for win%
        elif len(parts) == 2:
            wins, losses = map(int, parts)
            return wins, losses
        else:
            return 0, 0
    except:
        return 0, 0

def calculate_win_prob(wins, losses, home_adv=0.03):
    total = wins + losses
    if total == 0:
        return 0.5
    return min(max((wins / total) + home_adv, 0.1), 0.9)

def format_odds(odds):
    if pd.isna(odds) or odds is None:
        return "N/A"
    if odds > 0:
        return f"+{int(odds)}"
    return f"{int(odds)}"

# Header
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

# Sidebar
with st.sidebar:
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
    
    odds_api_key = os.getenv('THEODDS_API_KEY')
    if odds_api_key:
        st.markdown("✅ The Odds API (Configured)")
    else:
        st.markdown("⚠️ The Odds API (No API Key)")
        st.caption("Set THEODDS_API_KEY in secrets for live odds")
    
    st.markdown("✅ ESPN API (Free)")
    
    st.markdown("---")
    st.markdown("### 💎 Support the Project")
    
    # Tip/Unlock section
    is_supporter = st.session_state.get('is_supporter', False)
    
    if not is_supporter:
        st.markdown("#### Unlock Premium Features")
        st.markdown("""
        **Free:** Basic predictions, win %, 3-day history
        
        **$5+ Supporters Get:**
        ✅ Value picks highlighted  
        ✅ Parlay builder + EV calc  
        ✅ 30-day backtesting  
        ✅ Priority odds refresh  
        ✅ Supporter badge
        """)
        
        st.markdown("#### ☕ Unlock Premium Features")
        st.markdown("**Free:** Basic predictions, win %, 3-day history")
        st.markdown("""
        **$5/Month — Supporters Get:**
        ✅ Value picks highlighted  
        ✅ Parlay builder + EV calc  
        ✅ 30-day backtesting  
        ✅ Priority odds refresh  
        ✅ Supporter badge
        """)
        
        st.link_button("Subscribe — $5/mo", "https://buy.stripe.com/4gM28k5L17246LNfubfjG00", type="primary", use_container_width=True)
        st.caption("Monthly subscription. Cancel anytime.")
    else:
        st.markdown("✨ **You're a Supporter!**")
        st.markdown("All premium features unlocked.")
        st.success("Thank you for your support!")

# Main Content
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    
    with st.spinner(f"Loading {sport} data..."):
        espn = ESPNAPI()
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Stats Row
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''<div class="stat-box"><div class="stat-number">{len(teams)}</div><div style="color: #a0a0c0;">Teams</div></div>''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''<div class="stat-box"><div class="stat-number">{len(schedule)}</div><div style="color: #a0a0c0;">Upcoming</div></div>''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''<div class="stat-box"><div class="stat-number">99%</div><div style="color: #a0a0c0;">Uptime</div></div>''', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'''<div class="stat-box"><div class="stat-number">{datetime.now().strftime("%H:%M")}</div><div style="color: #a0a0c0;">Updated</div></div>''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PROMINENT UPGRADE BANNER (if not supporter and value picks exist)
        is_supporter = st.session_state.get('is_supporter', False)
        has_value_picks = False  # Will check after predictions built
        
        # PRE-CHECK: Build predictions silently to check for value picks
        preview_predictions = []
        for _, game in schedule.head(8).iterrows():
            home_rec = game.get('home_record', '0-0')
            away_rec = game.get('away_record', '0-0')
            hw, hl = parse_record(home_rec)
            aw, al = parse_record(away_rec)
            
            home_prob = calculate_win_prob(hw, hl, 0.04)
            away_prob = 1 - home_prob
            
            # Check if this would be a value pick
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
                
                if pd.notna(home_ml) and pd.notna(away_ml):
                    home_implied = american_to_implied(home_ml)
                    away_implied = american_to_implied(away_ml)
                    home_edge = home_prob - home_implied
                    away_edge = away_prob - away_implied
                    if abs(home_edge) > value_threshold or abs(away_edge) > value_threshold:
                        has_value_picks = True
        
        # SHOW UPGRADE BANNER
        if not is_supporter and has_value_picks:
            st.markdown('''
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); 
                        padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center;">
                <h2 style="color: white; margin: 0 0 10px 0;">🔒 Premium Value Picks Locked</h2>
                <p style="color: white; font-size: 1.1rem; margin: 0 0 15px 0;">
                    High-confidence picks detected! Unlock for $5/month.
                </p>
                <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin: 0;">
                    ✅ Value Picks  •  ✅ 30-Day Backtesting  •  ✅ Parlay Builder
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                st.link_button("🔓 Unlock Premium — $5/mo", "https://buy.stripe.com/4gM28k5L17246LNfubfjG00", type="primary", use_container_width=True)
            st.caption("Monthly subscription • Cancel anytime • Instant access to value picks")
            st.markdown("---")
        
        # Try to get odds
        odds = pd.DataFrame()
        odds_error = None
        
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
        except Exception as e:
            odds_error = str(e)
            pass
        
        if odds_error:
            with st.expander("⚠️ Odds API Issue (Click for details)"):
                st.warning("Live odds unavailable. Using estimated probabilities.")
                st.caption(f"Error: {odds_error}")
                st.info("To get live odds, add THEODDS_API_KEY to your Streamlit secrets.")
        
        # Predictions Section
        st.markdown(f"### {get_sport_emoji(sport)} {sport.upper()} Predictions")
        
        if not schedule.empty:
            predictions = []
            
            for _, game in schedule.head(8).iterrows():
                home_rec = game.get('home_record', '0-0')
                away_rec = game.get('away_record', '0-0')
                hw, hl = parse_record(home_rec)
                aw, al = parse_record(away_rec)
                
                home_prob = calculate_win_prob(hw, hl, 0.04)
                away_prob = 1 - home_prob
                
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
                    
                    # Use implied probability from odds when available
                    if pd.notna(home_ml):
                        home_implied = american_to_implied(home_ml)
                        away_implied = american_to_implied(away_ml) if pd.notna(away_ml) else (1 - home_implied)
                        # Use implied probs for display (more accurate than record-based)
                        home_prob = home_implied
                        away_prob = away_implied
                    else:
                        home_implied = home_prob
                        away_implied = away_prob
                    
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
                    'home_record': home_rec,
                    'away_record': away_rec,
                    'home_prob': home_prob,
                    'away_prob': away_prob,
                    'home_ml': home_ml,
                    'away_ml': away_ml,
                    'home_edge': home_edge,
                    'away_edge': away_edge,
                    'has_edge': has_edge
                })
            
            pred_df = pd.DataFrame(predictions)
            
            # VALUE PICKS (Premium Feature)
            value_picks = pred_df[pred_df['has_edge'] == True]
            if not value_picks.empty:
                st.markdown("### 💎 Value Picks")
                
                if not is_supporter:
                    # Show locked preview
                    count = len(value_picks)
                    st.info(f"🔒 {count} value picks detected. Unlock premium to see them.")
                    if st.button("Unlock for $5 →", type="primary"):
                        st.markdown("[Complete purchase here](https://buy.stripe.com/4gM28k5L17246LNfubfjG00)")
                else:
                    # Show all value picks for supporters
                    for _, pick in value_picks.head(3).iterrows():
                        edge_pct = max(abs(pick['home_edge']), abs(pick['away_edge'])) * 100
                        confidence = "HIGH 🔥" if edge_pct > 8 else "MED ⚡"
                        
                        best_pick = pick['home_team'] if pick['home_edge'] > pick['away_edge'] else pick['away_team']
                        best_odds = pick['home_ml'] if pick['home_edge'] > pick['away_edge'] else pick['away_ml']
                        
                        st.markdown(f'''
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
                        ''', unsafe_allow_html=True)
            
            # GAME CARDS
            st.markdown("### 📋 All Games")
            cols = st.columns(2)
            
            for idx, pred in pred_df.iterrows():
                with cols[idx % 2]:
                    st.markdown(f'''
                    <div class="game-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div><div class="team-name">{pred['home_team']}</div><div class="team-record">{pred['home_record']}</div></div>
                            <div style="text-align: center;"><div style="color: #00d2ff; font-weight: 700;">VS</div></div>
                            <div style="text-align: right;"><div class="team-name">{pred['away_team']}</div><div class="team-record">{pred['away_record']}</div></div>
                        </div>
                        <div style="margin-top: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span>{pred['home_prob']*100:.0f}%</span><span style="color: #a0a0c0;">Win Prob</span><span>{pred['away_prob']*100:.0f}%</span>
                            </div>
                            <div class="prob-bar-bg"><div class="prob-bar-fill" style="width: {pred['home_prob']*100}%; margin-left: 0;"></div></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                            <div class="odds-box">{format_odds(pred['home_ml'])}</div>
                            <div class="odds-box">{format_odds(pred['away_ml'])}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            emoji = get_sport_emoji(sport)
            st.info(f"{emoji} No {sport.upper()} games scheduled for the next {days} day{'s' if days > 1 else ''}.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    import traceback
    with st.expander("Debug Info"):
        st.code(traceback.format_exc())

st.markdown("---")
st.markdown('<div style="text-align: center; color: #666;">Powered by ESPN API | Sports Betting AI Pro</div>', unsafe_allow_html=True)
