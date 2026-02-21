"""
Parlay Builder Page - Build your perfect parlay
"""
import streamlit as st
import requests

st.set_page_config(page_title="Parlay Builder - Sports Betting AI Pro", page_icon="🎯", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

# Shared Navigation Function
def show_page_nav():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="
                width: 40px; 
                height: 40px; 
                margin: 0 auto 0.5rem;
                background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
            ">🎯</div>
            <h4 style="margin: 0; color: white; font-size: 1rem;">Sports Betting AI</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⊕  Dashboard", use_container_width=True):
            st.switch_page("Home.py")
        if st.button("◈  Odds", use_container_width=True):
            st.switch_page("pages/Live_Odds.py")
        if st.button("❖  Props", use_container_width=True):
            st.switch_page("pages/Player_Props.py")
        if st.button("⛓  Parlay", use_container_width=True):
            st.switch_page("pages/Parlay_Builder.py")
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1rem 0;'>", unsafe_allow_html=True)
        
        if st.button("○  Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

show_page_nav()

# ESPN API Functions
def fetch_espn_games(sport="nba"):
    """Fetch live games from ESPN API"""
    try:
        sport_paths = {
            "nba": "basketball/nba",
            "nfl": "football/nfl",
            "mlb": "baseball/mlb",
            "nhl": "hockey/nhl",
            "ncaab": "basketball/mens-college-basketball",
            "ncaaf": "football/college-football"
        }
        sport_path = sport_paths.get(sport.lower(), "basketball/nba")
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/scoreboard"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = []
            for event in data.get('events', [])[:6]:
                home_team = event['competitions'][0]['competitors'][0]['team']['displayName']
                away_team = event['competitions'][0]['competitors'][1]['team']['displayName']
                status = event.get('status', {}).get('type', {}).get('state', 'pre')
                
                games.append({
                    'id': event['id'],
                    'sport': sport.upper(),
                    'home': home_team,
                    'away': away_team,
                    'home_short': home_team.split()[-1],
                    'away_short': away_team.split()[-1],
                    'ml_home': -140,
                    'ml_away': 120,
                    'spread': -3.5,
                    'spread_odds': -110,
                    'total': 228.5,
                    'total_odds': -110,
                    'time': event.get('status', {}).get('shortDetail', 'TBD'),
                    'status': 'live' if status == 'in' else 'upcoming',
                    'players': get_mock_players(sport, home_team, away_team)
                })
            return games
    except Exception as e:
        print(f"Error fetching ESPN data: {e}")
    return []

def get_mock_players(sport, home_team, away_team):
    """Generate mock player props for games"""
    players = []
    
    if sport.upper() == "NBA":
        players = [
            {"name": "LeBron James", "team": home_team, "points_line": 26.5, "rebounds_line": 7.5, "assists_line": 8.5},
            {"name": "Stephen Curry", "team": away_team, "points_line": 28.5, "rebounds_line": 4.5, "assists_line": 6.5},
            {"name": "Anthony Davis", "team": home_team, "points_line": 24.5, "rebounds_line": 11.5, "assists_line": 3.5},
            {"name": "Klay Thompson", "team": away_team, "points_line": 18.5, "rebounds_line": 3.5, "assists_line": 2.5},
        ]
    elif sport.upper() == "NFL":
        players = [
            {"name": "Patrick Mahomes", "team": home_team, "pass_yards_line": 285.5, "tds_line": 2.5, "rush_yards_line": 25.5},
            {"name": "Brock Purdy", "team": away_team, "pass_yards_line": 265.5, "tds_line": 1.5, "rush_yards_line": 15.5},
            {"name": "Travis Kelce", "team": home_team, "rec_yards_line": 75.5, "tds_line": 0.5, "receptions_line": 6.5},
            {"name": "Christian McCaffrey", "team": away_team, "rush_yards_line": 85.5, "tds_line": 0.5, "rec_yards_line": 35.5},
        ]
    elif sport.upper() == "NHL":
        players = [
            {"name": "Auston Matthews", "team": home_team, "points_line": 1.5, "goals_line": 0.5, "shots_line": 4.5},
            {"name": "Nathan MacKinnon", "team": away_team, "points_line": 1.5, "goals_line": 0.5, "shots_line": 4.5},
        ]
    elif sport.upper() == "MLB":
        players = [
            {"name": "Shohei Ohtani", "team": home_team, "hits_line": 1.5, "runs_line": 0.5, "rbis_line": 0.5},
            {"name": "Aaron Judge", "team": away_team, "hits_line": 1.5, "home_runs_line": 0.5, "rbis_line": 0.5},
        ]
    
    return players

# Initialize session state
if 'parlay_legs' not in st.session_state:
    st.session_state.parlay_legs = []
if 'parlay_sport' not in st.session_state:
    st.session_state.parlay_sport = 'NBA'

st.markdown("<h1>Parlay Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Build your perfect parlay with AI insights</p>", unsafe_allow_html=True)

# Sport Selector
sport_cols = st.columns([1, 3])
with sport_cols[0]:
    st.markdown("<p style='color: #8A8F98; margin-bottom: 0.5rem;'>Select Sport</p>", unsafe_allow_html=True)
    selected_sport = st.selectbox("Sport", ["🏀 NBA", "🏈 NFL", "⚾ MLB", "🏒 NHL", "🏀 NCAAB", "🏈 NCAAF"], 
                                   index=["NBA", "NFL", "MLB", "NHL", "NCAAB", "NCAAF"].index(st.session_state.parlay_sport) if st.session_state.parlay_sport in ["NBA", "NFL", "MLB", "NHL", "NCAAB", "NCAAF"] else 0,
                                   label_visibility="collapsed")
    st.session_state.parlay_sport = selected_sport.split()[-1]

with sport_cols[1]:
    st.markdown("<p style='color: #8A8F98; margin-bottom: 0.5rem;'>&nbsp;</p>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Games", use_container_width=True):
        st.rerun()

# Fetch games
with st.spinner("Loading games..."):
    games = fetch_espn_games(st.session_state.parlay_sport.lower())

# Tabs for different bet types
tab_games, tab_players = st.tabs(["📊 Game Lines", "🏃 Player Props"])

col1, col2 = st.columns([2, 1])

with col1:
    with tab_games:
        if games:
            st.markdown(f"<h3>Available {st.session_state.parlay_sport} Games</h3>", unsafe_allow_html=True)
            
            for game in games:
                with st.expander(f"🏀 {game['home']} vs {game['away']} ({game['time']})"):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown("<p style='color: #00d2ff; font-size: 0.75rem; font-weight: 600;'>MONEYLINE</p>", unsafe_allow_html=True)
                        if st.button(f"{game['home']} {game['ml_home']}", key=f"ml_home_{game['id']}", use_container_width=True):
                            st.session_state.parlay_legs.append({
                                "id": len(st.session_state.parlay_legs),
                                "selection": f"{game['home']} ML",
                                "odds": game['ml_home'],
                                "game": f"{game['home']} vs {game['away']}",
                                "type": "Moneyline"
                            })
                            st.rerun()
                        if st.button(f"{game['away']} {game['ml_away']}", key=f"ml_away_{game['id']}", use_container_width=True):
                            st.session_state.parlay_legs.append({
                                "id": len(st.session_state.parlay_legs),
                                "selection": f"{game['away']} ML",
                                "odds": game['ml_away'],
                                "game": f"{game['home']} vs {game['away']}",
                                "type": "Moneyline"
                            })
                            st.rerun()
                    
                    with col_b:
                        st.markdown("<p style='color: #00d2ff; font-size: 0.75rem; font-weight: 600;'>SPREAD</p>", unsafe_allow_html=True)
                        if st.button(f"{game['home']} {game['spread']}", key=f"spread_home_{game['id']}", use_container_width=True):
                            st.session_state.parlay_legs.append({
                                "id": len(st.session_state.parlay_legs),
                                "selection": f"{game['home']} {game['spread']}",
                                "odds": game['spread_odds'],
                                "game": f"{game['home']} vs {game['away']}",
                                "type": "Spread"
                            })
                            st.rerun()
                        if st.button(f"{game['away']} +{abs(game['spread'])}", key=f"spread_away_{game['id']}", use_container_width=True):
                            st.session_state.parlay_legs.append({
                                "id": len(st.session_state.parlay_legs),
                                "selection": f"{game['away']} +{abs(game['spread'])}",
                                "odds": game['spread_odds'],
                                "game": f"{game['home']} vs {game['away']}",
                                "type": "Spread"
                            })
                            st.rerun()
                    
                    with col_c:
                        st.markdown("<p style='color: #00d2ff; font-size: 0.75rem; font-weight: 600;'>TOTAL</p>", unsafe_allow_html=True)
                        if st.button(f"Over {game['total']}", key=f"over_{game['id']}", use_container_width=True):
                            st.session_state.parlay_legs.append({
                                "id": len(st.session_state.parlay_legs),
                                "selection": f"Over {game['total']}",
                                "odds": game['total_odds'],
                                "game": f"{game['home']} vs {game['away']}",
                                "type": "Total"
                            })
                            st.rerun()
                        if st.button(f"Under {game['total']}", key=f"under_{game['id']}", use_container_width=True):
                            st.session_state.parlay_legs.append({
                                "id": len(st.session_state.parlay_legs),
                                "selection": f"Under {game['total']}",
                                "odds": game['total_odds'],
                                "game": f"{game['home']} vs {game['away']}",
                                "type": "Total"
                            })
                            st.rerun()
        else:
            st.info("No games found for this sport. Try another sport or check back later.")
    
    with tab_players:
        if games:
            st.markdown(f"<h3>{st.session_state.parlay_sport} Player Props</h3>", unsafe_allow_html=True)
            
            for game in games:
                with st.expander(f"🏀 {game['home']} vs {game['away']} - Player Props"):
                    if game.get('players'):
                        for player in game['players']:
                            st.markdown(f"<p style='color: white; font-weight: 600; margin-top: 1rem;'>{player['name']} ({player['team']})</p>", unsafe_allow_html=True)
                            
                            prop_cols = st.columns(3)
                            
                            if st.session_state.parlay_sport == 'NBA':
                                with prop_cols[0]:
                                    if st.button(f"Points O/U {player['points_line']}", key=f"pts_{player['name']}_{game['id']}", use_container_width=True):
                                        st.session_state.parlay_legs.append({
                                            "id": len(st.session_state.parlay_legs),
                                            "selection": f"{player['name']} Over {player['points_line']} Pts",
                                            "odds": -110,
                                            "game": f"{game['home']} vs {game['away']}",
                                            "type": "Player Prop"
                                        })
                                        st.rerun()
                                with prop_cols[1]:
                                    if st.button(f"Rebounds O/U {player['rebounds_line']}", key=f"reb_{player['name']}_{game['id']}", use_container_width=True):
                                        st.session_state.parlay_legs.append({
                                            "id": len(st.session_state.parlay_legs),
                                            "selection": f"{player['name']} Over {player['rebounds_line']} Reb",
                                            "odds": -110,
                                            "game": f"{game['home']} vs {game['away']}",
                                            "type": "Player Prop"
                                        })
                                        st.rerun()
                                with prop_cols[2]:
                                    if st.button(f"Assists O/U {player['assists_line']}", key=f"ast_{player['name']}_{game['id']}", use_container_width=True):
                                        st.session_state.parlay_legs.append({
                                            "id": len(st.session_state.parlay_legs),
                                            "selection": f"{player['name']} Over {player['assists_line']} Ast",
                                            "odds": -110,
                                            "game": f"{game['home']} vs {game['away']}",
                                            "type": "Player Prop"
                                        })
                                        st.rerun()
                            
                            elif st.session_state.parlay_sport == 'NFL':
                                with prop_cols[0]:
                                    if st.button(f"Pass Yds O/U {player.get('pass_yards_line', 250)}", key=f"pass_{player['name']}_{game['id']}", use_container_width=True):
                                        st.session_state.parlay_legs.append({
                                            "id": len(st.session_state.parlay_legs),
                                            "selection": f"{player['name']} Over {player.get('pass_yards_line', 250)} Pass Yds",
                                            "odds": -110,
                                            "game": f"{game['home']} vs {game['away']}",
                                            "type": "Player Prop"
                                        })
                                        st.rerun()
                                with prop_cols[1]:
                                    if st.button(f"TDs O/U {player.get('tds_line', 1)}", key=f"td_{player['name']}_{game['id']}", use_container_width=True):
                                        st.session_state.parlay_legs.append({
                                            "id": len(st.session_state.parlay_legs),
                                            "selection": f"{player['name']} Over {player.get('tds_line', 1)} TDs",
                                            "odds": -110,
                                            "game": f"{game['home']} vs {game['away']}",
                                            "type": "Player Prop"
                                        })
                                        st.rerun()
                                with prop_cols[2]:
                                    if st.button(f"Rush Yds O/U {player.get('rush_yards_line', 50)}", key=f"rush_{player['name']}_{game['id']}", use_container_width=True):
                                        st.session_state.parlay_legs.append({
                                            "id": len(st.session_state.parlay_legs),
                                            "selection": f"{player['name']} Over {player.get('rush_yards_line', 50)} Rush Yds",
                                            "odds": -110,
                                            "game": f"{game['home']} vs {game['away']}",
                                            "type": "Player Prop"
                                        })
                                        st.rerun()
        else:
            st.info("No games found for player props. Try another sport.")

with col2:
    # Parlay Ticket
    st.markdown("<h3>🎫 Your Parlay</h3>", unsafe_allow_html=True)
    
    legs = st.session_state.parlay_legs
    
    if not legs:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 2rem; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">➕</div>
            <p style="color: #8A8F98;">Add selections to build your parlay</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Calculate parlay odds
        decimal_odds = 1
        for leg in legs:
            if leg['odds'] > 0:
                decimal_odds *= (leg['odds'] / 100 + 1)
            else:
                decimal_odds *= (100 / abs(leg['odds']) + 1)
        
        if decimal_odds > 2:
            parlay_odds = int((decimal_odds - 1) * 100)
        else:
            parlay_odds = int(-100 / (decimal_odds - 1))
        
        # Display legs with glass styling
        for idx, leg in enumerate(legs):
            bet_type = leg.get('type', 'Bet')
            type_colors = {
                'Moneyline': '#00d2ff',
                'Spread': '#00e701', 
                'Total': '#F97316',
                'Player Prop': '#A855F7'
            }
            type_color = type_colors.get(bet_type, '#8A8F98')
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="color: {type_color}; font-size: 0.65rem; text-transform: uppercase; font-weight: 600;">{bet_type}</span>
                        <p style="color: white; font-weight: 500; margin: 0; font-size: 0.875rem;">{leg['selection']}</p>
                        <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">{leg['game']}</p>
                    </div>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{leg['odds']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("❌", key=f"remove_{leg['id']}"):
                st.session_state.parlay_legs.pop(idx)
                st.rerun()
        
        # Stake input
        stake = st.number_input("Stake ($)", value=100, min_value=1)
        
        # Quick stake buttons
        cols = st.columns(4)
        for col, amount in zip(cols, [25, 50, 100, 250]):
            with col:
                if st.button(f"${amount}", key=f"stake_{amount}", use_container_width=True):
                    st.session_state.parlay_stake = amount
        
        # Calculate payout
        if parlay_odds > 0:
            payout = stake + (stake * parlay_odds / 100)
        else:
            payout = stake + (stake * 100 / abs(parlay_odds))
        
        profit = payout - stake
        implied_prob = (1 / decimal_odds) * 100
        
        # Summary - Glass Cards
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # Stats row
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; text-align: center;">
                <p style="color: #8A8F98; font-size: 0.7rem; margin: 0 0 0.25rem;">ODDS</p>
                <p style="color: white; font-family: monospace; font-size: 1.1rem; font-weight: 600; margin: 0;">{parlay_odds}</p>
            </div>
            """, unsafe_allow_html=True)
        with stat_col2:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; text-align: center;">
                <p style="color: #8A8F98; font-size: 0.7rem; margin: 0 0 0.25rem;">PAYOUT</p>
                <p style="color: #00e701; font-family: monospace; font-size: 1.1rem; font-weight: 600; margin: 0;">${payout:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        with stat_col3:
            profit_color = "#00e701" if profit > 0 else "#ff4d4d"
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; text-align: center;">
                <p style="color: #8A8F98; font-size: 0.7rem; margin: 0 0 0.25rem;">PROFIT</p>
                <p style="color: {profit_color}; font-family: monospace; font-size: 1.1rem; font-weight: 600; margin: 0;">+${profit:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Win probability
        st.markdown(f"<p style='color: #8A8F98; font-size: 0.875rem; margin-top: 1rem;'>Win Probability: {implied_prob:.1f}%</p>", unsafe_allow_html=True)
        st.progress(implied_prob / 100)
        
        # Action buttons
        st.button("🎯 Place Parlay", type="primary", use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("📋 Copy", use_container_width=True)
        with col2:
            st.button("📤 Share", use_container_width=True)
        
        # Risk level
        risk_level = "Low" if len(legs) <= 2 else "Medium" if len(legs) <= 4 else "High"
        risk_color = "#00e701" if risk_level == "Low" else "#F97316" if risk_level == "Medium" else "#ff4d4d"
        st.markdown(f"<p style='color: #8A8F98; margin-top: 1rem;'>Risk Level: <span style='color: {risk_color}; font-weight: 600;'>{risk_level}</span></p>", unsafe_allow_html=True)
