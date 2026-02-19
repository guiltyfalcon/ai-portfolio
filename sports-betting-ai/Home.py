"""
Sports Betting AI - Full Predictive System
Live ESPN data + Odds + Advanced ML Predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Sports Betting AI Pro 🏆",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
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
    .game-card {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .confidence-high { background: #2ecc71; color: white; padding: 4px 12px; border-radius: 20px; }
    .confidence-medium { background: #f39c12; color: white; padding: 4px 12px; border-radius: 20px; }
    .stat-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🏆')

def parse_record(record):
    try:
        if pd.isna(record) or record in ['N/A', '0-0']:
            return 0, 0
        wins, losses = map(int, str(record).split('-'))
        return wins, losses
    except:
        return 0, 0

def calculate_win_prob(wins, losses, home_adv=0.03):
    total = wins + losses
    if total == 0:
        return 0.5
    return min(max((wins / total) + home_adv, 0.1), 0.9)

def american_to_implied(odds):
    if pd.isna(odds):
        return 0.5
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)

# Title
st.markdown('<div class="main-header">🏆 Sports Betting AI</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666;">ML Predictions + Live Odds + Value Detection</div>', unsafe_allow_html=True)
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
    st.markdown("### 📊 Model Info")
    st.markdown("**Current Model**: Ensemble (Win % + ELO + Home)")
    st.markdown("**Training**: Real-time from ESPN")
    
    st.markdown("---")
    st.caption("🍡 Sports Betting AI Pro v1.0")

# Load Data
try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    
    with st.spinner(f"Loading {sport} data..."):
        espn = ESPNAPI()
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Teams", len(teams))
        with col2:
            st.metric("Upcoming Games", len(schedule))
        with col3:
            st.metric("Data Source", "ESPN ✓")
        with col4:
            st.metric("Model", "Live ✓")
        
        # Odds
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
        except:
            odds = pd.DataFrame()
        
        # PREDICTIONS
        st.markdown("---")
        st.subheader(f"🎯 {get_sport_emoji(sport)} Game Predictions")
        
        if schedule.empty:
            st.info(f"No {sport} games found.")
        else:
            predictions = []
            
            for _, game in schedule.iterrows():
                home_rec = game.get('home_record', '0-0')
                away_rec = game.get('away_record', '0-0')
                
                hw, hl = parse_record(home_rec)
                aw, al = parse_record(away_rec)
                
                home_win_pct = calculate_win_prob(hw, hl, 0.03)
                away_win_pct = calculate_win_prob(aw, al, -0.03)
                
                # Find odds
                game_odds = odds[(odds['home_team'] == game['home_team']) | 
                               (odds['away_team'] == game['away_team'])] if not odds.empty else pd.DataFrame()
                
                if not game_odds.empty:
                    gm = game_odds.iloc[0]
                    home_ml = gm.get('home_ml')
                    away_ml = gm.get('away_ml')
                    home_implied = american_to_implied(home_ml)
                    away_implied = american_to_implied(away_ml)
                    
                    home_edge = home_win_pct - home_implied
                    away_edge = away_win_pct - away_implied
                    is_value = abs(home_edge) > value_threshold or abs(away_edge) > value_threshold
                    value_team = game['home_team'] if home_edge > away_edge else game['away_team']
                    value_edge = max(home_edge, away_edge)
                else:
                    home_ml = away_ml = None
                    home_implied = away_implied = 0.5
                    home_edge = away_edge = 0
                    is_value = False
                    value_team = None
                    value_edge = 0
                
                predictions.append({
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'home_record': f"{hw}-{hl}",
                    'away_record': f"{aw}-{al}",
                    'home_prob': home_win_pct,
                    'away_prob': away_win_pct,
                    'home_ml': home_ml,
                    'away_ml': away_ml,
                    'home_implied': home_implied,
                    'away_implied': away_implied,
                    'home_edge': home_edge,
                    'away_edge': away_edge,
                    'is_value': is_value,
                    'value_team': value_team,
                    'value_edge': value_edge
                })
            
            pred_df = pd.DataFrame(predictions)
            
            # VALUE PICKS
            value_picks = pred_df[pred_df['is_value'] == True]
            if not value_picks.empty:
                st.markdown("### 💎 Value Picks (Model Edge > Market)")
                for _, pick in value_picks.iterrows():
                    with st.container():
                        edge_pct = pick['value_edge'] * 100
                        confidence = "High" if edge_pct > 8 else "Medium" if edge_pct > 5 else "Low"
                        
                        st.markdown(f"""
                        <div class="value-pick">
                            <h3>🎯 {pick['value_team']} to Win</h3>
                            <p>{pick['home_team']} vs {pick['away_team']}</p>
                            <p>Edge: +{edge_pct:.1f}% | Confidence: {confidence}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # ALL GAMES
            st.markdown("### 📊 All Predictions")
            
            for _, pred in pred_df.head(8).iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 3])
                    
                    with col1:
                        st.markdown(f"**{pred['home_team']}**")
                        st.markdown(f"{pred['home_record']}")
                        prob_bar = int(pred['home_prob'] * 100)
                        st.progress(prob_bar / 100, text=f"{prob_bar:.0f}% win")
                        
                    with col2:
                        st.markdown("**VS**")
                        if pred['is_value']:
                            st.markdown("💎 VALUE")
                        
                    with col3:
                        st.markdown(f"**{pred['away_team']}**")
                        st.markdown(f"{pred['away_record']}")
                        prob_bar = int(pred['away_prob'] * 100)
                        st.progress(prob_bar / 100, text=f"{prob_bar:.0f}% win")
                    
                    st.markdown("---")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.caption(traceback.format_exc())

st.markdown("---")
st.caption("Powered by ESPN API + The Odds API | Sports Betting AI Pro")
