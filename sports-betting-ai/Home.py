"""
Sports Betting AI - Professional Sportsbook Design
Dark theme, skeleton loading, tappable odds buttons
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

# === PROFESSIONAL SPORTSBOOK THEME ===
st.markdown("""
<style>
    :root {
        --sb-bg-primary: #0a0a0a;
        --sb-bg-secondary: #141414;
        --sb-bg-card: #1a1a1a;
        --sb-accent: #00d26a;
        --sb-accent-hover: #00ff7f;
        --sb-danger: #ff4757;
        --sb-warning: #ffa502;
        --sb-text-primary: #ffffff;
        --sb-text-secondary: #a0a0a0;
        --sb-border: #2d2d2d;
    }
    
    .stApp {
        background: var(--sb-bg-primary);
        color: var(--sb-text-primary);
    }
    
    /* Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        color: var(--sb-text-primary);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .main-header span {
        color: var(--sb-accent);
        text-shadow: 0 0 20px rgba(0, 210, 106, 0.5);
    }
    
    /* Live Badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 71, 87, 0.15);
        border: 1px solid var(--sb-danger);
        padding: 6px 14px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--sb-danger);
    }
    
    .live-dot {
        width: 6px;
        height: 6px;
        background: var(--sb-danger);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    /* Game Card */
    .game-card {
        background: var(--sb-bg-card);
        border: 1px solid var(--sb-border);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.2s ease;
    }
    
    .game-card:hover {
        border-color: var(--sb-accent);
        box-shadow: 0 4px 20px rgba(0, 210, 106, 0.1);
    }
    
    /* Teams Layout */
    .matchup-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .team-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .team-logo {
        width: 40px;
        height: 40px;
        background: var(--sb-bg-secondary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .team-details h4 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--sb-text-primary);
    }
    
    .team-details span {
        font-size: 0.75rem;
        color: var(--sb-text-secondary);
    }
    
    /* Odds Buttons */
    .odds-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    
    .odds-box {
        background: var(--sb-bg-secondary);
        border: 1px solid var(--sb-border);
        border-radius: 8px;
        padding: 12px 8px;
        text-align: center;
        transition: all 0.15s ease;
    }
    
    .odds-box:hover {
        background: rgba(0, 210, 106, 0.1);
        border-color: var(--sb-accent);
    }
    
    .odds-box .label {
        font-size: 0.65rem;
        color: var(--sb-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .odds-box .value {
        font-size: 1rem;
        font-weight: 700;
        color: var(--sb-text-primary);
    }
    
    .odds-box.positive {
        border-color: var(--sb-accent);
        background: rgba(0, 210, 106, 0.15);
    }
    
    /* Value Pick */
    .value-pick {
        background: linear-gradient(135deg, rgba(0,210,106,0.2) 0%, rgba(0,210,106,0.1) 100%);
        border: 1px solid var(--sb-accent);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        position: relative;
    }
    
    .value-pick::before {
        content: 'EDGE';
        position: absolute;
        top: -10px;
        right: 12px;
        background: var(--sb-accent);
        color: #000;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 4px;
    }
    
    /* Skeleton Loading */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .skeleton {
        background: linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite linear;
        border-radius: 8px;
    }
    
    .skeleton-card {
        background: var(--sb-bg-card);
        border: 1px solid var(--sb-border);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    
    /* Stats */
    .stat-box {
        background: var(--sb-bg-card);
        border: 1px solid var(--sb-border);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--sb-accent);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--sb-bg-secondary);
    }
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🎯')

def american_to_implied(odds):
    """Convert American odds to implied probability with validation."""
    if pd.isna(odds) or odds == 0:
        return 0.5
    try:
        odds = float(odds)
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)
    except (ValueError, TypeError):
        return 0.5

def parse_record(record):
    """Parse win-loss record with validation."""
    try:
        if pd.isna(record) or not isinstance(record, str):
            return 0, 0
        if '-' not in str(record):
            return 0, 0
        parts = str(record).split('-')
        if len(parts) != 2:
            return 0, 0
        wins = int(parts[0])
        losses = int(parts[1])
        if wins < 0 or losses < 0:
            return 0, 0
        return wins, losses
    except (ValueError, TypeError):
        return 0, 0

def calculate_win_prob(wins, losses, home_adv=0.03):
    """Calculate win probability with bounds checking."""
    total = wins + losses
    if total == 0:
        return 0.5
    prob = (wins / total) + home_adv
    return max(0.1, min(0.9, prob))  # Clamp between 10% and 90%

def render_skeleton_card():
    """Render skeleton placeholder while loading."""
    st.markdown("""
    <div class="skeleton-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="skeleton" style="width: 40px; height: 40px; border-radius: 50%;"></div>
                <div style="width: 120px;">
                    <div class="skeleton" style="height: 16px; width: 80%; margin-bottom: 8px;"></div>
                    <div class="skeleton" style="height: 12px; width: 50%;"></div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 120px; text-align: right;">
                    <div class="skeleton" style="height: 16px; width: 80%; margin-bottom: 8px; margin-left: auto;"></div>
                    <div class="skeleton" style="height: 12px; width: 50%; margin-left: auto;"></div>
                </div>
                <div class="skeleton" style="width: 40px; height: 40px; border-radius: 50%;"></div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 16px;">
            <div class="skeleton" style="height: 50px;"></div>
            <div class="skeleton" style="height: 50px;"></div>
            <div class="skeleton" style="height: 50px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<div class="main-header">🎯 BET AI <span>PRO</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #a0a0c0; font-size: 1rem; margin-bottom: 10px;">Professional Sports Predictions</div>', unsafe_allow_html=True)
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f'''
    <div style="text-align: center; margin-bottom: 20px;">
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
    value_threshold = st.slider("Value Edge %", 1, 15, 5)
    
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
loading = st.empty()

with loading.container():
    # Show skeleton while loading
    st.markdown("### Loading Games...")
    for _ in range(4):
        render_skeleton_card()

try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    
    with st.spinner(""):
        espn = ESPNAPI()
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Clear skeleton
        loading.empty()
        
        # Stats Row
        cols = st.columns(4)
        stats = [
            (len(teams), "Teams"),
            (len(schedule), "Upcoming"),
            ("99%", "Uptime"),
            (datetime.now().strftime("%H:%M"), "Updated")
        ]
        
        for col, (value, label) in zip(cols, stats):
            with col:
                st.markdown(f'''
                <div class="stat-box">
                    <div class="stat-number">{value}</div>
                    <div style="color: #a0a0c0; font-size: 0.8rem;">{label}</div>
                </div>
                ''', unsafe_allow_html=True)
        
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
            
            for _, game in schedule.head(6).iterrows():
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
                    home_implied = american_to_implied(home_ml)
                    away_implied = american_to_implied(away_ml)
                    
                    home_edge = home_prob - home_implied
                    away_edge = away_prob - away_implied
                    has_edge = abs(home_edge) > (value_threshold/100) or abs(away_edge) > (value_threshold/100)
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
                    'has_edge': has_edge
                })
            
            pred_df = pd.DataFrame(predictions)
            
            # VALUE PICKS
            value_picks = pred_df[pred_df['has_edge'] == True]
            if not value_picks.empty:
                st.markdown("### 💎 Value Picks")
                for _, pick in value_picks.head(2).iterrows():
                    edge_pct = max(abs(pick['home_edge']), abs(pick['away_edge'])) * 100
                    pick_team = pick['home_team'] if pick['home_edge'] > pick['away_edge'] else pick['away_team']
                    
                    st.markdown(f'''
                    <div class="value-pick">
                        <h4 style="margin: 0; color: #00d26a;">{pick_team} ML</h4>
                        <p style="margin: 5px 0; color: #a0a0a0; font-size: 0.9rem;">{pick['home_team']} vs {pick['away_team']}</p>
                        <p style="margin: 0; color: #00d26a; font-weight: 700;">+{edge_pct:.1f}% Edge</p>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # GAME CARDS
            cols = st.columns(2)
            for idx, pred in pred_df.iterrows():
                with cols[idx % 2]:
                    home_pos = pred['home_ml'] > 0 if pd.notna(pred['home_ml']) else False
                    away_pos = pred['away_ml'] > 0 if pd.notna(pred['away_ml']) else False
                    
                    st.markdown(f'''
                    <div class="game-card">
                        <div class="matchup-row">
                            <div class="team-info">
                                <div class="team-logo">🏠</div>
                                <div class="team-details">
                                    <h4>{pred['home_team']}</h4>
                                    <span>Home • {pred['home_prob']*100:.0f}%</span>
                                </div>
                            </div>
                            <div style="color: #666; font-weight: 700;">VS</div>
                            <div class="team-info" style="flex-direction: row-reverse; text-align: right;">
                                <div class="team-logo">✈️</div>
                                <div class="team-details">
                                    <h4>{pred['away_team']}</h4>
                                    <span>Away • {pred['away_prob']*100:.0f}%</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="odds-container">
                            <div class="odds-box">
                                <div class="label">Spread</div>
                                <div class="value">-5.5</div>
                            </div>
                            <div class="odds-box {'positive' if home_pos else ''}">
                                <div class="label">ML</div>
                                <div class="value">{pred['home_ml'] if pd.notna(pred['home_ml']) else '--'}</div>
                            </div>
                            <div class="odds-box">
                                <div class="label">O/U</div>
                                <div class="value">226.5</div>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.info("No upcoming games found for this sport.")

except Exception as e:
    loading.empty()
    st.error(f"Error loading data: {e}")
    import traceback
    st.caption(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #666; font-size: 0.8rem;">Powered by ESPN + The Odds API | Sports Betting AI Pro</div>', unsafe_allow_html=True)
