"""
Sports Betting AI - Main Dashboard
Live data from ESPN + The Odds API
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Sports Betting AI 🏆",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .game-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .value-bet {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🏆')

# Title
st.markdown('<div class="main-header">🏆 Sports Betting AI</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666;">Live ESPN Data + Odds Analysis</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=60)
    st.markdown("## Settings")
    
    sport = st.selectbox(
        "Sport",
        ['NBA', 'NFL', 'MLB', 'NHL'],
        format_func=lambda x: f"{get_sport_emoji(x)} {x}"
    )
    
    days = st.slider("Days Ahead", 1, 7, 3)
    
    st.markdown("---")
    st.markdown("### 📊 Live Data Sources")
    st.markdown("- **ESPN API**: Team stats, schedules")
    st.markdown("- **The Odds API**: Live betting lines")
    
    st.markdown("---")
    st.caption("Built with Streamlit 🍡")

# Load data
try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    
    with st.spinner(f"Loading {sport} data..."):
        # ESPN Data
        espn = ESPNAPI()
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Teams", len(teams))
        with col2:
            st.metric("Upcoming Games", len(schedule))
        with col3:
            st.metric("Data Source", "ESPN ✓")
        
        st.markdown("---")
        st.subheader(f"{get_sport_emoji(sport)} Upcoming Games")
        
        if schedule.empty:
            st.info(f"No {sport} games scheduled in the next {days} days.")
        else:
            # Show games
            cols = st.columns(2)
            for idx, (_, game) in enumerate(schedule.iterrows()):
                with cols[idx % 2]:
                    with st.container():
                        st.markdown(f"""
                        <div class="game-card">
                            <h4>{game['home_team']} vs {game['away_team']}</h4>
                            <p>🏠 {game['home_team']}: {game.get('home_record', 'N/A')}<br>
                               ✈️ {game['away_team']}: {game.get('away_record', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Try to load odds
        st.markdown("---")
        st.subheader("💰 Live Odds")
        
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
            
            if not odds.empty:
                st.dataframe(
                    odds[['home_team', 'away_team', 'home_ml', 'away_ml']].head(10),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No odds data available for selected sport.")
        except Exception as e:
            st.error(f"⚠️ Odds API Error: {e}")
            st.info("Check your THEODDS_API_KEY in Settings → Secrets")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure API keys are configured correctly.")

# Footer
st.markdown("---")
st.caption("Powered by ESPN API + The Odds API | Built with Streamlit")
