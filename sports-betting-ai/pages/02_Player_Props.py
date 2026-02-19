import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
        transition: all 0.3s ease;
    }
    .prop-card:hover {
        transform: translateY(-3px);
        border-color: rgba(255,107,107,0.3);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Player Props Predictor</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Over/Under predictions for Points, Rebounds, Assists
</div>
""", unsafe_allow_html=True)

# Mock player selector
st.markdown("### 🎯 Select Prop")

col1, col2, col3 = st.columns(3)

with col1:
    player = st.selectbox("Player", [
        "LeBron James", "Kevin Durant", "Stephen Curry", 
        "Giannis Antetokounmpo", "Luka Dončić", "Nikola Jokić"
    ])

with col2:
    prop_type = st.selectbox("Prop Type", [
        "Points", "Rebounds", "Assists", "PRA", "Threes"
    ])

with col3:
    line = st.number_input("Line", value=26.5, step=0.5)

# Prediction display
st.markdown("---")

# Mock prediction
over_prob = 0.58

st.markdown("### 📊 Prediction")

cols = st.columns(3)
with cols[0]:
    st.metric("Over Probability", f"{over_prob*100:.0f}%")
    st.progress(over_prob)
with cols[1]:
    st.metric("Under Probability", f"{(1-over_prob)*100:.0f}%")
    st.progress(1-over_prob)
with cols[2]:
    if over_prob > 0.55:
        st.success("✅ OVER recommended")
    elif over_prob < 0.45:
        st.error("📉 UNDER recommended")
    else:
        st.info("⚖️ No edge detected")

# Recent performance
st.markdown("### 📈 Last 5 Games")

games_data = pd.DataFrame({
    'Game': ['vs LAL', 'vs BOS', '@NYK', 'vs MIA', '@PHX'],
    prop_type: [28.5, 32.0, 24.0, 31.5, 29.0]
})

st.dataframe(games_data, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Player props powered by BallDontLie player data")
