import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.espn import ESPNAPI
from api.odds import OddsAPI

st.set_page_config(page_title="Live Odds 📊", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .odds-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
        padding: 20px; margin: 10px 0; transition: all 0.3s ease;
    }
    .odds-card:hover { border-color: rgba(0,210,255,0.3); }
    .odds-box {
        background: rgba(0,210,255,0.1); border: 1px solid rgba(0,210,255,0.3);
        border-radius: 12px; padding: 12px; text-align: center;
        font-weight: 700; color: #00d2ff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Live Odds</div>', unsafe_allow_html=True)

sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL'])

odds_api = OddsAPI()
if not odds_api.is_configured():
    st.warning("⚠️ Add THEODDS_API_KEY to secrets for live odds")

try:
    with st.spinner("Loading odds..."):
        odds = odds_api.get_odds(sport.lower()) if odds_api.is_configured() else pd.DataFrame()
    
    if not odds.empty:
        for _, game in odds.head(10).iterrows():
            st.markdown(f'''
            <div class="odds-card">
                <h4>{game['home_team']} vs {game['away_team']}</h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;">
                    <div class="odds-box">Spread<br/>-5.5</div>
                    <div class="odds-box">ML<br/>{int(game.get('home_ml', -110))}</div>
                    <div class="odds-box">O/U<br/>226.5</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No live odds available")
        
except Exception as e:
    st.error(f"Error: {e}")
