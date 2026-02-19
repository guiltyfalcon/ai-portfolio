import streamlit as st
import plotly.graph_objects as go
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.sports_data import (
    get_sports, get_teams, get_props, get_team_players, 
    get_player_stat, calculate_line, SPORT_CONFIG
)

st.set_page_config(page_title="Player Props 🎯", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .player-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px;
        margin: 10px 0; transition: all 0.3s ease;
    }
    .player-card:hover { border-color: rgba(255,107,107,0.3); }
    .hit-badge {
        background: linear-gradient(135deg, rgba(0,210,106,0.2), rgba(0,210,106,0.1));
        border: 1px solid rgba(0,210,106,0.4); color: #00d26a;
        padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;
    }
    .miss-badge {
        background: linear-gradient(135deg, rgba(255,71,87,0.2), rgba(255,71,87,0.1));
        border: 1px solid rgba(255,71,87,0.4); color: #ff4757;
        padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;
    }
    .prob-bar-bg {
        background: rgba(255,255,255,0.1); border-radius: 10px; height: 10px; overflow: hidden;
    }
    .prob-bar-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #ff6b6b, #feca57);
    }
    .sport-icon {
        font-size: 1.5rem; margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Player Props</div>', unsafe_allow_html=True)

# Show data source
st.caption("📊 Using 2025-26 season averages (NBA has live data option with nba-api package)")

# Sport selection
sports = get_sports()
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    sport = st.selectbox("Sport", sports, format_func=lambda x: {
        'NBA': '🏀 NBA', 'NFL': '🏈 NFL', 'MLB': '⚾ MLB', 'NHL': '🏒 NHL'
    }.get(x, x))

with col2:
    teams = get_teams(sport)
    selected_team = st.selectbox("Team", teams if teams else ["No teams available"])

with col3:
    props = get_props(sport)
    prop_type = st.selectbox("Prop", props if props else ["No props available"])

# Check if we have data
if not teams or not props or selected_team == "No teams available":
    st.warning(f"Player prop data not available for {sport} yet.")
    st.stop()

# Get players
players = get_team_players(sport, selected_team)

if not players:
    st.warning(f"No player data for {selected_team}")
    st.stop()

st.markdown(f"### 📊 {selected_team} Player Props - {prop_type}")

# Calculate and display for each player
for player in players:
    player_name = player.get('name', 'Unknown')
    
    # Get base stat
    base_stat = get_player_stat(player, prop_type, sport)
    
    # Calculate line
    line = calculate_line(base_stat, sport)
    
    # Calculate probability
    diff = base_stat - line
    variance_factor = max(2, base_stat * 0.15) if base_stat > 0 else 2
    over_prob = 0.5 + (diff / variance_factor)
    over_prob = min(0.90, max(0.10, over_prob))
    
    # Confidence
    confidence = "🔥 HIGH" if abs(over_prob - 0.5) > 0.2 else "⚡ MEDIUM" if abs(over_prob - 0.5) > 0.1 else "📊 LOW"
    
    # Recent performance simulation
    random.seed(hash(player_name + sport) % 1000)
    variance = variance_factor * 0.5
    last_5 = [base_stat + random.gauss(0, variance) for _ in range(5)]
    over_count = sum(1 for x in last_5 if x > line)
    
    # Create card
    with st.container():
        st.markdown(f'<div class="player-card">', unsafe_allow_html=True)
        
        cols = st.columns([3, 1, 1, 1, 1, 1])
        
        with cols[0]:
            st.markdown(f"**{player_name}**")
        
        with cols[1]:
            if sport == 'MLB' and prop_type == 'Hits':
                st.markdown(f"📊 {base_stat:.3f} avg")
            else:
                st.markdown(f"📊 {base_stat:.1f} avg")
        
        with cols[2]:
            st.markdown(f"📈 Line: {line:.1f}")
        
        with cols[3]:
            if over_prob > 0.6:
                st.markdown(f'<span class="hit-badge">{over_prob*100:.0f}% OVER</span>', unsafe_allow_html=True)
            elif over_prob < 0.4:
                st.markdown(f'<span class="miss-badge">{(1-over_prob)*100:.0f}% UNDER</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span style="color:#888;font-weight:600;">50/50</span>', unsafe_allow_html=True)
        
        with cols[4]:
            st.markdown(f"{confidence}")
        
        with cols[5]:
            st.markdown(f"📉 L5: {over_count}/5")
        
        # Probability bar
        st.markdown(f'''
            <div style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-bottom: 5px;">
                    <span>Under {(1-over_prob)*100:.0f}%</span>
                    <span>{sport} 2025-26</span>
                    <span>Over {over_prob*100:.0f}%</span>
                </div>
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill" style="width: {over_prob*100}%;"></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Sport-specific explanations
explanations = {
    'NBA': """
    **NBA Props:** Points, Rebounds, Assists, or combined (PRA)
    - Live data available via nba_api package
    - Lines set at ~95% of season average
    """,
    'NFL': """
    **NFL Props:** Pass Yards, Pass TDs, Rush Yards, Receptions, Rec Yards, Anytime TD
    - QB stats per game (passing yards, TDs)
    - Skill position stats (receptions, rushing)
    """,
    'MLB': """
    **MLB Props:** Hits (batting avg), Home Runs, RBIs, Total Bases
    - Per game averages
    - Hit props based on batting average
    """,
    'NHL': """
    **NHL Props:** Goals, Assists, Points, Shots on Goal
    - Per game averages
    - Points = Goals + Assists
    """
}

st.markdown(explanations.get(sport, ""))

st.markdown("""
### 📖 How Predictions Work

**Hit Probability:**
- Player average vs prop line
- Variance factor (consistency)
- Trend not yet included (future update)

**Confidence:**
- 🔥 HIGH: >20% edge
- ⚡ MEDIUM: 10-20% edge  
- 📊 LOW: <10% edge

**L5:** Record over/under vs this line in last 5 games (simulated)
""")

st.markdown("*Powered by ESPN (NBA via nba_api) | Static Data for NFL/MLB/NHL*")
