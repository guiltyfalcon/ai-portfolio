import streamlit as st
import plotly.graph_objects as go
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.balldontlie import BallDontLieAPI

st.set_page_config(page_title="Player Props 🏀", page_icon="🏀", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .prop-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px;
    }
    .stat-large {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .prob-bar-bg {
        background: rgba(255,255,255,0.1); border-radius: 10px; height: 12px; overflow: hidden;
    }
    .prob-bar-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #ff6b6b, #feca57);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Player Props</div>', unsafe_allow_html=True)

# Initialize API
api = BallDontLieAPI()

# Check config and test connection
if not api.is_configured():
    st.warning("⚠️ BallDontLie API Key Not Configured")
    st.error("""
    **API Key Missing!**
    
    To get REAL player stats, add this to your **Streamlit Cloud Secrets**:
    
    ```toml
    BALLDONTLIE_API_KEY = "edbb1b5d-32f0-48cb-b813-6fdc08574f58"
    ```
    
    **How to add:**
    1. Go to https://share.streamlit.io
    2. Click your app → **Settings (⚙️)** → **Secrets**
    3. Paste the key above
    4. Click **Save** and **Reboot**
    
    💡 BallDontLie is **completely FREE** - just needs authentication
    """)
else:
    # Test the connection
    with st.spinner("Testing API connection..."):
        if not api.test_connection():
            st.error("⚠️ API key found but connection failed!")
            st.info("The key might be invalid or the API might be down. Using sample data.")
        else:
            st.success("✅ BallDontLie API connected!")

# Load player data
top_players = []
if api.is_configured():
    with st.spinner("Loading player data..."):
        try:
            top_players = api.get_top_players(limit=50)
        except Exception as e:
            st.error(f"API Error: {e}")
            top_players = pd.DataFrame()

# Use sample data if no API or load failed
if top_players.empty:
    st.caption("📊 Using sample player data (2026 season averages)")
    top_players = pd.DataFrame([
        {'id': 1, 'full_name': 'LeBron James', 'ppg': 25.2, 'rpg': 7.8, 'apg': 9.0, 'fg_pct': 0.52, 'games': 60},
        {'id': 2, 'full_name': 'Stephen Curry', 'ppg': 28.5, 'rpg': 4.4, 'apg': 5.1, 'fg_pct': 0.47, 'games': 65},
        {'id': 3, 'full_name': 'Kevin Durant', 'ppg': 29.1, 'rpg': 6.7, 'apg': 5.0, 'fg_pct': 0.53, 'games': 70},
        {'id': 4, 'full_name': 'Luka Dončić', 'ppg': 33.8, 'rpg': 9.2, 'apg': 9.8, 'fg_pct': 0.48, 'games': 55},
        {'id': 5, 'full_name': 'Giannis Antetokounmpo', 'ppg': 30.8, 'rpg': 11.5, 'apg': 6.5, 'fg_pct': 0.61, 'games': 62},
        {'id': 6, 'full_name': 'Nikola Jokić', 'ppg': 25.9, 'rpg': 12.0, 'apg': 9.1, 'fg_pct': 0.58, 'games': 68},
        {'id': 7, 'full_name': 'Joel Embiid', 'ppg': 34.2, 'rpg': 11.2, 'apg': 5.8, 'fg_pct': 0.54, 'games': 50},
        {'id': 8, 'full_name': 'Shai Gilgeous-Alexander', 'ppg': 30.8, 'rpg': 5.5, 'apg': 6.2, 'fg_pct': 0.53, 'games': 72},
        {'id': 9, 'full_name': 'Jayson Tatum', 'ppg': 27.2, 'rpg': 8.3, 'apg': 4.9, 'fg_pct': 0.48, 'games': 70},
        {'id': 10, 'full_name': 'Damian Lillard', 'ppg': 24.8, 'rpg': 4.4, 'apg': 7.0, 'fg_pct': 0.43, 'games': 58}
    ])

# Player selection
col1, col2, col3 = st.columns(3)

with col1:
    player_list = top_players['full_name'].tolist() if 'full_name' in top_players.columns else ["No players available"]
    player_name = st.selectbox("Player", player_list)
    
    # Get player data
    player_data = top_players[top_players['full_name'] == player_name].to_dict('records')[0] if player_name in top_players['full_name'].values else {}

with col2:
    prop = st.selectbox("Prop", ["Points", "Rebounds", "Assists", "PRA (Pts+Reb+Ast)"])
    prop_avg = {
        'Points': player_data.get('ppg', 25),
        'Rebounds': player_data.get('rpg', 8),
        'Assists': player_data.get('apg', 7),
        'PRA (Pts+Reb+Ast)': player_data.get('ppg', 25) + player_data.get('rpg', 8) + player_data.get('apg', 7)
    }.get(prop, 20)

with col3:
    line = st.number_input("Line", value=float(prop_avg), step=0.5, format="%.1f")

if not api.is_configured():
    st.caption("📊 Using sample data (2026 season). Add BALLDONTLIE_API_KEY for real-time stats.")

# Prediction panel
st.markdown("### 🔮 Prediction")

cols = st.columns(4)
cols[0].metric("Player Avg", f"{prop_avg:.1f}")
cols[1].metric("Line", f"{line}")

# Calculate probability based on average vs line
diff = prop_avg - line
games_played = player_data.get('games', 60)
# Higher confidence if player has more games
variance_factor = max(2, 10 - (games_played / 20))
over_prob = 0.5 + (diff / variance_factor)
over_prob = min(0.95, max(0.05, over_prob))

cols[2].metric("Over %", f"{over_prob*100:.0f}%")
cols[3].metric("Under %", f"{(1-over_prob)*100:.0f}%")

# Visual probability bar
st.markdown("### Win Probability")
st.markdown(f'''
<div style="display: flex; align-items: center; gap: 10px;">
    <span style="font-weight: 600;">Under {(1-over_prob)*100:.0f}%</span>
    <div class="prob-bar-bg" style="flex: 1;">
        <div class="prob-bar-fill" style="width: {over_prob*100}%; margin-left: 0;"></div>
    </div>
    <span style="font-weight: 600;">Over {over_prob*100:.0f}%</span>
</div>
''', unsafe_allow_html=True)

# Show last 5 games (real if API, sample otherwise)
st.markdown("### 📈 Recent Performance")

if api.is_configured() and player_data.get('id'):
    # Could fetch actual game logs here if endpoint available
    st.info("💡 With API access, actual game logs would appear here")
    last_5 = [prop_avg + np.random.normal(0, 4) for _ in range(5)]
else:
    # Sample last 5 games with realistic variance
    last_5 = [prop_avg + np.random.normal(0, prop_avg * 0.15) for _ in range(5)]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=['G-5', 'G-4', 'G-3', 'G-2', 'G-1'],
    y=last_5,
    mode='lines+markers',
    line=dict(color='#00d2ff', width=3),
    marker=dict(size=14, color=['#ff4757' if d < line else '#00d26a' for d in last_5]),
    name='Actual'
))
fig.add_hline(y=line, line_dash="dash", line_color="#ff4757", annotation_text=f"Line: {line}", annotation_position="right")
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=300,
    yaxis_title=prop,
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

if api.is_configured():
    # Show additional stats if available
    if player_data:
        st.markdown("---")
        st.markdown("### 📊 Player Stats")
        stats_cols = st.columns(5)
        stats_cols[0].metric("Games", int(player_data.get('games_played', 0)))
        stats_cols[1].metric("PPG", f"{player_data.get('ppg', 0):.1f}")
        stats_cols[2].metric("RPG", f"{player_data.get('rpg', 0):.1f}")
        stats_cols[3].metric("APG", f"{player_data.get('apg', 0):.1f}")
        stats_cols[4].metric("FG%", f"{player_data.get('fg_pct', 0)*100:.1f}%")
else:
    st.markdown("""
    ---
    🔑 **Want real data?**
    
    Get your free API key at [balldontlie.io](https://www.balldontlie.io/) and add it to your secrets!
    """)
