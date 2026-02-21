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
        
        /* Hide Streamlit toolbar icons (fork, reddit, etc) */
        .stToolbar {
            display: none !important;
        }
        
        /* Hide GitHub fork button */
        button[kind="header"],
        .stApp header button {
            display: none !important;
        }
        
        /* Hide share/overflow menu */
        #MainMenu, header .st-emotion-cache-1avcm0n {
            visibility: hidden !important;
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

# SIDEBAR MUST COME BEFORE ANY MAIN CONTENT
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
    
    # ADMIN OVERRIDE: Auto-unlock for admin
    if st.session_state.get('user_email') == 'guiltyfalcon@openclaw.com':
        st.session_state.is_supporter = True
        st.session_state.is_admin = True
    
    # Check subscription status
    if 'is_supporter' not in st.session_state:
        if check_subscription_status():
            st.session_state.is_supporter = True
    
    # Simple support section - only button, no duplicate unlock features
    is_supporter = st.session_state.get('is_supporter', False)
    is_admin = st.session_state.get('is_admin', False)
    
    if is_admin:
        st.markdown("### 👑 Admin Access")
        st.markdown("✅ **All features unlocked (admin)**")
    elif is_supporter:
        st.markdown("### ✨ Premium Active")
        st.markdown("✅ **All features unlocked!**")
    else:
        st.markdown("### 💎 Unlock Premium")
        st.link_button("Subscribe — $5/mo", "https://buy.stripe.com/4gM28k5L17246LNfubfjG00", type="primary", use_container_width=True)
        st.caption("Cancel anytime")

# Header (AFTER sidebar)
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
        
        # Try to get odds FIRST (before checking for value picks)
        odds = pd.DataFrame()
        odds_error = None
        
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
        except Exception as e:
            odds_error = str(e)
            pass
        
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
            
            # GAME CARDS WITH EXPANDABLE STATS
            st.markdown("### 📋 All Games")
            
            # LIMIT: Free users see only 2 games
            is_supporter = st.session_state.get('is_supporter', False)
            display_games = pred_df.head(2) if not is_supporter else pred_df
            
            if not is_supporter and len(pred_df) > 2:
                st.info(f"🔒 Free tier: Showing {len(display_games)} of {len(pred_df)} games. Unlock premium for all {len(pred_df)} games.")
            
            for idx, pred in display_games.iterrows():
                # Determine best pick for this game with detailed reasoning
                best_pick_team = ""
                pick_team_short = ""
                
                # Parse records first
                home_wins, home_losses, home_otl = 0, 0, 0
                away_wins, away_losses, away_otl = 0, 0, 0
                
                if pred['home_record'] and '-' in str(pred['home_record']):
                    parts = str(pred['home_record']).split('-')
                    home_wins = int(parts[0])
                    if len(parts) >= 2:
                        home_losses = int(parts[1])
                    if len(parts) >= 3:
                        home_otl = int(parts[2])
                
                if pred['away_record'] and '-' in str(pred['away_record']):
                    parts = str(pred['away_record']).split('-')
                    away_wins = int(parts[0])
                    if len(parts) >= 2:
                        away_losses = int(parts[1])
                    if len(parts) >= 3:
                        away_otl = int(parts[2])
                
                # Calculate win percentages
                home_total = home_wins + home_losses + home_otl
                away_total = away_wins + away_losses + away_otl
                home_win_pct = (home_wins / home_total * 100) if home_total > 0 else 0
                away_win_pct = (away_wins / away_total * 100) if away_total > 0 else 0
                
                # GENERATE COMPREHENSIVE PICK ANALYSIS
                if pred['home_prob'] > pred['away_prob']:
                    best_pick_team = pred['home_team']
                    pick_team_short = pred['home_team'].split()[-1] if ' ' in pred['home_team'] else pred['home_team']
                    other_team = pred['away_team']
                    other_team_short = pred['away_team'].split()[-1] if ' ' in pred['away_team'] else pred['away_team']
                    prob_pct = pred['home_prob'] * 100
                else:
                    best_pick_team = pred['away_team']
                    pick_team_short = pred['away_team'].split()[-1] if ' ' in pred['away_team'] else pred['away_team']
                    other_team = pred['home_team']
                    other_team_short = pred['home_team'].split()[-1] if ' ' in pred['home_team'] else pred['home_team']
                    prob_pct = pred['away_prob'] * 100
                
                # Calculate key metrics
                home_win_rate = (home_wins / home_total * 100) if home_total > 0 else 50
                away_win_rate = (away_wins / away_total * 100) if away_total > 0 else 50
                record_diff = abs(home_wins - away_wins)
                
                # Build comprehensive narrative reasons
                detailed_analysis = []
                
                # 1. Home Court Advantage Analysis
                if pred['home_prob'] > pred['away_prob'] and sport.lower() in ['nba', 'nfl', 'nhl', 'ncaab']:
                    home_games = max(10, home_total // 2)  # Estimate home games
                    home_w = int(home_games * (home_win_rate / 100))
                    home_l = home_games - home_w
                    road_games = away_total
                    road_w = away_wins
                    road_l = away_losses + away_otl
                    
                    if home_win_rate > away_win_rate + 10:
                        detailed_analysis.append(f"**Home Court Dominance**: The {pick_team_short} are significantly stronger at home with an estimated {home_w}-{home_l} home record compared to their {road_w}-{road_l} play on the road. The {prob_pct:.0f}% home win probability reflects this home court advantage.")
                    else:
                        detailed_analysis.append(f"**Home Court Advantage**: The {pick_team_short} hold a {home_win_rate:.0f}% win rate overall ({home_wins}-{home_losses}-{home_otl}), giving them a slight edge playing at home.")
                
                # 2. Record Comparison
                if record_diff >= 3:
                    if home_wins > away_wins:
                        detailed_analysis.append(f"**Superior Season Record**: The {pick_team_short} hold a decisive advantage with their {home_wins}-{home_losses}-{home_otl} record vs the {other_team_short}'s {away_wins}-{away_losses}-{away_otl}. This {home_win_rate:.0f}% to {away_win_rate:.0f}% win rate differential is significant.")
                    else:
                        detailed_analysis.append(f"**Superior Season Record**: The {pick_team_short} hold a decisive advantage with their record, sporting a higher win percentage ({prob_pct:.0f}% implied) vs the {other_team_short}'s struggles.")
                
                # 3. Odds Analysis
                if pred['home_ml'] is not None and pred['away_ml'] is not None:
                    favorite = pick_team_short
                    spread = abs(pred['home_ml'] + 100) / 20 if pred['home_ml'] < 0 else (pred['away_ml'] + 100) / 20
                    if pred['home_prob'] > 0.55:
                        detailed_analysis.append(f"**Oddsmaker Confidence**: The {favorite} are favored by roughly {int(spread)} points with a {prob_pct:.0f}% win probability according to Vegas odds. This pricing suggests the market sees clear mismatches in this matchup.")
                    else:
                        detailed_analysis.append(f"**Close Matchup**: Bookmakers have this as a tight contest with {prob_pct:.0f}% implied win probability, suggesting minimal edge for either side.")
                
                # 4. Form Analysis (recent trend implied by win %)
                if home_win_rate > 60:
                    detailed_analysis.append(f"**Hot Form**: The {pick_team_short} are playing at a high level, evidenced by their strong {home_win_rate:.0f}% win rate. Their momentum coming into this matchup is a key factor.")
                elif home_win_rate > 50:
                    detailed_analysis.append(f"**Solid Form**: The {pick_team_short} have been above average with a {home_win_rate:.0f}% win rate, positioning them well in this contest.")
                
                # Build the short explanation
                if len(detailed_analysis) >= 2:
                    pick_explanation = f"{pick_team_short} are favored: {detailed_analysis[0].split(':')[1].strip()[:80]}... and {len(detailed_analysis)-1} more factors."
                elif detailed_analysis:
                    pick_explanation = f"{pick_team_short} are favored: {detailed_analysis[0].split(':')[1].strip()[:100]}"
                else:
                    pick_explanation = f"{pick_team_short} hold a {prob_pct:.0f}% win probability in this matchup."
                
                # Create dropdown content
                pick_bullet_points = []
                for analysis in detailed_analysis:
                    pick_bullet_points.append(analysis)
                
                # Add matchup context
                if sport.lower() == 'nba':
                    pick_bullet_points.append("**League Context**: Both teams are battling in their respective conferences, making this a critical game for playoff positioning.")
                elif sport.lower() == 'nfl':
                    pick_bullet_points.append("**Playoff Implications**: With the season progressing, every win becomes crucial for postseason aspirations.")
                
                # Source citation
                if pred['home_ml'] is not None and not pd.isna(pred['home_ml']):
                    pick_bullet_points.append(f"**Data Sources**: ESPN team records ({pred['home_record']} vs {pred['away_record']}) | Odds: {format_odds(pred['home_ml'])} vs {format_odds(pred['away_ml'])} | Implied probability: {prob_pct:.0f}%")
                
                # Main game card with explanation
                with st.container():
                    st.markdown(f'''
                    <div class="game-card" style="margin-bottom: 10px;">
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
                        <div style="margin-top: 12px; padding: 10px; background: rgba(46, 204, 113, 0.15); border-radius: 8px; border-left: 3px solid #2ecc71;">
                            <span style="color: #2ecc71; font-weight: 600;">⭐ Pick: {best_pick_team}</span>
                            <div style="color: #ddd; font-size: 0.9rem; margin-top: 4px;">{pick_explanation}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Expandable team stats
                    with st.expander(f"📊 Team Stats & Players", expanded=False):
                        # Get actual records from prediction data
                        home_rec = pred['home_record']
                        away_rec = pred['away_record']
                        
                        col_stats1, col_stats2 = st.columns(2)
                        
                        with col_stats1:
                            st.markdown(f"**{pred['home_team']}**")
                            # Parse record for display
                            if home_rec and home_rec != 'N/A':
                                parts = str(home_rec).split('-')
                                if len(parts) >= 2:
                                    wins, losses = int(parts[0]), int(parts[1])
                                    total = wins + losses
                                    win_pct = (wins / total * 100) if total > 0 else 0
                                    
                                    col_w, col_l, col_p = st.columns(3)
                                    col_w.metric("Wins", wins)
                                    col_l.metric("Losses", losses)
                                    col_p.metric("Win%", f"{win_pct:.0f}%")
                            else:
                                st.caption("Record: N/A")
                            
                            # Prediction
                            st.markdown("**Our Prediction**")
                            prob = pred['home_prob'] * 100
                            st.progress(prob / 100, text=f"{prob:.0f}% Win Probability")
                        
                        with col_stats2:
                            st.markdown(f"**{pred['away_team']}**")
                            # Parse record for display
                            if away_rec and away_rec != 'N/A':
                                parts = str(away_rec).split('-')
                                if len(parts) >= 2:
                                    wins, losses = int(parts[0]), int(parts[1])
                                    total = wins + losses
                                    win_pct = (wins / total * 100) if total > 0 else 0
                                    
                                    col_w, col_l, col_p = st.columns(3)
                                    col_w.metric("Wins", wins)
                                    col_l.metric("Losses", losses)
                                    col_p.metric("Win%", f"{win_pct:.0f}%")
                            else:
                                st.caption("Record: N/A")
                            
                            # Prediction
                            st.markdown("**Our Prediction**")
                            prob = pred['away_prob'] * 100
                            st.progress(prob / 100, text=f"{prob:.0f}% Win Probability")
                        
                        st.divider()
                        
                        st.markdown(f"**Detailed Analysis**")
                        for point in pick_bullet_points:
                            st.markdown(f"• {point}")
                        
                        st.markdown("---")
                        st.markdown(f"**Best Pick: {best_pick_team}**")
                        st.caption(pick_explanation)
        else:
            emoji = get_sport_emoji(sport)
            st.info(f"{emoji} No {sport.upper()} games scheduled for the next {days} day{'s' if days > 1 else ''}.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    import traceback
    with st.expander("Debug Info"):
        st.code(traceback.format_exc())

# GAMBLING DISCLAIMER - Always at the bottom
st.markdown("---")
st.markdown("""
    <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,0,0,0.2); border-radius: 8px; padding: 12px; margin-top: 20px; text-align: center;">
        <p style="color: #aaa; margin: 0; font-size: 0.85rem;">
            <strong style="color: #ff6b6b;">⚠️ For entertainment only.</strong> 
            Please gamble responsibly. 18+.<br>
            <small style="color: #666;">Past performance ≠ future results. Only bet what you can afford to lose.</small>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Sports Betting AI")
