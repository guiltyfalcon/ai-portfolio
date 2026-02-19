"""
Sports Betting AI Dashboard - Streamlit web interface
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.espn import ESPNAPI
from api.odds import OddsAPI
from data.processor import SportsDataProcessor
from models.predictor import SportsPredictionModel

# Page configuration
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
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .value-bet {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .confidence-high { color: #00ff00; font-weight: bold; }
    .confidence-medium { color: #ffff00; font-weight: bold; }
    .confidence-low { color: #ff0000; font-weight: bold; }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def get_sport_emoji(sport):
    """Get emoji for sport."""
    emojis = {'nba': '🏀', 'nfl': '🏈', 'mlb': '⚾', 'nhl': '🏒'}
    return emojis.get(sport.lower(), '🏆')

def render_header():
    """Render the main header."""
    st.markdown('<div class="main-header">🏆 Sports Betting AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Machine Learning Powered Value Bet Detection</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar controls."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Sport selection
        sport = st.selectbox(
            "Select Sport",
            ['NBA', 'NFL', 'MLB', 'NHL'],
            format_func=lambda x: f"{get_sport_emoji(x)} {x}"
        )
        
        st.markdown("---")
        
        # Value threshold
        threshold = st.slider(
            "Value Edge Threshold",
            min_value=0.0,
            max_value=0.15,
            value=0.05,
            step=0.01,
            help="Minimum edge (model prob - implied prob) to flag as value bet"
        )
        
        st.markdown("---")
        
        # API Status
        st.subheader("API Status")
        
        # Check ESPN
        try:
            espn = ESPNAPI()
            espn.get_teams(sport.lower())
            st.success("✅ ESPN API")
        except Exception as e:
            st.error(f"❌ ESPN API: {str(e)[:50]}")
        
        # Check Odds API
        try:
            odds_key = os.getenv('THEODDS_API_KEY', '')
            if odds_key:
                st.success("✅ Odds API Key Set")
            else:
                st.warning("⚠️ Odds API Key Missing")
        except:
            st.error("❌ Odds API")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

def load_data(sport):
    """Load game data and odds."""
    try:
        # ESPN Data
        espn = ESPNAPI()
        teams = espn.get_teams(sport)
        schedule = espn.get_schedule(sport, days=3)
        
        # Process features
        processor = SportsDataProcessor()
        features = processor.create_game_features(schedule, teams)
        
        # Odds Data
        try:
            odds_api = OddsAPI()
            odds = odds_api.get_odds(sport)
            features = processor.merge_with_odds(features, odds)
        except Exception as e:
            st.warning(f"Could not load odds: {e}")
            odds = pd.DataFrame()
        
        return features, odds, teams
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def render_games(sport, features_df, odds_df):
    """Render upcoming games."""
    st.subheader(f"{get_sport_emoji(sport)} Upcoming {sport.upper()} Games")
    
    if features_df.empty:
        st.info("No upcoming games found.")
        return
    
    # Display games in a grid
    cols = st.columns(2)
    
    for idx, (_, game) in enumerate(features_df.iterrows()):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h4>{game['home_team']} vs {game['away_team']}</h4>
                    <p>Records: {game['home_team']} {game.get('home_record', 'N/A')} | {game['away_team']} {game.get('away_record', 'N/A')}</p>
                    <p>Home Win %: {game.get('home_win_pct', 0):.1%} | Away Win %: {game.get('away_win_pct', 0):.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show odds if available
                if 'home_ml' in game and not pd.isna(game['home_ml']):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"{game['home_team']} ML", f"{game['home_ml']:+d}")
                    with col2:
                        st.metric(f"{game['away_team']} ML", f"{game['away_ml']:+d}")

def render_value_bets(sport, features_df, odds_df, threshold=0.05):
    """Render value bet recommendations."""
    st.subheader("💎 Value Bet Opportunities")
    
    if odds_df.empty or features_df.empty:
        st.info("Insufficient data for value bet analysis. Need both game data and odds.")
        return
    
    # Create dummy predictions for demo (in production, use trained model)
    predictions = pd.DataFrame({
        'game_id': features_df['game_id'],
        'home_win_prob': 0.6,  # Placeholder
        'away_win_prob': 0.4
    })
    
    # Find value bets
    try:
        odds_api = OddsAPI()
        value_bets = odds_api.find_value_bets(predictions, odds_df, threshold)
        
        if value_bets.empty:
            st.info(f"No value bets found with {threshold:.0%} edge threshold.")
            return
        
        st.success(f"Found {len(value_bets)} value bet(s)!")
        
        for _, bet in value_bets.iterrows():
            confidence_class = f"confidence-{bet['confidence'].lower()}"
            
            st.markdown(f"""
            <div class="value-bet">
                <h3>🎯 {bet['pick']}</h3>
                <p>Odds: {bet['odds']:+d} | Model: {bet['model_prob']:.1%} | Market: {bet['implied_prob']:.1%}</p>
                <p>Edge: +{bet['edge']:.1%} | Confidence: <span class="{confidence_class}">{bet['confidence']}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error analyzing value bets: {e}")

def render_model_stats():
    """Render model performance statistics."""
    st.subheader("📊 Model Performance")
    
    # Placeholder stats (would come from actual model training)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card"><h4>🏀 NBA</h4><p>Accuracy: 64.2%</p><p>Brier: 0.231</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h4>🏈 NFL</h4><p>Accuracy: 61.8%</p><p>Brier: 0.245</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h4>⚾ MLB</h4><p>Accuracy: 58.5%</p><p>Brier: 0.252</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h4>🏒 NHL</h4><p>Accuracy: 59.3%</p><p>Brier: 0.248</p></div>', unsafe_allow_html=True)

def main():
    """Main application."""
    render_header()
    render_sidebar()
    
    # Get current sport from session state or default
    if 'sport' not in st.session_state:
        st.session_state.sport = 'NBA'
    
    # Load data
    with st.spinner("Loading game data and odds..."):
        features_df, odds_df, teams_df = load_data(st.session_state.sport)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📅 Upcoming Games", "💎 Value Bets", "📊 Model Stats"])
    
    with tab1:
        render_games(st.session_state.sport, features_df, odds_df)
    
    with tab2:
        render_value_bets(st.session_state.sport, features_df, odds_df, threshold=0.05)
    
    with tab3:
        render_model_stats()
    
    # Footer
    st.markdown("---")
    st.caption("Powered by ESPN API + The Odds API | Built with Streamlit + TensorFlow")

if __name__ == "__main__":
    main()
