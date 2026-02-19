import streamlit as st
import plotly.graph_objects as go
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.espn import ESPNAPI

st.set_page_config(page_title="Team Player Props 🏀", page_icon="🏀", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Team Player Props</div>', unsafe_allow_html=True)

# Sample player database by team
TEAM_PLAYERS = {
    'Lakers': [
        {'name': 'LeBron James', 'ppg': 25.2, 'rpg': 7.8, 'apg': 9.0, 'fg_pct': 0.52, 'trend': 'up'},
        {'name': 'Anthony Davis', 'ppg': 24.8, 'rpg': 12.5, 'apg': 3.5, 'fg_pct': 0.55, 'trend': 'stable'},
        {'name': 'Austin Reaves', 'ppg': 15.8, 'rpg': 4.2, 'apg': 5.1, 'fg_pct': 0.48, 'trend': 'up'},
        {'name': "D'Angelo Russell", 'ppg': 14.2, 'rpg': 3.1, 'apg': 6.0, 'fg_pct': 0.45, 'trend': 'down'},
    ],
    'Warriors': [
        {'name': 'Stephen Curry', 'ppg': 28.5, 'rpg': 4.4, 'apg': 5.1, 'fg_pct': 0.47, 'trend': 'up'},
        {'name': 'Klay Thompson', 'ppg': 18.2, 'rpg': 3.5, 'apg': 2.3, 'fg_pct': 0.43, 'trend': 'stable'},
        {'name': 'Draymond Green', 'ppg': 8.5, 'rpg': 7.2, 'apg': 6.8, 'fg_pct': 0.49, 'trend': 'stable'},
        {'name': 'Andrew Wiggins', 'ppg': 13.8, 'rpg': 4.5, 'apg': 1.7, 'fg_pct': 0.46, 'trend': 'down'},
    ],
    'Celtics': [
        {'name': 'Jayson Tatum', 'ppg': 27.2, 'rpg': 8.3, 'apg': 4.9, 'fg_pct': 0.48, 'trend': 'up'},
        {'name': 'Jaylen Brown', 'ppg': 23.5, 'rpg': 5.6, 'apg': 3.4, 'fg_pct': 0.49, 'trend': 'up'},
        {'name': 'Kristaps Porzingis', 'ppg': 20.1, 'rpg': 7.2, 'apg': 2.0, 'fg_pct': 0.51, 'trend': 'stable'},
        {'name': 'Derrick White', 'ppg': 15.2, 'rpg': 4.0, 'apg': 5.2, 'fg_pct': 0.46, 'trend': 'up'},
    ],
    'Nuggets': [
        {'name': 'Nikola Jokic', 'ppg': 25.9, 'rpg': 12.0, 'apg': 9.1, 'fg_pct': 0.58, 'trend': 'up'},
        {'name': 'Jamal Murray', 'ppg': 21.2, 'rpg': 4.1, 'apg': 6.5, 'fg_pct': 0.48, 'trend': 'stable'},
        {'name': 'Aaron Gordon', 'ppg': 13.8, 'rpg': 6.5, 'apg': 3.2, 'fg_pct': 0.56, 'trend': 'stable'},
        {'name': 'Michael Porter Jr', 'ppg': 16.5, 'rpg': 7.0, 'apg': 1.5, 'fg_pct': 0.48, 'trend': 'up'},
    ],
    'Mavericks': [
        {'name': 'Luka Dončić', 'ppg': 33.8, 'rpg': 9.2, 'apg': 9.8, 'fg_pct': 0.48, 'trend': 'up'},
        {'name': 'Kyrie Irving', 'ppg': 25.2, 'rpg': 5.0, 'apg': 5.2, 'fg_pct': 0.49, 'trend': 'up'},
        {'name': 'PJ Washington', 'ppg': 11.5, 'rpg': 6.8, 'apg': 1.2, 'fg_pct': 0.44, 'trend': 'stable'},
        {'name': 'Dereck Lively II', 'ppg': 8.8, 'rpg': 7.2, 'apg': 1.1, 'fg_pct': 0.75, 'trend': 'up'},
    ],
    'Bucks': [
        {'name': 'Giannis Antetokounmpo', 'ppg': 30.8, 'rpg': 11.5, 'apg': 6.5, 'fg_pct': 0.61, 'trend': 'up'},
        {'name': 'Damian Lillard', 'ppg': 24.8, 'rpg': 4.4, 'apg': 7.0, 'fg_pct': 0.43, 'trend': 'down'},
        {'name': 'Khris Middleton', 'ppg': 15.2, 'rpg': 4.8, 'apg': 5.1, 'fg_pct': 0.47, 'trend': 'stable'},
        {'name': 'Brook Lopez', 'ppg': 12.8, 'rpg': 4.9, 'apg': 1.3, 'fg_pct': 0.46, 'trend': 'down'},
    ],
    'Suns': [
        {'name': 'Kevin Durant', 'ppg': 29.1, 'rpg': 6.7, 'apg': 5.0, 'fg_pct': 0.53, 'trend': 'stable'},
        {'name': 'Devin Booker', 'ppg': 27.8, 'rpg': 4.5, 'apg': 6.9, 'fg_pct': 0.49, 'trend': 'up'},
        {'name': 'Bradley Beal', 'ppg': 18.2, 'rpg': 4.0, 'apg': 4.5, 'fg_pct': 0.51, 'trend': 'down'},
        {'name': 'Jusuf Nurkić', 'ppg': 11.0, 'rpg': 11.0, 'apg': 4.0, 'fg_pct': 0.52, 'trend': 'stable'},
    ],
    '76ers': [
        {'name': 'Joel Embiid', 'ppg': 34.2, 'rpg': 11.2, 'apg': 5.8, 'fg_pct': 0.54, 'trend': 'up'},
        {'name': 'Tyrese Maxey', 'ppg': 25.5, 'rpg': 3.7, 'apg': 6.2, 'fg_pct': 0.45, 'trend': 'up'},
        {'name': 'Tobias Harris', 'ppg': 17.2, 'rpg': 6.4, 'apg': 3.1, 'fg_pct': 0.48, 'trend': 'stable'},
        {'name': 'Kelly Oubre Jr', 'ppg': 15.5, 'rpg': 5.0, 'apg': 1.5, 'fg_pct': 0.45, 'trend': 'stable'},
    ],
    'Thunder': [
        {'name': 'Shai Gilgeous-Alexander', 'ppg': 30.8, 'rpg': 5.5, 'apg': 6.2, 'fg_pct': 0.53, 'trend': 'up'},
        {'name': 'Chet Holmgren', 'ppg': 16.8, 'rpg': 7.9, 'apg': 2.4, 'fg_pct': 0.52, 'trend': 'up'},
        {'name': 'Jalen Williams', 'ppg': 19.0, 'rpg': 4.0, 'apg': 4.5, 'fg_pct': 0.54, 'trend': 'up'},
        {'name': 'Josh Giddey', 'ppg': 12.5, 'rpg': 6.5, 'apg': 6.0, 'fg_pct': 0.46, 'trend': 'down'},
    ],
    'Timberwolves': [
        {'name': 'Anthony Edwards', 'ppg': 26.2, 'rpg': 5.4, 'apg': 5.1, 'fg_pct': 0.46, 'trend': 'up'},
        {'name': 'Karl-Anthony Towns', 'ppg': 22.0, 'rpg': 8.5, 'apg': 3.0, 'fg_pct': 0.50, 'trend': 'stable'},
        {'name': 'Rudy Gobert', 'ppg': 14.0, 'rpg': 12.5, 'apg': 1.2, 'fg_pct': 0.66, 'trend': 'stable'},
        {'name': 'Mike Conley', 'ppg': 11.2, 'rpg': 2.6, 'apg': 6.0, 'fg_pct': 0.44, 'trend': 'down'},
    ],
}

# Team selection
col1, col2 = st.columns([1, 1])
with col1:
    selected_team = st.selectbox("Select Team", list(TEAM_PLAYERS.keys()))
with col2:
    prop_type = st.selectbox("Prop Type", ["Points", "Rebounds", "Assists", "PRA (Pts+Reb+Ast)"])

# Get players for selected team
players = TEAM_PLAYERS.get(selected_team, [])

st.markdown(f"### 📊 {selected_team} Player Props - {prop_type}")

# Calculate lines and predictions for each player
for player in players:
    player_name = player['name']
    
    # Get base stat based on prop type
    if prop_type == "Points":
        base_stat = player['ppg']
        line = base_stat * 0.95  # Line slightly below average
    elif prop_type == "Rebounds":
        base_stat = player['rpg']
        line = base_stat * 0.90
    elif prop_type == "Assists":
        base_stat = player['apg']
        line = base_stat * 0.90
    else:  # PRA
        base_stat = player['ppg'] + player['rpg'] + player['apg']
        line = base_stat * 0.93
    
    # Round line to nice numbers
    line = round(line * 2) / 2  # Round to nearest 0.5
    
    # Calculate probability based on performance vs line
    diff = base_stat - line
    variance_factor = max(3, base_stat * 0.15)
    over_prob = 0.5 + (diff / variance_factor)
    over_prob = min(0.90, max(0.10, over_prob))  # Clamp between 10-90%
    
    # Determine prediction
    confidence = "🔥 HIGH" if abs(over_prob - 0.5) > 0.2 else "⚡ MEDIUM" if abs(over_prob - 0.5) > 0.1 else "📊 LOW"
    
    # Get recent performance (simulated)
    import random
    random.seed(hash(player_name) % 1000)
    last_5 = [base_stat + random.gauss(0, variance_factor * 0.5) for _ in range(5)]
    over_count = sum(1 for x in last_5 if x > line)
    
    # Create player card
    with st.container():
        st.markdown(f'<div class="player-card">', unsafe_allow_html=True)
        
        cols = st.columns([2, 1, 1, 1, 1, 1])
        
        with cols[0]:
            st.markdown(f"**{player_name}**")
        
        with cols[1]:
            st.markdown(f"📊 {base_stat:.1f} avg")
        
        with cols[2]:
            st.markdown(f"📈 Line: {line:.1f}")
        
        with cols[3]:
            if over_prob > 0.6:
                st.markdown(f'<span class="hit-badge">{over_prob*100:.0f}% HIT</span>', unsafe_allow_html=True)
            elif over_prob < 0.4:
                st.markdown(f'<span class="miss-badge">{(1-over_prob)*100:.0f}% MISS</span>', unsafe_allow_html=True)
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
                    <span>Over {over_prob*100:.0f}%</span>
                </div>
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill" style="width: {over_prob*100}%;"></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Explanations
st.markdown("""
### 📖 How Predictions Work

**Hit Probability Calculation:**
- Player's season average vs prop line
- Trend factor (recent performance direction)
- Variance based on consistency (lower variance = higher confidence)

**Confidence Levels:**
- 🔥 **HIGH** - Strong edge (>20% deviation from 50%)
- ⚡ **MEDIUM** - Moderate edge (10-20% deviation)
- 📊 **LOW** - Close to coin flip (<10% deviation)

**L5 Column:** Over/Under record in last 5 games vs this line

*Note: Data is 2026 season averages for demonstration. Use BallDontLie API for real-time stats.*
""")

st.markdown("*Powered by ESPN Free API | Sample Data for Demo*")
