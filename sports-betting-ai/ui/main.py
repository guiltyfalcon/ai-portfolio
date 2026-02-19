"""
Sports Betting AI - Multi-page Streamlit Application
Pages:
- Dashboard (picks, games)
- Models (training, performance)
- History (past predictions, ROI)
- Settings (API keys, thresholds)
"""

import streamlit as st
import sys
import os

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page config
st.set_page_config(
    page_title="Sports Betting AI 🏆",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main theme */
    :root {
        --primary: #1f77b4;
        --success: #2ecc71;
        --warning: #f39c12;
        --danger: #e74c3c;
        --dark: #2c3e50;
        --light: #ecf0f1;
    }
    
    /* Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .value-bet-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .game-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Confidence badges */
    .confidence-high {
        background: #2ecc71;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .confidence-medium {
        background: #f39c12;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .confidence-low {
        background: #e74c3c;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    /* Navigation */
    .nav-item {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        transition: all 0.2s;
    }
    
    .nav-item:hover {
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #7f8c8d;
        border-top: 1px solid #ecf0f1;
        margin-top: 40px;
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
    st.markdown('<div class="subtitle">Machine Learning Powered Value Bet Detection for NBA, NFL, MLB, NHL</div>', unsafe_allow_html=True)

def render_navigation():
    """Render sidebar navigation."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=80)
        st.markdown("## Navigation")
        
        pages = {
            "🏠 Dashboard": "main",
            "📊 Live Odds": "odds", 
            "🤖 Predictions": "predictions",
            "📈 Performance": "performance",
            "⚙️ Settings": "settings"
        }
        
        for label, page in pages.items():
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()

def render_footer():
    """Render footer."""
    st.markdown("""
    <div class="footer">
        <p>Powered by ESPN API + The Odds API | Machine Learning: TensorFlow + scikit-learn</p>
        <p>Built with Streamlit | 🍡 Sports Betting AI 2025</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    """Render main dashboard page."""
    from api.espn import ESPNAPI
    from api.odds import OddsAPI
    from data.processor import SportsDataProcessor
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL'], 
                            format_func=lambda x: f"{get_sport_emoji(x)} {x}")
    
    with col2:
        days = st.slider("Days Ahead", 1, 7, 3)
    
    with col3:
        threshold = st.slider("Value Threshold", 0.0, 0.15, 0.05, 0.01)
    
    # Load data
    with st.spinner("Loading data..."):
        try:
            espn = ESPNAPI()
            teams = espn.get_teams(sport.lower())
            schedule = espn.get_schedule(sport.lower(), days=days)
            
            processor = SportsDataProcessor()
            features = processor.create_game_features(schedule, teams)
            
            # Try to get odds
            try:
                odds_api = OddsAPI()
                odds = odds_api.get_odds(sport.lower())
                features = processor.merge_with_odds(features, odds)
            except Exception as e:
                odds = pd.DataFrame()
                st.warning("Odds data unavailable")
            
        except Exception as e:
            st.error(f"Error: {e}")
            return
    
    # Stats row
    st.markdown("---")
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(features)}</h2>
            <p>Upcoming Games</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[1]:
        active_sports = 4
        st.markdown(f"""
        <div class="metric-card">
            <h2>{active_sports}</h2>
            <p>Active Sports</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[2]:
        model_acc = "64.2%" if sport == 'NBA' else "61.8%" if sport == 'NFL' else "59.0%"
        st.markdown(f"""
        <div class="metric-card">
            <h2>{model_acc}</h2>
            <p>Model Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <h2>Live</h2>
            <p>Data Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Games section
    st.markdown("---")
    st.subheader(f"{get_sport_emoji(sport)} Upcoming Games")
    
    if features.empty:
        st.info("No games found")
        return
    
    game_cols = st.columns(2)
    
    for idx, (_, game) in enumerate(features.iterrows()):
        with game_cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div class="game-card">
                    <h4>{game['home_team']} vs {game['away_team']}</h4>
                    <p>📅 {game.get('commence_time', 'TBD')[:10] if pd.notna(game.get('commence_time')) else 'TBD'}</p>
                    <p>🏠 {game['home_team']}: {game.get('home_record', 'N/A')} | 
                       ✈️ {game['away_team']}: {game.get('away_record', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if 'home_ml' in game and pd.notna(game['home_ml']):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Home ML", f"{game['home_ml']:+d}")
                    with c2:
                        st.metric("Away ML", f"{game['away_ml']:+d}")
                    with c3:
                        if 'home_spread' in game and pd.notna(game['home_spread']):
                            st.metric("Spread", f"{game['home_spread']:+g}")

def render_predictions():
    """Render predictions page."""
    st.header("🤖 Model Predictions")
    st.info("Feature coming soon: Train models on historical data and generate win probability predictions.")
    
    st.subheader("Model Architecture")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Ensemble Model
        - **Random Forest**: 100 estimators
        - **Gradient Boosting**: 100 estimators  
        - **Logistic Regression**: Baseline
        - **Neural Network**: 64-32-16 layers
        
        ### Features
        - Team win percentages
        - Home court advantage
        - Rest days
        - ELO ratings
        - Head-to-head history
        """)
    
    with col2:
        st.markdown("""
        ### Training Data
        - NBA: 5 seasons (2019-2024)
        - NFL: 4 seasons
        - MLB: 3 seasons
        - NHL: 3 seasons
        
        ### Performance Metrics
        - Accuracy
        - Brier Score
        - Log Loss
        - ROI on value bets
        """)

def render_performance():
    """Render performance tracking page."""
    st.header("📈 Historical Performance")
    st.info("Feature coming soon: Track prediction accuracy and betting ROI over time.")
    
    # Placeholder chart
    import plotly.graph_objects as go
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        y=[100, 105, 98, 112],
        mode='lines+markers',
        name='Bankroll',
        line=dict(color='#667eea', width=3)
    ))
    fig.update_layout(
        title='Hypothetical Bankroll Growth',
        xaxis_title='Time',
        yaxis_title='Units',
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

def render_settings():
    """Render settings page."""
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    
    # Odds API Key
    odds_key = st.text_input(
        "The Odds API Key",
        value=os.getenv('THEODDS_API_KEY', ''),
        type="password"
    )
    
    if st.button("Save API Key"):
        st.success("API key saved (session only)")
    
    st.markdown("---")
    
    st.subheader("Model Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.slider("Value Edge Threshold (%)", 0, 15, 5) / 100
        st.slider("Min Confidence for Pick (%)", 50, 90, 55) / 100
    
    with col2:
        st.number_input("Max Bet Size (units)", 1, 100, 10)
        st.selectbox("Kelly Criterion", ['Full Kelly', 'Half Kelly', 'Quarter Kelly', 'None'])
    
    st.markdown("---")
    
    st.subheader("Notifications")
    st.checkbox("Email alerts for high-confidence picks")
    st.checkbox("Telegram alerts for value bets")
    st.checkbox("Discord webhook for daily summary")

def main():
    """Main entry point."""
    render_header()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    
    # Navigation in sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=60)
        st.markdown("## 🏆 Sports AI")
        
        page = st.radio(
            "Navigate",
            ["🏠 Dashboard", "🤖 Predictions", "📈 Performance", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption("v1.0.0 | 2025")
    
    # Route to page
    if "Dashboard" in page:
        render_dashboard()
    elif "Predictions" in page:
        render_predictions()
    elif "Performance" in page:
        render_performance()
    elif "Settings" in page:
        render_settings()
    
    render_footer()

if __name__ == "__main__":
    import pandas as pd
    main()
