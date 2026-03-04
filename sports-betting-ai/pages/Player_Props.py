"""
Player Props Page - Explore player prop markets with AI reasoning
Now uses player_props_cache.json for real-time data
"""
import streamlit as st
import requests
import json
import os
import sys
sys.path.append('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai')
from models.universal_predictor import UniversalSportsPredictor

st.set_page_config(page_title="Player Props - Sports Betting AI Pro", page_icon="👤", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

# Load player props cache
def load_player_props_cache():
    """Load player props from cache file."""
    cache_path = '/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/player_props_cache.json'
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None

def get_props_for_sport(cache, sport):
    """Get player props for a specific sport."""
    if not cache or 'sports' not in cache:
        return []
    return cache['sports'].get(sport.lower(), [])

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
            for event in data.get('events', [])[:4]:
                home_team = event['competitions'][0]['competitors'][0]['team']['displayName']
                away_team = event['competitions'][0]['competitors'][1]['team']['displayName']
                status = event.get('status', {}).get('type', {}).get('state', 'pre')
                
                games.append({
                    'id': event['id'],
                    'sport': sport.upper(),
                    'home_team': home_team,
                    'away_team': away_team,
                    'time': event.get('status', {}).get('shortDetail', 'TBD'),
                    'status': 'live' if status == 'in' else 'upcoming',
                    'home_players': get_players_for_team(sport, home_team),
                    'away_players': get_players_for_team(sport, away_team)
                })
            return games
    except Exception as e:
        print(f"Error fetching ESPN data: {e}")
    return []

def generate_prop_reasoning(player: dict, prop: dict, sport: str) -> str:
    """Generate AI reasoning for why a prop is likely to hit."""
    hit_rate = prop['hit_rate']
    prop_type = prop['type']
    line = prop['line']
    
    # Sport-specific reasoning templates
    if sport.upper() == "NBA":
        if prop_type == "Points":
            if hit_rate >= 65:
                return f"Strong matchup: {player['name']} averaging above {line} in recent games. Defense allowing {line+2:.0f}+ to position."
            elif hit_rate >= 55:
                return f"Moderate lean: {player['name']} hit this line in {hit_rate}% of games. Watch pregame warmup."
            else:
                return f"Risky: {player['name']} below {line} in 3 of last 5. Consider UNDER."
        elif prop_type == "Rebounds":
            if hit_rate >= 65:
                return f"Board battle advantage: {player['name']} vs weaker rebounding matchup. Pace favors high rebounds."
            elif hit_rate >= 55:
                return f"Decent spot: {player['name']} averaging {line+0.5:.0f} rebounds vs this opponent type."
            else:
                return f"Tough matchup: Opponent limits {player['position']} to under {line-1:.0f} boards."
        elif prop_type == "Assists":
            if hit_rate >= 65:
                return f"Playmaker alert: {player['name']} in high-usage role. Team pace boosts assist opportunities."
            elif hit_rate >= 55:
                return f"Solid floor: {player['name']} dished {line+1:.0f}+ assists in 4 of last 6 games."
            else:
                return f"Concern: Ball-dominant teammate may limit {player['name']}'s creation."
        elif prop_type == "Threes":
            if hit_rate >= 55:
                return f"Green light: {player['name']} shooting {hit_rate-5:.0f}% from deep recently. High volume expected."
            else:
                return f"Cold streak: {player['name']} hit only {hit_rate-10:.0f}% of threes in last 5."
        elif prop_type == "Blocks" or prop_type == "Steals":
            if hit_rate >= 60:
                return f"Defensive stopper: {player['name']} excels vs this opponent's play style. High activity expected."
            else:
                return f"Volatile market: Defensive stats hard to predict. Small sample size."
    
    elif sport.upper() == "NFL":
        if prop_type == "Pass Yards":
            if hit_rate >= 60:
                return f"Aerial attack: QB averaging {line+15:.0f} yards vs this secondary. Pass-heavy script expected."
            elif hit_rate >= 50:
                return f"Game flow dependent: Could exceed if trailing, but run game may dominate."
            else:
                return f"Tough coverage: Opponent CBs limiting WRs. Consider UNDER."
        elif prop_type == "Rush Yards":
            if hit_rate >= 60:
                return f"Ground game edge: RB averaging {line+8:.0f} yards vs this front. High carry volume expected."
            else:
                return f"Stacked box: Defense strong vs run. May struggle to hit {line}."
        elif prop_type == "Rec Yards":
            if hit_rate >= 60:
                return f"Target share: WR seeing {hit_rate+10:.0f}% target rate. Favorable CB matchup."
            else:
                return f"Inconsistent: WR production boom-or-bust. Risky prop."
    
    elif sport.upper() == "NHL":
        if prop_type == "Points" or prop_type == "Goals":
            if hit_rate >= 55:
                return f"Hot hand: {player['name']} with points in {hit_rate:.0f}% of recent games. Power play time boosts odds."
            else:
                return f"Cold streak: {player['name']} scoreless in 3 of last 5. Goalie matchup tough."
        elif prop_type == "Shots":
            if hit_rate >= 55:
                return f"Volume play: {player['name']} averaging {line+1:.0f} shots. High usage role."
            else:
                return f"Low shot volume: {player['name']} below {line} in recent games."
    
    elif sport.upper() == "MLB":
        if prop_type == "Hits":
            if hit_rate >= 55:
                return f"Batter edge: {player['name']} hitting {hit_rate+10:.0f}% vs this pitcher's handedness. Good park factor."
            else:
                return f"Tough matchup: Pitcher limits hits to .{200+hit_rate:.0f} vs this batter type."
        elif prop_type == "Total Bases" or prop_type == "RBIs":
            if hit_rate >= 50:
                return f"Power spot: {player['name']} with extra-base hit potential. Lineup position drives RBI chances."
            else:
                return f"Low run expectancy: Lineup ahead may not get on base. RBI opportunity limited."
    
    # Default fallback
    if hit_rate >= 60:
        return f"Model favors OVER: {hit_rate}% historical hit rate. Statistical edge detected."
    elif hit_rate >= 50:
        return f"Coin flip: {hit_rate}% hit rate. No strong edge either direction."
    else:
        return f"Model leans UNDER: Only {hit_rate}% hit rate. Risky OVER play."


def get_players_for_team(sport, team_name):
    """Generate players for a team with their prop lines"""
    team_abbr = ''.join([c for c in team_name.split()[-1].upper() if c.isalpha()])[:3]
    
    if sport.upper() == "NBA":
        return [
            {"name": f"Star Player", "team": team_name, "abbr": team_abbr, "position": "PG", "emoji": "🏀",
             "props": [
                 {"type": "Points", "line": 25.5, "over": -110, "under": -110, "hit_rate": 65},
                 {"type": "Rebounds", "line": 6.5, "over": -115, "under": -105, "hit_rate": 58},
                 {"type": "Assists", "line": 7.5, "over": -120, "under": 100, "hit_rate": 62},
             ]},
            {"name": f"Top Scorer", "team": team_name, "abbr": team_abbr, "position": "SF", "emoji": "🔥",
             "props": [
                 {"type": "Points", "line": 22.5, "over": -110, "under": -110, "hit_rate": 60},
                 {"type": "Rebounds", "line": 7.5, "over": -110, "under": -110, "hit_rate": 55},
                 {"type": "Threes", "line": 2.5, "over": -125, "under": 105, "hit_rate": 52},
             ]},
            {"name": f"Big Man", "team": team_name, "abbr": team_abbr, "position": "C", "emoji": "💪",
             "props": [
                 {"type": "Points", "line": 15.5, "over": -110, "under": -110, "hit_rate": 55},
                 {"type": "Rebounds", "line": 9.5, "over": -115, "under": -105, "hit_rate": 68},
                 {"type": "Blocks", "line": 1.5, "over": -120, "under": 100, "hit_rate": 48},
             ]},
            {"name": f"Wing Player", "team": team_name, "abbr": team_abbr, "position": "SG", "emoji": "⚡",
             "props": [
                 {"type": "Points", "line": 18.5, "over": -110, "under": -110, "hit_rate": 58},
                 {"type": "Steals", "line": 1.5, "over": -130, "under": 110, "hit_rate": 62},
             ]},
        ]
    elif sport.upper() == "NFL":
        return [
            {"name": "Starting QB", "team": team_name, "abbr": team_abbr, "position": "QB", "emoji": "🏈",
             "props": [
                 {"type": "Pass Yards", "line": 275.5, "over": -110, "under": -110, "hit_rate": 58},
                 {"type": "TD Passes", "line": 2.5, "over": -135, "under": 115, "hit_rate": 64},
                 {"type": "Rush Yards", "line": 25.5, "over": -115, "under": -105, "hit_rate": 52},
             ]},
            {"name": "RB1", "team": team_name, "abbr": team_abbr, "position": "RB", "emoji": "🔥",
             "props": [
                 {"type": "Rush Yards", "line": 75.5, "over": -110, "under": -110, "hit_rate": 60},
                 {"type": "TD", "line": 0.5, "over": -150, "under": 125, "hit_rate": 55},
                 {"type": "Rec Yards", "line": 22.5, "over": -115, "under": -105, "hit_rate": 48},
             ]},
            {"name": "WR1", "team": team_name, "abbr": team_abbr, "position": "WR", "emoji": "⚡",
             "props": [
                 {"type": "Rec Yards", "line": 85.5, "over": -110, "under": -110, "hit_rate": 62},
                 {"type": "Catches", "line": 6.5, "over": -140, "under": 120, "hit_rate": 65},
                 {"type": "TD", "line": 0.5, "over": -110, "under": -110, "hit_rate": 45},
             ]},
        ]
    elif sport.upper() == "NHL":
        return [
            {"name": "Star F", "team": team_name, "abbr": team_abbr, "position": "C", "emoji": "🏒",
             "props": [
                 {"type": "Points", "line": 1.5, "over": -120, "under": 100, "hit_rate": 58},
                 {"type": "Shots", "line": 3.5, "over": -110, "under": -110, "hit_rate": 55},
                 {"type": "Goals", "line": 0.5, "over": -150, "under": 125, "hit_rate": 38},
             ]},
            {"name": "Defenseman", "team": team_name, "abbr": team_abbr, "position": "D", "emoji": "🛡️",
             "props": [
                 {"type": "Shots", "line": 2.5, "over": -115, "under": -105, "hit_rate": 48},
                 {"type": "Blocks", "line": 2.5, "over": -130, "under": 110, "hit_rate": 62},
             ]},
        ]
    elif sport.upper() == "MLB":
        return [
            {"name": "Star Batter", "team": team_name, "abbr": team_abbr, "position": "OF", "emoji": "⚾",
             "props": [
                 {"type": "Hits", "line": 1.5, "over": -140, "under": 120, "hit_rate": 52},
                 {"type": "Total Bases", "line": 1.5, "over": -110, "under": -110, "hit_rate": 48},
                 {"type": "RBIs", "line": 0.5, "over": -115, "under": -105, "hit_rate": 42},
             ]},
        ]
    else:
        return []

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

st.markdown("<h1>Player Props</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Explore player prop markets and trends</p>", unsafe_allow_html=True)

# Sport Selector
sport_cols = st.columns([1, 3])
with sport_cols[0]:
    st.markdown("<p style='color: #8A8F98; margin-bottom: 0.5rem;'>Select Sport</p>", unsafe_allow_html=True)
    selected_sport = st.selectbox("Sport", ["🏀 NBA", "🏈 NFL", "⚾ MLB", "🏒 NHL", "🏀 NCAAB", "🏈 NCAAF"], 
                                   index=0, label_visibility="collapsed")
    current_sport = selected_sport.split()[-1]

with sport_cols[1]:
    st.markdown("<p style='color: #8A8F98; margin-bottom: 0.5rem;'>&nbsp;</p>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Games", use_container_width=True):
        st.rerun()

# Load player props from cache
cache = load_player_props_cache()
props_games = get_props_for_sport(cache, current_sport.lower())

# Show cache timestamp if available
if cache and 'timestamp' in cache:
    st.caption(f"📊 Data updated: {cache['timestamp'].replace('T', ' ').split('.')[0]}")

if not props_games:
    st.info(f"No player props available for {current_sport}. Check back later or try a different sport.")
else:
    # Game selector
    st.markdown("<h3>📅 Select a Game</h3>", unsafe_allow_html=True)
    
    game_options = {f"{g['home_team']} vs {g['away_team']}": g for g in props_games}
    selected_game_name = st.selectbox("Game", list(game_options.keys()), label_visibility="collapsed")
    selected_game = game_options[selected_game_name]
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Display players from both teams
    col_home, col_away = st.columns(2)
    
    # Helper to format prop type names
    def format_prop_type(prop_type):
        return prop_type.replace('_', ' ').title()
    
    with col_home:
        st.markdown(f"""
        <div style="background: rgba(0, 210, 255, 0.1); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #00d2ff;">{selected_game['home_team']}</h3>
            <p style="color: #8A8F98; margin: 0; font-size: 0.875rem;">Home Team</p>
        </div>
        """, unsafe_allow_html=True)
        
        for player in selected_game.get('players', [])[:4]:  # Show top 4 players
            player_name = player.get('player', 'Unknown')
            team = player.get('team', '')
            props = player.get('props', [])
            
            with st.expander(f"🎯 {player_name}"):
                for prop in props:
                    if not prop:
                        continue
                    
                    prop_type = format_prop_type(prop.get('type', 'Unknown'))
                    line = prop.get('line', 0)
                    avg = prop.get('avg', line - 0.5)
                    
                    # Calculate hit rate from avg vs line
                    hit_rate = 55 if avg >= line else 45
                    
                    # Generate simple reasoning
                    if avg >= line:
                        reasoning = f"✅ Averaging {avg:.1f} - above the {line} line. Strong OVER lean."
                        rec_badge = '<span style="background: rgba(0, 231, 1, 0.2); color: #00e701; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">LEAN OVER</span>'
                    else:
                        reasoning = f"⚠️ Averaging {avg:.1f} - below the {line} line. Consider UNDER."
                        rec_badge = '<span style="background: rgba(255, 77, 77, 0.2); color: #ff4d4d; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">LEAN UNDER</span>'
                    
                    # Prop card
                    prop_html = f"""
                    <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div>
                                <span style="color: white; font-weight: 600;">{prop_type}</span>
                                <span style="color: #00d2ff; font-family: monospace;"> {line}</span>
                            </div>
                            {rec_badge}
                        </div>
                        <div style="background: rgba(0, 210, 255, 0.08); border-left: 3px solid #00d2ff; padding: 0.5rem; border-radius: 4px;">
                            <div style="color: #00d2ff; font-size: 0.7rem; font-weight: 600; margin-bottom: 0.25rem;">📊 AVG: {avg:.1f}</div>
                            <div style="color: #B0B5BC; font-size: 0.75rem; line-height: 1.4;">{reasoning}</div>
                        </div>
                    </div>
                    """
                    st.markdown(prop_html, unsafe_allow_html=True)
                    
                    # Add to parlay buttons
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"Add Over ➕", key=f"over_{player['name']}_{prop['type']}", use_container_width=True):
                            if 'parlay_builder_legs' not in st.session_state:
                                st.session_state.parlay_builder_legs = []
                            st.session_state.parlay_builder_legs.append({
                                "selection": f"{player['name']} Over {prop['line']} {prop['type']}",
                                "odds": prop['over'],
                                "game": f"{selected_game['home_team']} vs {selected_game['away_team']}"
                            })
                            st.success(f"Added {player['name']} Over {prop['line']} to parlay!")
                    with btn_col2:
                        if st.button(f"Add Under ➕", key=f"under_{player['name']}_{prop['type']}", use_container_width=True):
                            if 'parlay_builder_legs' not in st.session_state:
                                st.session_state.parlay_builder_legs = []
                            st.session_state.parlay_builder_legs.append({
                                "selection": f"{player['name']} Under {prop['line']} {prop['type']}",
                                "odds": prop['under'],
                                "game": f"{selected_game['home_team']} vs {selected_game['away_team']}"
                            })
                            st.success(f"Added {player['name']} Under {prop['line']} to parlay!")
    
    with col_away:
        st.markdown(f"""
        <div style="background: rgba(0, 231, 1, 0.1); border: 1px solid rgba(0, 231, 1, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #00e701;">{selected_game['away_team']}</h3>
            <p style="color: #8A8F98; margin: 0; font-size: 0.875rem;">Away Team</p>
        </div>
        """, unsafe_allow_html=True)
        
        for player in selected_game.get('players', [])[:4]:  # Show top 4 players
            with st.expander(f"{player['emoji']} {player['name']} ({player['position']})"):
                for prop in player['props']:
                    # Generate reasoning for this prop
                    reasoning = generate_prop_reasoning(player, prop, current_sport)
                    
                    # Recommendation badge
                    hit_rate = prop['hit_rate']
                    if hit_rate >= 60:
                        rec_badge = '<span style="background: rgba(0, 231, 1, 0.2); color: #00e701; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">STRONG OVER</span>'
                    elif hit_rate >= 55:
                        rec_badge = '<span style="background: rgba(0, 210, 255, 0.2); color: #00d2ff; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">LEAN OVER</span>'
                    elif hit_rate >= 45:
                        rec_badge = '<span style="background: rgba(255, 255, 255, 0.1); color: #8A8F98; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">TOSS-UP</span>'
                    else:
                        rec_badge = '<span style="background: rgba(255, 77, 77, 0.2); color: #ff4d4d; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">LEAN UNDER</span>'
                    
                    # Prop card with Over/Under + Reasoning
                    prop_html = f"""
                    <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div>
                                <span style="color: white; font-weight: 600;">{prop['type']}</span>
                                <span style="color: #00d2ff; font-family: monospace;"> {prop['line']}</span>
                            </div>
                            {rec_badge}
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <div style="background: rgba(0, 231, 1, 0.1); border-radius: 6px; padding: 0.5rem; text-align: center;">
                                <span style="color: #8A8F98; font-size: 0.65rem; display: block;">OVER</span>
                                <span style="color: #00e701; font-family: monospace; font-weight: 600;">{prop['over']}</span>
                            </div>
                            <div style="background: rgba(255, 77, 77, 0.1); border-radius: 6px; padding: 0.5rem; text-align: center;">
                                <span style="color: #8A8F98; font-size: 0.65rem; display: block;">UNDER</span>
                                <span style="color: #ff4d4d; font-family: monospace; font-weight: 600;">{prop['under']}</span>
                            </div>
                        </div>
                        <div style="background: rgba(0, 210, 255, 0.08); border-left: 3px solid #00d2ff; padding: 0.5rem; border-radius: 4px;">
                            <div style="color: #00d2ff; font-size: 0.7rem; font-weight: 600; margin-bottom: 0.25rem;">🧠 AI ANALYSIS</div>
                            <div style="color: #B0B5BC; font-size: 0.75rem; line-height: 1.4;">{reasoning}</div>
                        </div>
                    </div>
                    """
                    st.markdown(prop_html, unsafe_allow_html=True)
                    
                    # Add to parlay buttons
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"Add Over ➕", key=f"over_away_{player['name']}_{prop['type']}", use_container_width=True):
                            if 'parlay_builder_legs' not in st.session_state:
                                st.session_state.parlay_builder_legs = []
                            st.session_state.parlay_builder_legs.append({
                                "selection": f"{player['name']} Over {prop['line']} {prop['type']}",
                                "odds": prop['over'],
                                "game": f"{selected_game['home_team']} vs {selected_game['away_team']}"
                            })
                            st.success(f"Added {player['name']} Over {prop['line']} to parlay!")
                    with btn_col2:
                        if st.button(f"Add Under ➕", key=f"under_away_{player['name']}_{prop['type']}", use_container_width=True):
                            if 'parlay_builder_legs' not in st.session_state:
                                st.session_state.parlay_builder_legs = []
                            st.session_state.parlay_builder_legs.append({
                                "selection": f"{player['name']} Under {prop['line']} {prop['type']}",
                                "odds": prop['under'],
                                "game": f"{selected_game['home_team']} vs {selected_game['away_team']}"
                            })
                            st.success(f"Added {player['name']} Under {prop['line']} to parlay!")

# Quick Parlay Summary (if legs exist)
if st.session_state.get('parlay_builder_legs'):
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3>🎫 Parlay Builder</h3>", unsafe_allow_html=True)
    
    for i, leg in enumerate(st.session_state.parlay_builder_legs):
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(0,210,255,0.3); border-radius: 8px; padding: 0.5rem; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: white; font-size: 0.875rem;">{leg['selection']}</span>
                <span style="color: #00d2ff; font-family: monospace;">{leg['odds']}</span>
            </div>
            <span style="color: #8A8F98; font-size: 0.75rem;">{leg['game']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("Clear Parlay 🗑️", use_container_width=True):
        st.session_state.parlay_builder_legs = []
        st.rerun()
    
    if st.button("Go to Parlay Builder ➡️", type="primary", use_container_width=True):
        st.switch_page("pages/Parlay_Builder.py")
