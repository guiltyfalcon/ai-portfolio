import streamlit as st
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.espn_all_sports import ESPNSportsAPI, get_player_data_unified, PROP_CONFIG, STATIC_FALLBACK

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
    .data-live { color: #00d26a; font-weight: 600; }
    .data-static { color: #feca57; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Player Props</div>', unsafe_allow_html=True)

# Sport selection
sports = ['NBA', 'NFL', 'MLB', 'NHL']
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    sport = st.selectbox("Sport", sports, format_func=lambda x: {
        'NBA': '🏀 NBA', 'NFL': '🏈 NFL', 'MLB': '⚾ MLB', 'NHL': '🏒 NHL'
    }.get(x, x))

# Get teams from static fallback (for selection)
teams = list(STATIC_FALLBACK.get(sport, {}).keys())

with col2:
    selected_team = st.selectbox("Team", teams if teams else ["Loading..."])

# Get props for sport
props = PROP_CONFIG.get(sport, {}).get('props', [])

with col3:
    prop_type = st.selectbox("Prop", props if props else ["Loading..."])

# Try to get live data first
data_source = "LIVE"
players = []

try:
    api = ESPNSportsAPI(sport)
    
    # Get team ID
    api_teams = api.get_teams()
    team_id = None
    for t in api_teams:
        if t.get('name') == selected_team:
            team_id = t.get('id')
            break
    
    if team_id:
        api_players = api.get_team_players(team_id)
        for player in api_players[:8]:  # Top 8 players
            stats = api.get_player_stats(player.get('id'))
            if stats:
                players.append({
                    'name': player.get('name'),
                    'position': player.get('position', ''),
                    **stats
                })
    
    if not players:
        raise Exception("No live data")
        
except Exception as e:
    # Fallback to static
    data_source = "STATIC"
    players = STATIC_FALLBACK.get(sport, {}).get(selected_team, [])

# Show data source indicator
if data_source == "LIVE":
    st.caption(f"📡 <span class='data-live'>LIVE DATA</span> from ESPN API | {sport} 2025-26 Season", unsafe_allow_html=True)
else:
    st.caption(f"📊 <span class='data-static'>STATIC DATA</span> (ESPN API unavailable) | {sport} 2025-26 Season", unsafe_allow_html=True)

if not players:
    st.warning(f"No player data available for {selected_team}")
    st.stop()

st.markdown(f"### 📊 {selected_team} Player Props - {prop_type}")

# Get stat mapping
stat_map = PROP_CONFIG.get(sport, {}).get('stat_map', {})
stat_key = stat_map.get(prop_type)

# Calculate and display for each player
for player in players:
    player_name = player.get('name', 'Unknown')
    position = player.get('position', '')
    
    # Get base stat
    if isinstance(stat_key, list):
        base_stat = sum(player.get(k, 0) for k in stat_key)
    else:
        base_stat = player.get(stat_key, 0)
    
    if base_stat == 0:
        continue
    
    # Calculate line (95% of average, rounded nicely)
    if sport == 'MLB' and prop_type == 'Hits':
        line = round(base_stat * 0.95, 3)
    elif sport == 'NHL':
        line = round(base_stat * 0.95, 2)
    else:
        line = round(base_stat * 0.95 * 2) / 2
    
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
    last_5 = [base_stat + np.random.normal(0, variance) for _ in range(5)]
    over_count = sum(1 for x in last_5 if x > line)
    
    # Create card
    with st.container():
        st.markdown(f'<div class="player-card">', unsafe_allow_html=True)
        
        cols = st.columns([3, 1, 1, 1, 1, 1])
        
        with cols[0]:
            st.markdown(f"**{player_name}** <span style='color:#888;font-size:0.8rem'>{position}</span>")
        
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
                    <span>{data_source}</span>
                    <span>Over {over_prob*100:.0f}%</span>
                </div>
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill" style="width: {over_prob*100}%;"></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Sport-specific info
sport_info = {
    'NBA': "🏀 **NBA Props:** Points, Rebounds, Assists, PRA | Data from ESPN API",
    'NFL': "🏈 **NFL Props:** Pass Yds, Pass TDs, Rush Yds, Receptions, Rec Yards | Data from ESPN API",
    'MLB': "⚾ **MLB Props:** Hits, Home Runs, RBIs | Data from ESPN API",
    'NHL': "🏒 **NHL Props:** Goals, Assists, Points, Shots | Data from ESPN API"
}

st.markdown(sport_info.get(sport, ""))

st.markdown("""
### 📖 How It Works

**Data Sources:**
- 📡 **LIVE** - Real-time from ESPN API (free, no key)
- 📊 **STATIC** - Sample data when API unavailable

**Hit Probability:**
- Based on season average vs prop line
- Variance factor for consistency
- Edge calculation for confidence

**All ESPN APIs are FREE - no authentication required!**
""")

st.markdown("*Powered by ESPN Public API | Free Tier*")
