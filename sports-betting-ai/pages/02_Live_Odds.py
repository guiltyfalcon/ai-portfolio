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
        font-weight: 700; color: #00d2ff; font-size: 1.1rem;
    }
    .odds-label {
        font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px;
    }
    .best-odds {
        background: rgba(46,204,113,0.2); border-color: rgba(46,204,113,0.5); color: #2ecc71;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Live Odds</div>', unsafe_allow_html=True)

sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL'])

# Bookmaker selector - mapped to API keys
bookmaker_map = {
    'DraftKings': 'draftkings',
    'FanDuel': 'fanduel', 
    'BetMGM': 'betmgm',
    'Pinnacle': 'pinnacle'
}
col1, col2 = st.columns([3, 1])
with col2:
    selected_book_display = st.selectbox("Bookmaker", list(bookmaker_map.keys()))
    selected_book = bookmaker_map[selected_book_display]

odds_api = OddsAPI()
if not odds_api.is_configured():
    st.warning("⚠️ Add THEODDS_API_KEY to secrets for live odds")
    st.info("Get free API key at: https://the-odds-api.com/")

try:
    with st.spinner(f"Loading {selected_book_display} odds..."):
        odds_df = odds_api.get_odds(sport.lower(), bookmaker=selected_book) if odds_api.is_configured() else pd.DataFrame()
    
    if not odds_df.empty:
        # Show which bookmaker we're displaying
        actual_bookmaker = odds_df['bookmaker'].iloc[0] if 'bookmaker' in odds_df.columns else selected_book_display
        st.success(f"✅ Loaded {len(odds_df)} games from {actual_bookmaker}")
        
        for _, game in odds_df.head(10).iterrows():
            # Get spread - could be home or away
            spread_val = game.get('home_spread') or game.get('away_spread')
            spread_str = f"{spread_val:+}" if spread_val else "N/A"
            
            # Get total
            total_val = game.get('total')
            total_str = f"{total_val}" if pd.notna(total_val) else "N/A"
            
            # Get moneyline odds
            home_ml = game.get('home_ml')
            away_ml = game.get('away_ml')
            home_ml_str = f"{int(home_ml)}" if pd.notna(home_ml) else "N/A"
            away_ml_str = f"{int(away_ml)}" if pd.notna(away_ml) else "N/A"
            
            # Calculate implied win probability
            def american_to_prob(odds):
                if pd.isna(odds): return 0.5
                if odds > 0: return 100 / (odds + 100)
                return abs(odds) / (abs(odds) + 100)
            
            home_prob = american_to_prob(home_ml) * 100 if pd.notna(home_ml) else 50
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Game info
                st.markdown(f"""
                <div class="odds-card">
                    <h4 style="margin:0;color:#fff;">{game['home_team']} vs {game['away_team']}</h4>
                    <p style="color:#888;margin:5px 0;font-size:0.9rem;">{game.get('commence_time', 'TBD')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Odds display
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"""
                        <div class="odds-box">
                            <div class="odds-label">Spread</div>
                            {spread_str}
                        </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"""
                        <div class="odds-box">
                            <div class="odds-label">Home ML</div>
                            {home_ml_str}
                            <div style="font-size:0.75rem;color:#888;">{home_prob:.0f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"""
                        <div class="odds-box">
                            <div class="odds-label">O/U</div>
                            {total_str}
                        </div>
                    """, unsafe_allow_html=True)
    else:
        if odds_api.is_configured():
            st.info("No live odds currently available. The Odds API may have no active games.")
        else:
            # Show sample data
            st.info("💡 Showing sample format - add THEODDS_API_KEY for live data")
            sample_games = [
                {"home": "Lakers", "away": "Warriors", "spread": "-4.5", "ml": "-180", "total": "225.5"},
                {"home": "Celtics", "away": "Heat", "spread": "-7.5", "ml": "-300", "total": "218.5"},
            ]
            for game in sample_games:
                cols = st.columns([1, 2])
                with cols[0]:
                    st.markdown(f"""
                    <div class="odds-card" style="opacity:0.5;">
                        <h4>{game['home']} vs {game['away']}</h4>
                        <p style="color:#888;">Sample Game</p>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    c = st.columns(3)
                    c[0].markdown(f'<div class="odds-box" style="opacity:0.5;">Spread<br/>{game["spread"]}</div>', unsafe_allow_html=True)
                    c[1].markdown(f'<div class="odds-box" style="opacity:0.5;">ML<br/>{game["ml"]}</div>', unsafe_allow_html=True)
                    c[2].markdown(f'<div class="odds-box" style="opacity:0.5;">O/U<br/>{game["total"]}</div>', unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Error loading odds: {e}")
    st.info("📚 Make sure THEODDS_API_KEY is set in your Streamlit secrets")
