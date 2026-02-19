import streamlit as st
import plotly.graph_objects as go
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.balldontlie import BallDontLieAPI
from api.espn import ESPNAPI

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
    .coming-soon {
        background: rgba(255,255,255,0.05); border: 1px dashed rgba(255,255,255,0.2);
        border-radius: 12px; padding: 20px; text-align: center; color: #888;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Player Props</div>', unsafe_allow_html=True)

# Check for API availability
api_key = os.getenv('BALLDONTLIE_API_KEY')
if not api_key:
    st.warning("⚠️ BallDontLie API requires authentication")
    st.info("""
    To enable real player prop data:
    1. Get free API key at: https://www.balldontlie.io/
    2. Add `BALLDONTLIE_API_KEY` to your Streamlit secrets
    
    **Note:** This page currently shows sample data for demonstration.
    """)

# For now, use sample data with clear labeling
SAMPLE_PLAYERS = {
    'LeBron James': {'team': 'LAL', 'ppg': 25.2, 'rpg': 7.8, 'apg': 9.0, 'fg_pct': 0.52},
    'Stephen Curry': {'team': 'GSW', 'ppg': 28.5, 'rpg': 4.4, 'apg': 5.1, 'fg_pct': 0.47},
    'Kevin Durant': {'team': 'PHX', 'ppg': 29.1, 'rpg': 6.7, 'apg': 5.0, 'fg_pct': 0.53},
    'Luka Dončić': {'team': 'DAL', 'ppg': 33.8, 'rpg': 9.2, 'apg': 9.8, 'fg_pct': 0.48},
    'Giannis Antetokounmpo': {'team': 'MIL', 'ppg': 30.8, 'rpg': 11.5, 'apg': 6.5, 'fg_pct': 0.61},
    'Nikola Jokić': {'team': 'DEN', 'ppg': 25.9, 'rpg': 12.0, 'apg': 9.1, 'fg_pct': 0.58}
}

col1, col2, col3 = st.columns(3)
with col1:
    player_name = st.selectbox("Player", list(SAMPLE_PLAYERS.keys()))
with col2:
    prop = st.selectbox("Prop", ["Points", "Rebounds", "Assists", "3-Pointers Made"])
with col3:
    player_data = SAMPLE_PLAYERS.get(player_name, {})
    prop_avg = {'Points': player_data.get('ppg', 25), 
                'Rebounds': player_data.get('rpg', 8),
                'Assists': player_data.get('apg', 7),
                '3-Pointers Made': 3.2}.get(prop, 20)
    line = st.number_input("Line", value=float(prop_avg), step=0.5)

if not api_key:
    st.caption("📊 Using sample data (2024 season averages)")

st.markdown("### 📊 Prediction")
cols = st.columns(4)
cols[0].metric("Player Avg", f"{prop_avg}")
cols[1].metric("Line", f"{line}")

# Simple probability based on average vs line
diff = prop_avg - line
over_prob = min(0.9, max(0.1, 0.5 + (diff / 10)))
cols[2].metric("Over %", f"{over_prob*100:.0f}%")
cols[3].metric("Under %", f"{(1-over_prob)*100:.0f}%")

# Show sample recent games (not real data)
import numpy as np
last_5 = [prop_avg + np.random.normal(0, 5) for _ in range(5)]

st.markdown("### 📈 Last 5 Games")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=['G-5', 'G-4', 'G-3', 'G-2', 'G-1'],
    y=last_5,
    mode='lines+markers',
    line=dict(color='#00d2ff', width=3),
    marker=dict(size=12, color=[d >= line for d in last_5], colorscale=[[0, '#ff4757'], [1, '#00d26a']], showscale=False),
    name='Actual'
))
fig.add_hline(y=line, line_dash="dash", line_color="#ff4757", annotation_text=f"Line: {line}")
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=300,
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

if not api_key:
    st.markdown("""
    ---
    💡 **Want real data?**
    ```toml
    # Add to .streamlit/secrets.toml
    BALLDONTLIE_API_KEY = "your_key_here"
    ```
    """)
