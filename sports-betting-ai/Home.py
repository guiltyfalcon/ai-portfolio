"""
Sports Betting AI - Full System with BallDontLie + Universal Predictor
NBA gets player-level data, all sports get sport-specific predictions
LIVE DATA - Auto-refreshes every 60 seconds
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Sports Betting AI Pro 🏆",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 60 seconds (like real betting apps)
st_autorefresh(interval=60 * 1000, key="datarefresh")

# Styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .value-pick {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
    }
    .player-stats {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🏆')

def american_to_implied(odds):
    if pd.isna(odds):
        return 0.5
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)

# Title
st.markdown('<div class="main-header">🏆 Sports Betting AI <span style="color:#2ecc71; font-size:0.6em; vertical-align:middle;">● LIVE</span></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666;">Universal Predictions + BallDontLie NBA Data</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #2ecc71; font-size: 0.9em;">🔄 Auto-refresh every 60 seconds</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=60)
    st.markdown("## Settings")
    
    sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL'], 
                        format_func=lambda x: f"{get_sport_emoji(x)} {x}")
    days = st.slider("Days Ahead", 1, 7, 3)
    value_threshold = st.slider("Value Edge %", 1, 15, 5) / 100
    
    st.markdown("---")
    
    # LIVE indicator with last refresh time
    st.markdown("### 🟢 LIVE Data")
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"**Last Refresh:** {current_time}")
    st.caption("Auto-refreshes every 60 seconds")
    
    # Data source info
    if sport == 'NBA':
        st.markdown("### 🏀 NBA Data Sources")
        st.markdown("- **BallDontLie**: Free player stats, games")
        st.markdown("- **ESPN**: Team schedules")
        st.markdown("- **The Odds API**: Live lines")
    else:
        st.markdown(f"### {get_sport_emoji(sport)} {sport} Data")
        st.markdown("- **ESPN**: Schedules, records")
        st.markdown("- **The Odds API**: Live lines")
        st.markdown("- **Sport-Specific Model**: Prediction engine")
    
    st.markdown("---")
    st.caption("🍡 Sports Betting AI v1.1")

# Load Data
try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    from models.universal_predictor import UniversalSportsPredictor
    
    # Load sport-specific data
    with st.spinner(f"Loading {sport} data..."):
        espn = ESPNAPI()
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Try BallDontLie for NBA
        nba_data = None
        if sport == 'NBA':
            try:
                from api.balldontlie import BallDontLieAPI
                bdl = BallDontLieAPI()
                nba_teams = bdl.get_teams()
                nba_games = bdl.get_games(start_date=pd.Timestamp.now().strftime('%Y-%m-%d'),
                                           end_date=(pd.Timestamp.now() + pd.Timedelta(days=days)).strftime('%Y-%m-%d'))
                nba_data = {'teams': nba_teams, 'games': nba_games}
                st.sidebar.success("✅ BallDontLie connected")
            except Exception as e:
                st.sidebar.warning(f"⚠️ BallDontLie: {str(e)[:50]}")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Teams", len(teams))
        with col2:
            st.metric("Upcoming Games", len(schedule))
        with col3:
            st.metric("Data Source", "BallDontLie" if nba_data else "ESPN")
        with col4:
            st.metric("Predictor", "Universal Model")
        
        # Initialize predictor
        predictor = UniversalSportsPredictor(sport.lower())
        
        # Engineer features
        features = predictor.engineer_features(schedule, teams)
        
        # Get predictions
        predictions = predictor.predict(features)
        
        # Merge back
        result = pd.concat([features, predictions], axis=1)
        
        # Load odds
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
            
            if not odds.empty:
                result = result.merge(
                    odds[['home_team', 'away_team', 'home_ml', 'away_ml']],
                    on=['home_team', 'away_team'],
                    how='left'
                )
                
                # Calculate value bets
                result['home_implied'] = result['home_ml'].apply(american_to_implied)
                result['away_implied'] = result['away_ml'].apply(american_to_implied)
                result['home_edge'] = result['home_win_prob'] - result['home_implied']
                result['away_edge'] = result['away_win_prob'] - result['away_implied']
                result['max_edge'] = result[['home_edge', 'away_edge']].max(axis=1)
                result['is_value'] = result['max_edge'] > value_threshold
            else:
                result['is_value'] = False
                result['max_edge'] = 0
        except:
            result['is_value'] = False
            result['max_edge'] = 0
        
        # NBA Player Stats (if BallDontLie works)
        if sport == 'NBA' and nba_data and not nba_data['games'].empty:
            st.markdown("---")
            st.subheader("🏀 NBA Player Data (BallDontLie)")
            with st.expander("View available games from BallDontLie"):
                st.dataframe(nba_data['games'][['home_team_name', 'visitor_team_name', 'date']].head(5), 
                          hide_index=True)
        
        # VALUE PICKS
        st.markdown("---")
        st.subheader(f"💎 Value Picks")
        
        value_picks = result[result['is_value'] == True]
        if not value_picks.empty:
            for _, pick in value_picks.head(5).iterrows():
                team = pick['home_team'] if pick['home_edge'] > pick['away_edge'] else pick['away_team']
                edge = max(pick['home_edge'], pick['away_edge']) * 100
                confidence = "High 💰" if edge > 8 else "Medium ⚡" if edge > 5 else "Low"
                
                with st.container():
                    st.markdown(f"""
                    <div class="value-pick">
                        <h3>🎯 {team} to Win</h3>
                        <p>{pick['home_team']} vs {pick['away_team']}</p>
                        <p>Model: {pick['home_win_prob']*100:.1f}% | Edge: +{edge:.1f}% | {confidence}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No value picks found. Adjust the threshold in sidebar.")
        
        # ALL PREDICTIONS
        st.markdown("### 📊 All Predictions")
        
        for _, row in result.head(8).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 3])
                
                with col1:
                    st.markdown(f"**{row['home_team']}**")
                    pct = int(row['home_win_prob'] * 100)
                    st.markdown(f"{pct}%")
                    st.progress(pct / 100)
                    if 'home_ml' in row and pd.notna(row['home_ml']):
                        st.caption(f"ML: {row['home_ml']:+}")
                
                with col2:
                    st.markdown("**VS**")
                    if row['is_value']:
                        st.markdown("💎")
                
                with col3:
                    st.markdown(f"**{row['away_team']}**")
                    pct = int(row['away_win_prob'] * 100)
                    st.markdown(f"{pct}%")
                    col3.progress(pct / 100)
                    if 'away_ml' in row and pd.notna(row['away_ml']):
                        st.caption(f"ML: {row['away_ml']:+}")
                
                st.markdown("---")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.caption(traceback.format_exc())

st.markdown("---")
st.caption("Powered by ESPN + BallDontLie + Universal Prediction Models")
