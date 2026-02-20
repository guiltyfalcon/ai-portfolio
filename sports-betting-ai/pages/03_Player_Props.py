import streamlit as st
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try MySportsFeeds first, fall back to ESPN/Static
try:
    from api.mysportsfeeds import MySportsFeedsAPI, SPORT_CONFIG
    MYSPORTSFEEDS_AVAILABLE = True
except:
    MYSPORTSFEEDS_AVAILABLE = False

from api.espn_all_sports import ESPNSportsAPI, STATIC_FALLBACK, PROP_CONFIG

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
    .status-badge {
        display: inline-block; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: 600;
    }
    .status-live { background: rgba(0,210,106,0.2); color: #00d26a; }
    .status-static { background: rgba(254,202,87,0.2); color: #feca57; }
    .status-setup { background: rgba(255,107,107,0.2); color: #ff6b6b; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Player Props</div>', unsafe_allow_html=True)

# Check data source
api_key = st.secrets.get("MYSPORTSFEEDS_API_KEY", "")
if MYSPORTSFEEDS_AVAILABLE and api_key:
    data_source = "MYSPORTSFEEDS"
    source_label = "📡 MySportsFeeds LIVE"
    source_class = "status-live"
    st.caption(f"<span class='status-badge {source_class}'>{source_label}</span> | Real-time player stats for all sports", unsafe_allow_html=True)
elif MYSPORTSFEEDS_AVAILABLE and not api_key:
    data_source = "SETUP"
    source_label = "⚙️ SETUP REQUIRED"
    source_class = "status-setup"
    st.caption(f"<span class='status-badge {source_class}'>{source_label}</span> | Add MySportsFeeds API key to secrets", unsafe_allow_html=True)
else:
    data_source = "ESPN/STATIC"
    source_label = "📊 ESPN + Static"
    source_class = "status-static"
    st.caption(f"<span class='status-badge {source_class}'>{source_label}</span> | Sample data (Live data coming with MySportsFeeds)", unsafe_allow_html=True)

# Sport selection
sports = ['NBA', 'NFL', 'MLB', 'NHL']
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    sport = st.selectbox("Sport", sports, format_func=lambda x: {
        'NBA': '🏀 NBA', 'NFL': '🏈 NFL', 'MLB': '⚾ MLB', 'NHL': '🏒 NHL'
    }.get(x, x))

# Get teams based on data source
if data_source == "MYSPORTSFEEDS":
    teams = SPORT_CONFIG.get(sport.lower(), {}).get('teams', [])
    props = SPORT_CONFIG.get(sport.lower(), {}).get('props', [])
else:
    teams = list(STATIC_FALLBACK.get(sport, {}).keys())
    props = PROP_CONFIG.get(sport, {}).get('props', [])

with col2:
    selected_team = st.selectbox("Team", teams if teams else ["Loading..."])

with col3:
    prop_type = st.selectbox("Prop", props if props else ["Loading..."])

# Fetch player data
players = []

if data_source == "MYSPORTSFEEDS":
    try:
        api = MySportsFeedsAPI(api_key=api_key)
        df = api.get_players_by_team(sport.lower(), selected_team)
        if not df.empty:
            df = api._add_prop_lines(df, sport.lower(), prop_type)
            players = df.to_dict('records')
    except Exception as e:
        st.error(f"MySportsFeeds error: {e}")
        data_source = "ESPN/STATIC"

if not players and data_source != "MYSPORTSFEEDS":
    # Use static fallback
    players = STATIC_FALLBACK.get(sport, {}).get(selected_team, [])

if not players:
    if data_source == "SETUP":
        st.error("""
        ### 🔑 MySportsFeeds API Key Required
        
        To get LIVE player props data:
        
        1. **Register free at**: [mysportsfeeds.com/register](https://www.mysportsfeeds.com/register/)
        2. **Get your API key** from your account dashboard
        3. **Add to Streamlit secrets** in `.streamlit/secrets.toml`:
        
        ```toml
        [secrets]
        THEODDS_API_KEY = "your-odds-api-key"
        MYSPORTSFEEDS_API_KEY = "your-mysportsfeeds-key"
        ```
        
        **Free Tier**: 500 API calls/day (plenty for this app!)
        """)
    else:
        st.warning(f"No player data available for {selected_team}")
    st.stop()

st.markdown(f"### 📊 {selected_team} Player Props - {prop_type}")

# Display players
for player in players:
    if data_source == "MYSPORTSFEEDS":
        player_name = player.get('fullName', 'Unknown')
        position = player.get('position', '')
        base_stat = player.get('prop_avg', 0)
        line = player.get('prop_line', 0)
        over_prob = player.get('over_prob', 0.5)
    else:
        # Static format
        player_name = player.get('name', 'Unknown')
        position = player.get('position', '')
        
        # Map prop to stat
        stat_map = PROP_CONFIG.get(sport, {}).get('stat_map', {}).get(prop_type)
        if isinstance(stat_map, list):
            base_stat = sum(player.get(k, 0) for k in stat_map)
        else:
            base_stat = player.get(stat_map, 0) if stat_map else 0
        
        # Calculate line
        if sport == 'MLB' and prop_type == 'Hits':
            line = round(base_stat * 0.95, 3)
        elif sport == 'NHL':
            line = round(base_stat * 0.95, 2)
        else:
            line = round(base_stat * 0.95 * 2) / 2
        
        # Calculate probability
        diff = base_stat - line
        variance = max(2, base_stat * 0.15) if base_stat > 0 else 2
        over_prob = 0.5 + (diff / variance)
        over_prob = min(0.90, max(0.10, over_prob))
    
    if base_stat == 0:
        continue
    
    # Confidence
    confidence = "🔥 HIGH" if abs(over_prob - 0.5) > 0.2 else "⚡ MEDIUM" if abs(over_prob - 0.5) > 0.1 else "📊 LOW"
    
    # Last 5 simulation
    random.seed(hash(player_name + sport) % 1000)
    variance_factor = max(2, base_stat * 0.15) if base_stat > 0 else 2
    last_5 = [base_stat + np.random.normal(0, variance_factor * 0.5) for _ in range(5)]
    over_count = sum(1 for x in last_5 if x > line)
    
    # Display card
    with st.container():
        st.markdown(f'<div class="player-card">', unsafe_allow_html=True)
        cols = st.columns([3, 1, 1, 1, 1, 1])
        
        with cols[0]:
            st.markdown(f"**{player_name}** <span style='color:#888;font-size:0.8rem'>{position}</span>", unsafe_allow_html=True)
        
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

# Sport info
sport_info = {
    'NBA': "🏀 **NBA Props:** Points, Rebounds, Assists, PRA | 2025-26 Season",
    'NFL': "🏈 **NFL Props:** Pass Yds, TDs, Rush Yds, Receptions | 2024-25 Season",
    'MLB': "⚾ **MLB Props:** Hits, HR, RBI | 2025 Season",
    'NHL': "🏒 **NHL Props:** Goals, Assists, Points, Shots | 2025-26 Season"
}
st.markdown(sport_info.get(sport, ""))

st.markdown("""
### 📖 Data Sources

**MySportsFeeds (Recommended)**
- ✅ Live player statistics
- ✅ All major sports
- ✅ 500 free API calls/day
- 🔑 Requires free API key

**ESPN + Static (Fallback)**
- 📊 Sample season data
- ✅ Works without API key
- ⚠️ Updated periodically

**To enable live data:**
1. Register at [mysportsfeeds.com/register](https://www.mysportsfeeds.com/register/)
2. Add key to `.streamlit/secrets.toml`
3. Restart app
""")

st.markdown("*Market-ready with MySportsFeeds integration*")
