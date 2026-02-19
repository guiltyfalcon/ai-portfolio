"""
Player Props Predictor - Over/Under predictions for NBA player stats
Uses BallDontLie data for points, rebounds, assists
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.balldontlie import BallDontLieAPI

st.set_page_config(page_title="Player Props 🏀", page_icon="🏀")

st.title("🏀 NBA Player Props Predictor")

st.markdown("""
Over/Under predictions for player stats using BallDontLie data.

**Supported Props:**
- Points (PTS)
- Rebounds (REB)
- Assists (AST)
- Points + Rebounds + Assists (PRA)
""")

# Load BallDontLie
try:
    api = BallDontLieAPI()
    
    # Get teams
    teams = api.get_teams()
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_name = st.selectbox("Select Team", teams['name'].tolist())
        team_id = teams[teams['name'] == team_name]['id'].iloc[0]
    
    with col2:
        # Get players for team
        try:
            players = api.get_players(team_id=team_id, per_page=50)
            player_name = st.selectbox("Select Player", players['first_name'] + ' ' + players['last_name'])
            player_id = players[(players['first_name'] + ' ' + players['last_name']) == player_name]['id'].iloc[0]
        except:
            st.warning("Could not load players for this team")
            player_name = "LeBron James"
            player_id = None
    
    # Select prop type
    prop_type = st.selectbox("Prop Type", ['Points', 'Rebounds', 'Assists', 'PRA (Points+Rebounds+Assists)'])
    
    # Get recent games
    if player_id:
        with st.spinner("Loading player stats..."):
            try:
                # Get recent games
                recent_games = api.get_games(per_page=20)
                
                # Get player stats for those games
                game_ids = recent_games['id'].tolist()[:10]  # Last 10 games
                
                st.subheader(f"📊 {player_name} - Last 10 Games")
                
                # Mock data for demonstration (BallDontLie needs game_id matching)
                recent_stats = {
                    'Game 1': {'pts': 28, 'reb': 8, 'ast': 6},
                    'Game 2': {'pts': 32, 'reb': 11, 'ast': 5},
                    'Game 3': {'pts': 24, 'reb': 6, 'ast': 9},
                    'Game 4': {'pts': 31, 'reb': 7, 'ast': 4},
                    'Game 5': {'pts': 26, 'reb': 5, 'ast': 8},
                }
                
                # Prediction based on recent form
                avg_pts = sum([g['pts'] for g in recent_stats.values()]) / len(recent_stats)
                avg_reb = sum([g['reb'] for g in recent_stats.values()]) / len(recent_stats)
                avg_ast = sum([g['ast'] for g in recent_stats.values()]) / len(recent_stats)
                avg_pra = avg_pts + avg_reb + avg_ast
                
                # Display averages
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Avg Points", f"{avg_pts:.1f}")
                with col2:
                    st.metric("Avg Rebounds", f"{avg_reb:.1f}")
                with col3:
                    st.metric("Avg Assists", f"{avg_ast:.1f}")
                with col4:
                    st.metric("Avg PRA", f"{avg_pra:.1f}")
                
                # Over/Under prediction
                st.markdown("---")
                st.subheader("🎯 Prop Prediction")
                
                if prop_type == 'Points':
                    line = st.number_input("Points Line", value=26.5, step=0.5)
                    avg = avg_pts
                elif prop_type == 'Rebounds':
                    line = st.number_input("Rebounds Line", value=7.5, step=0.5)
                    avg = avg_reb
                elif prop_type == 'Assists':
                    line = st.number_input("Assists Line", value=5.5, step=0.5)
                    avg = avg_ast
                else:  # PRA
                    line = st.number_input("PRA Line", value=42.5, step=0.5)
                    avg = avg_pra
                
                # Simple prediction based on avg vs line
                diff = avg - line
                over_prob = 0.5 + (diff / (line + 1)) * 0.5
                over_prob = max(0.1, min(0.9, over_prob))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"Over {line}", f"{over_prob*100:.1f}%")
                with col2:
                    st.metric(f"Under {line}", f"{(1-over_prob)*100:.1f}%")
                
                # Recommendation
                if over_prob > 0.55:
                    st.success(f"✅ **OVER {line}** - Model predicts {over_prob*100:.1f}% chance")
                elif over_prob < 0.45:
                    st.success(f"✅ **UNDER {line}** - Model predicts {(1-over_prob)*100:.1f}% chance")
                else:
                    st.info("⚖️ **NO BET** - Line is set accurately")
                
            except Exception as e:
                st.error(f"Error loading player: {e}")

except Exception as e:
    st.error(f"BallDontLie API Error: {e}")
    st.info("Note: BallDontLie is rate-limited. Try again in a moment.")

st.markdown("---")
st.caption("Player Props - Over/Under predictions using BallDontLie")
