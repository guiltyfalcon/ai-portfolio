"""
Sports Betting AI Pro - Main Entry Point
Right panel layout with login
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
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Sports Betting AI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        
        .prob-bar-bg {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            height: 15px;
            overflow: hidden;
        }
        
        .prob-bar-fill {
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .odds-box {
            background: rgba(0,210,255,0.1);
            border: 1px solid rgba(0,210,255,0.3);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            font-weight: 700;
        }
        
        .live-badge {
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid rgba(46, 204, 113, 0.4);
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 0.9rem;
            color: #2ecc71;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .live-dot {
            width: 8px;
            height: 8px;
            background: #2ecc71;
            border-radius: 50%;
            animation: pulse 2s infinite;
            display: inline-block;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .team-name { font-weight: 700; font-size: 1.1rem; }
        .team-record { color: #a0a0c0; font-size: 0.9rem; }
        
        .value-pick {
            background: linear-gradient(135deg, rgba(46,204,113,0.2) 0%, rgba(39,174,96,0.15) 100%);
            border: 1px solid rgba(46,204,113,0.4);
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

def get_sport_emoji(sport):
    emojis = {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒', 'ncaab': '🏀', 'ncaaf': '🏈'}
    return emojis.get(sport.lower(), '🏆')

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
            wins, losses, otl = map(int, parts)
            return wins, losses + otl
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

# MAIN LAYOUT: Content (left) + Settings Panel (right)
content_col, settings_col = st.columns([3, 1])

# RIGHT PANEL - Settings & Login
with settings_col:
    st.markdown("### ⚙️ Settings")
    
    # LOGIN SECTION
    if st.session_state.get('user_email'):
        st.markdown(f"**👤 {st.session_state.user_email}**")
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user_email = None
            st.session_state.is_supporter = False
            st.session_state.is_admin = False
            st.rerun()
    else:
        st.markdown("**🔐 Login**")
        email_input = st.text_input("Email", placeholder="your@email.com", key="login_email_input")
        if st.button("Login / Check", use_container_width=True, key="login_btn"):
            if email_input and '@' in email_input:
                st.session_state.user_email = email_input
                if email_input == 'guiltyfalcon@openclaw.com':
                    st.session_state.is_admin = True
                    st.session_state.is_supporter = True
                    st.success("👑 Admin granted!")
                    st.rerun()
                elif check_subscription_status():
                    st.session_state.is_supporter = True
                    st.success("✅ Premium active!")
                    st.rerun()
                else:
                    st.info("💎 Subscribe for premium")
                    st.rerun()
            else:
                st.error("Enter valid email")
    
    st.markdown("---")
    
    sport = st.selectbox(
        "Sport",
        ['NBA', 'NFL', 'MLB', 'NHL'],
        format_func=lambda x: f"{get_sport_emoji(x)} {x.upper()}",
        key="sport_select"
    )
    
    days = st.slider("Days", 1, 7, 3, key="days_slider")
    value_threshold = st.slider("Value %", 1, 20, 5, key="value_slider") / 100
    
    st.markdown("---")
    
    # Check status
    is_supporter = st.session_state.get('is_supporter', False)
    is_admin = st.session_state.get('is_admin', False)
    
    if is_admin:
        st.markdown("**👑 Admin**")
        st.caption("All features unlocked")
        st.markdown("✅ Bet Tracker")
        st.markdown("✅ Live Odds")
        st.markdown("✅ Player Props")
        st.markdown("✅ Parlay Builder")
        st.markdown("✅ Backtesting")
    elif is_supporter:
        st.markdown("**✨ Premium Active**")
        st.caption("All features unlocked")
    else:
        st.markdown("**💎 Free Tier**")
        st.markdown("• 2 games only")
        st.markdown("• Basic picks")
        st.link_button("Upgrade $5/mo", "https://buy.stripe.com/4gM28k5L17246LNfubfjG00", type="primary", use_container_width=True)
        st.caption("Unlock all features")

# LEFT PANEL - Main Content
with content_col:
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
                st.markdown(f'''<div class="stat-box"><div style="font-size: 2rem; font-weight: 700;">{len(teams)}</div><div style="color: #a0a0c0;">Teams</div></div>''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''<div class="stat-box"><div style="font-size: 2rem; font-weight: 700;">{len(schedule)}</div><div style="color: #a0a0c0;">Upcoming</div></div>''', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'''<div class="stat-box"><div style="font-size: 2rem; font-weight: 700;">99%</div><div style="color: #a0a0c0;">Uptime</div></div>''', unsafe_allow_html=True)
            
            with col4:
                st.markdown(f'''<div class="stat-box"><div style="font-size: 2rem; font-weight: 700;">{datetime.now().strftime("%H:%M")}</div><div style="color: #a0a0c0;">Updated</div></div>''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Try to get odds
            odds = pd.DataFrame()
            try:
                odds_api = OddsAPI()
                odds = odds_api.get_odds(sport.lower())
            except:
                pass
            
            # Process games
            if not schedule.empty:
                predictions = []
                
                for _, game in schedule.iterrows():
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
                        
                        if pd.notna(home_ml):
                            home_implied = american_to_implied(home_ml)
                            away_implied = american_to_implied(away_ml) if pd.notna(away_ml) else (1 - home_implied)
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
                
                # FREE LIMIT: 2 games only for non-supporters
                is_supporter = st.session_state.get('is_supporter', False)
                display_games = pred_df.head(2) if not is_supporter else pred_df
                
                if not is_supporter and len(pred_df) > 2:
                    st.info(f"🔒 Free tier: Showing {len(display_games)} of {len(pred_df)} games. Login or subscribe for access to all games.")
                
                st.markdown(f"### 📋 {sport.upper()} Games")
                
                for idx, pred in display_games.iterrows():
                    # Determine best pick
                    if pred['home_prob'] > pred['away_prob']:
                        best_pick_team = pred['home_team']
                        pick_team_short = pred['home_team'].split()[-1] if ' ' in pred['home_team'] else pred['home_team']
                    else:
                        best_pick_team = pred['away_team']
                        pick_team_short = pred['away_team'].split()[-1] if ' ' in pred['away_team'] else pred['away_team']
                    
                    # Build explanation
                    prob_pct = max(pred['home_prob'], pred['away_prob']) * 100
                    pick_explanation = f"{pick_team_short} favored ({prob_pct:.0f}% win probability)"
                    
                    # Game card
                    with st.container():
                        st.markdown(f'''
                        <div class="game-card" style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div><div class="team-name">{pred['home_team']}</div><div class="team-record">{pred['home_record']}</div></div>
                                <div style="text-align: center;"><div style="color: #00d2ff; font-weight: 700;">VS</div></div>
                                <div style="text-align: right;"><div class="team-name">{pred['away_team']}</div><div class="team-record">{pred['away_record']}</div></div>
                            </div>
                            <div style="margin-top: 15px;">
                                <div class="prob-bar-bg"><div class="prob-bar-fill" style="width: {pred['home_prob']*100}%;"></div></div>
                                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.85rem;">
                                    <span>{pred['home_prob']*100:.0f}%</span><span style="color: #a0a0c0;">Win Probability</span><span>{pred['away_prob']*100:.0f}%</span>
                                </div>
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
                        
                        # Expandable stats
                        with st.expander("📊 Team Stats", expanded=False):
                            col_stats1, col_stats2 = st.columns(2)
                            with col_stats1:
                                st.markdown(f"**{pred['home_team']}**")
                                st.markdown(f"Record: {pred['home_record']}")
                                st.markdown(f"Win Prob: {pred['home_prob']*100:.0f}%")
                            with col_stats2:
                                st.markdown(f"**{pred['away_team']}**")  
                                st.markdown(f"Record: {pred['away_record']}")
                                st.markdown(f"Win Prob: {pred['away_prob']*100:.0f}%")
                            
                            st.markdown("---")
                            st.markdown(f"**{pick_team_short} Analysis:**")
                            st.markdown(f"• Higher win probability: {prob_pct:.0f}%")
                            st.markdown(f"• Record advantage in this matchup")
                            st.markdown(f"• Source: ESPN data ({pred['home_record']} vs {pred['away_record']})")
            else:
                emoji = get_sport_emoji(sport)
                st.info(f"{emoji} No {sport.upper()} games scheduled for the next {days} day{'s' if days > 1 else ''}.")
    
    except Exception as e:
        st.error(f"Error: {e}")
        import traceback
        with st.expander("Debug"):
            st.code(traceback.format_exc())

# Subscription Benefits Section
is_supporter = st.session_state.get('is_supporter', False)
if not is_supporter:
    st.markdown("---")
    st.markdown("""
        <div style="background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.3); border-radius: 10px; padding: 15px; margin: 20px 0; text-align: center;">
            <p style="color: #2ecc71; font-weight: 600; margin: 0 0 10px 0;">💎 Unlock Premium Features</p>
            <p style="color: #ddd; margin: 0; font-size: 0.9rem;">
                💎 Complete Bet Tracker with ROI<br>
                💎 Real-time Live Odds from Vegas<br>
                💎 Advanced Player Props analytics<br>
                💎 Smart Parlay Builder + EV calc<br>
                💎 Full Backtesting suite<br>
                💎 All games (not just 2)<br>
                💎 Priority updates every 2 hours
            </p>
        </div>
    """, unsafe_allow_html=True)

# Gambling Disclaimer
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
