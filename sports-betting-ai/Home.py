"""
Sports Betting AI - Main Dashboard with Predictions
Live data from ESPN + The Odds API + ML Predictions
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
    .probability-bar {
        height: 20px;
        border-radius: 10px;
        background: #e0e0e0;
        margin: 5px 0;
    }
    .probability-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    return {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}.get(sport.lower(), '🏆')

def simple_prediction(home_win_pct, away_win_pct, home_advantage=0.03):
    """Simple heuristic prediction based on win % and home advantage."""
    home_prob = home_win_pct / (home_win_pct + away_win_pct + 0.0001) + home_advantage
    return min(max(home_prob, 0.1), 0.9)  # Clamp between 10-90%

def american_to_implied_prob(odds):
    """Convert American odds to implied probability."""
    if pd.isna(odds):
        return 0.5
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

# Title
st.markdown('<div class="main-header">🏆 Sports Betting AI</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666;">Live Predictions + Value Bet Detection</div>', unsafe_allow_html=True)
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
    value_threshold = st.slider("Value Edge %", 1, 10, 5) / 100
    
    st.markdown("---")
    st.markdown("### 📊 Model Info")
    st.markdown("**Current Model**: Heuristic (Win % + Home Advantage)")
    st.markdown("**Training**: Historical data coming soon")
    
    st.markdown("---")
    st.caption("Built with Streamlit + scikit-learn 🍡")

# Load data
try:
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    
    espn = ESPNAPI()
    
    with st.spinner(f"Loading {sport} data..."):
        teams = espn.get_teams(sport.lower())
        schedule = espn.get_schedule(sport.lower(), days=days)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Teams", len(teams))
        with col2:
            st.metric("Upcoming Games", len(schedule))
        with col3:
            st.metric("Data Source", "ESPN ✓")
        
        # Fetch odds
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport.lower())
            odds_loaded = True
        except Exception as e:
            odds = pd.DataFrame()
            odds_loaded = False
        
        # PREDICTIONS SECTION
        st.markdown("---")
        st.subheader(f"🎯 {get_sport_emoji(sport)} Today's Predictions")
        
        if schedule.empty:
            st.info(f"No {sport} games scheduled in the next {days} days.")
        else:
            # Process each game
            predictions = []
            
            for _, game in schedule.iterrows():
                # Get win percentages from records
                home_rec = game.get('home_record', '0-0')
                away_rec = game.get('away_record', '0-0')
                
                try:
                    hw, hl = map(int, home_rec.split('-')) if '-' in str(home_rec) else (0, 0)
                    aw, al = map(int, away_rec.split('-')) if '-' in str(away_rec) else (0, 0)
                    home_win_pct = hw / (hw + hl) if (hw + hl) > 0 else 0.5
                    away_win_pct = aw / (aw + al) if (aw + al) > 0 else 0.5
                except:
                    home_win_pct, away_win_pct = 0.5, 0.5
                
                # Predict
                home_prob = simple_prediction(home_win_pct, away_win_pct)
                away_prob = 1 - home_prob
                
                # Find odds for this game
                game_odds = odds[
                    (odds['home_team'] == game['home_team']) | 
                    (odds['away_team'] == game['away_team'])
                ] if not odds.empty else pd.DataFrame()
                
                if not game_odds.empty:
                    gm = game_odds.iloc[0]
                    home_ml = gm.get('home_ml', None)
                    away_ml = gm.get('away_ml', None)
                    home_implied = american_to_implied_prob(home_ml) if home_ml else home_prob
                    away_implied = american_to_implied_prob(away_ml) if away_ml else away_prob
                    
                    # Calculate value
                    home_edge = home_prob - home_implied
                    away_edge = away_prob - away_implied
                    
                    has_value = home_edge > value_threshold or away_edge > value_threshold
                    value_pick = game['home_team'] if home_edge > away_edge else game['away_team']
                    value_edge = max(home_edge, away_edge)
                else:
                    home_implied, away_implied = 0.5, 0.5
                    has_value = False
                    value_pick = None
                    value_edge = 0
                    home_ml, away_ml = None, None
                
                predictions.append({
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'home_win_prob': home_prob,
                    'away_win_prob': away_prob,
                    'home_ml': home_ml,
                    'away_ml': away_ml,
                    'home_implied': home_implied,
                    'away_implied': away_implied,
                    'has_value': has_value,
                    'value_pick': value_pick,
                    'value_edge': value_edge
                })
            
            # Display predictions
            pred_df = pd.DataFrame(predictions)
            
            # VALUE PICKS
            value_picks = pred_df[pred_df['has_value'] == True]
            if not value_picks.empty:
                st.markdown("### 💎 Value Picks (Model > Market)")
                for _, pick in value_picks.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="value-pick">
                            <h3>🎯 {pick['value_pick']} to Win</h3>
                            <p>{pick['home_team']} vs {pick['away_team']}</p>
                            <p>Model: {pick['home_win_prob']*100 if pick['value_pick'] == pick['home_team'] else pick['away_win_prob']*100:.1f}% | 
                               Market: {(1-pick['value_edge'])*100 if pick['value_pick'] != pick['home_team'] else pick['home_implied']*100:.1f}% | 
                               Edge: +{pick['value_edge']*100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # ALL PREDICTIONS
            st.markdown("### 📊 All Game Predictions")
            for _, pred in pred_df.head(8).iterrows():
                with st.container():
                    home_pct = pred['home_win_prob'] * 100
                    away_pct = pred['away_win_prob'] * 100
                    
                    col1, col2, col3 = st.columns([3, 1, 3])
                    with col1:
                        st.markdown(f"**{pred['home_team']}**")
                        st.markdown(f"{home_pct:.1f}%")
                        if pd.notna(pred['home_ml']):
                            st.caption(f"ML: {pred['home_ml']:+}")
                    with col2:
                        st.markdown(f"**VS**")
                        winner = "🏠" if home_pct > away_pct else "✈️"
                        st.markdown(f"{winner}")
                    with col3:
                        st.markdown(f"**{pred['away_team']}**")
                        st.markdown(f"{away_pct:.1f}%")
                        if pd.notna(pred['away_ml']):
                            st.caption(f"ML: {pred['away_ml']:+}")
                    
                    st.markdown("---")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.caption("Powered by ESPN API + The Odds API | Built with Streamlit")
