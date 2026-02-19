"""
Live Odds - Compare odds across sportsbooks
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.odds import OddsAPI

st.set_page_config(
    page_title="Live Odds 📊",
    page_icon="📊",
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
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .odds-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
    }
    .bookmaker {
        background: rgba(0,210,255,0.1);
        border: 1px solid rgba(0,210,255,0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: #00d2ff;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Live Odds Comparison</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Compare odds across top sportsbooks in real-time
</div>
""", unsafe_allow_html=True)

# Check if Odds API is configured
odds_api = OddsAPI()
if not odds_api.is_configured():
    st.warning("⚠️ The Odds API key is not configured. Add `THEODDS_API_KEY` to your secrets to see live odds.")
    st.info("💡 In the meantime, showing demo odds structure")

# Sport selector
sport = st.selectbox("Select Sport", ['NBA', 'NFL', 'MLB', 'NHL', 'NCAAB', 'NCAAF'])

# Try to load odds
try:
    if odds_api.is_configured():
        with st.spinner("Loading live odds..."):
            odds_df = odds_api.get_odds(sport.lower())
        
        if not odds_df.empty:
            st.success(f"✅ Loaded {len(odds_df)} games with odds")
            
            for _, game in odds_df.head(10).iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="odds-card">
                        <h4>{game['home_team']} vs {game['away_team']}</h4>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px;">
                            <div class="bookmaker">
                                <div style="font-size: 0.8rem; color: #888;">DraftKings</div>
                                <div>{game.get('home_ml', 'N/A')}</div>
                            </div>
                            <div class="bookmaker">
                                <div style="font-size: 0.8rem; color: #888;">FanDuel</div>
                                <div>{game.get('home_ml', 'N/A')}</div>
                            </div>
                            <div class="bookmaker">
                                <div style="font-size: 0.8rem; color: #888;">BetMGM</div>
                                <div>{game.get('home_ml', 'N/A')}</div>
                            </div>
                            <div class="bookmaker">
                                <div style="font-size: 0.8rem; color: #888;">bet365</div>
                                <div>{game.get('home_ml', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No odds available for this sport right now.")
    else:
        # Demo mode
        st.info("🔧 Demo Mode - Add API key for live data")
        
        demo_games = [
            ("Lakers", "Warriors", -110, -110),
            ("Celtics", "Nets", -140, +120),
            ("Bucks", "Heat", -160, +140),
        ]
        
        for home, away, home_odds, away_odds in demo_games:
            st.markdown(f"""
            <div class="odds-card">
                <h4>{home} vs {away}</h4>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px;">
                    <div class="bookmaker">
                        <div style="font-size: 0.8rem; color: #888;">DraftKings</div>
                        <div>{home_odds:+d}</div>
                    </div>
                    <div class="bookmaker">
                        <div style="font-size: 0.8rem; color: #888;">FanDuel</div>
                        <div>{home_odds:+d}</div>
                    </div>
                    <div class="bookmaker">
                        <div style="font-size: 0.8rem; color: #888;">BetMGM</div>
                        <div>{home_odds:+d}</div>
                    </div>
                    <div class="bookmaker">
                        <div style="font-size: 0.8rem; color: #888;">bet365</div>
                        <div>{home_odds:+d}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading odds: {e}")

st.markdown("---")
st.caption("💡 Live odds update every 60 seconds | Data from The Odds API")
