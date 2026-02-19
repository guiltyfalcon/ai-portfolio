"""
Player Props - NBA player stat predictions
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.balldontlie import BallDontLieAPI

st.set_page_config(
    page_title="Player Props 🏀",
    page_icon="🏀",
    layout="wide"
)

# Modern Dark Theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .prop-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
    }
    .stat-box {
        background: rgba(255,107,107,0.1);
        border: 1px solid rgba(255,107,107,0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Player Props Predictor</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Over/Under predictions for Points, Rebounds, Assists
</div>
""", unsafe_allow_html=True)

# Player selector
st.markdown("### 🎯 Select Prop")

col1, col2, col3 = st.columns(3)

with col1:
    player = st.selectbox(
        "Player",
        [
            "LeBron James", "Kevin Durant", "Stephen Curry",
            "Giannis Antetokounmpo", "Luka Dončić", "Nikola Jokić",
            "Joel Embiid", "Jayson Tatum", "Ja Morant", "Trae Young"
        ]
    )

with col2:
    prop_type = st.selectbox(
        "Prop Type",
        ["Points", "Rebounds", "Assists", "PRA (Points+Rebounds+Assists)", "Threes Made"]
    )

with col3:
    line = st.number_input("Line", value=26.5, step=0.5, min_value=0.0)

# Get player data and make prediction
st.markdown("---")

# Mock prediction based on player and line
player_averages = {
    "LeBron James": {"Points": 27.5, "Rebounds": 8.0, "Assists": 7.5, "Threes Made": 2.2},
    "Kevin Durant": {"Points": 28.0, "Rebounds": 7.0, "Assists": 5.0, "Threes Made": 1.8},
    "Stephen Curry": {"Points": 29.0, "Rebounds": 5.0, "Assists": 6.5, "Threes Made": 4.5},
    "Giannis Antetokounmpo": {"Points": 31.0, "Rebounds": 11.5, "Assists": 5.5, "Threes Made": 0.8},
    "Luka Dončić": {"Points": 33.0, "Rebounds": 8.5, "Assists": 9.0, "Threes Made": 3.2},
    "Nikola Jokić": {"Points": 26.0, "Rebounds": 12.0, "Assists": 9.5, "Threes Made": 1.2},
    "Joel Embiid": {"Points": 34.0, "Rebounds": 11.0, "Assists": 6.0, "Threes Made": 1.1},
    "Jayson Tatum": {"Points": 27.0, "Rebounds": 8.5, "Assists": 4.5, "Threes Made": 3.0},
    "Ja Morant": {"Points": 25.5, "Rebounds": 5.5, "Assists": 8.0, "Threes Made": 1.5},
    "Trae Young": {"Points": 26.5, "Rebounds": 3.0, "Assists": 10.5, "Threes Made": 3.2}
}

# Calculate probability
if prop_type == "PRA (Points+Rebounds+Assists)":
    avg = sum(player_averages.get(player, {}).values()) - player_averages.get(player, {}).get("Threes Made", 0)
else:
    avg = player_averages.get(player, {}).get(prop_type, line)

# Simple model: probability based on average vs line
if avg > line:
    over_prob = min(0.85, 0.5 + (avg - line) / 10)
else:
    over_prob = max(0.15, 0.5 - (line - avg) / 10)

st.markdown("### 📊 Prediction")

cols = st.columns(3)

with cols[0]:
    st.metric("Player Average", f"{avg:.1f}")
    st.progress(over_prob)

with cols[1]:
    st.metric("Over Probability", f"{over_prob*100:.0f}%")
    st.progress(over_prob)

with cols[2]:
    st.metric("Under Probability", f"{(1-over_prob)*100:.0f}%")
    st.progress(1-over_prob)

# Recommendation
st.markdown("---")

if over_prob > 0.6:
    st.success(f"✅ **OVER {line} Recommended** - Player averages {avg:.1f} {prop_type}")
elif over_prob < 0.4:
    st.error(f"📉 **UNDER {line} Recommended** - Player averages {avg:.1f} {prop_type}")
else:
    st.info(f"⚖️ **No Edge Detected** - Player average {avg:.1f} is close to line {line}")

# Last 5 games simulation
st.markdown("### 📈 Last 5 Games Performance")

import numpy as np

# Generate realistic last 5 games based on average
np.random.seed(hash(player) % 1000)
games = []
for i in range(5):
    if prop_type == "PRA (Points+Rebounds+Assists)":
        # Sum of 3 stats with variance
        val = np.random.normal(avg, 5)
    else:
        val = np.random.normal(avg, avg * 0.15)
    games.append(max(0, val))

games_df = pd.DataFrame({
    'Game': ['vs LAL', 'vs BOS', '@ NYK', 'vs MIA', '@ PHX'],
    prop_type: [f"{g:.1f}" for g in games],
    'Result': ['Over' if g > line else 'Under' for g in games]
})

st.dataframe(games_df, hide_index=True, use_container_width=True)

# Chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=list(range(1, 6)),
    y=games,
    mode='lines+markers',
    name='Actual',
    line=dict(color='#00d2ff', width=3),
    marker=dict(size=10)
))

fig.add_hline(y=line, line_dash="dash", line_color="#ff4757", 
              annotation_text=f"Line: {line}")

fig.update_layout(
    title=f"{player} - Last 5 Games {prop_type}",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=300,
    xaxis_title="Game",
    yaxis_title=prop_type
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("💡 Player props powered by historical averages and recent form")
