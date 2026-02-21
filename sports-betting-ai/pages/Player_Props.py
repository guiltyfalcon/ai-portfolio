"""
Player Props Page - Explore player prop markets
"""
import streamlit as st

st.set_page_config(page_title="Player Props - Sports Betting AI Pro", page_icon="👤", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

st.markdown("<h1>Player Props</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Explore player prop markets and trends</p>", unsafe_allow_html=True)

# Player carousel
players = [
    {"name": "LeBron James", "team": "LAL", "position": "SF", "image": "👑"},
    {"name": "Stephen Curry", "team": "GSW", "position": "PG", "image": "🎯"},
    {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "image": "☘️"},
    {"name": "Patrick Mahomes", "team": "KC", "position": "QB", "image": "🏈"},
    {"name": "Brock Purdy", "team": "SF", "position": "QB", "image": "🌉"},
]

# Player selector
col1, col2, col3, col4, col5 = st.columns(5)
selected_player = None

for idx, (col, player) in enumerate(zip([col1, col2, col3, col4, col5], players)):
    with col:
        if st.button(f"{player['image']}\n{player['name']}\n{player['team']}", key=f"player_{idx}", use_container_width=True):
            st.session_state.selected_player = player
            selected_player = player

# Default selection
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = players[0]

selected_player = st.session_state.selected_player

# Player details
st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"""
    <div style="background: rgba(21, 26, 38, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{selected_player['image']}</div>
        <h2 style="margin: 0; color: white;">{selected_player['name']}</h2>
        <p style="color: #8A8F98; margin: 0.5rem 0;">{selected_player['team']} • {selected_player['position']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Season stats
    st.markdown("<h4 style='margin-top: 1.5rem;'>Season Stats</h4>", unsafe_allow_html=True)
    
    if selected_player['position'] in ['SF', 'PG']:
        stats = {"PTS": 25.8, "REB": 7.2, "AST": 8.1}
    else:
        stats = {"Pass Yds": 285.5, "TD": 2.1, "Rush Yds": 25.3}
    
    cols = st.columns(3)
    for col, (stat, value) in zip(cols, stats.items()):
        with col:
            st.markdown(f"""
            <div style="background: rgba(11, 14, 20, 0.8); border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="font-size: 1.5rem; font-weight: 700; color: white; margin: 0;">{value}</p>
                <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">{stat}</p>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("<h3>Available Props</h3>", unsafe_allow_html=True)
    
    # Mock props
    if selected_player['position'] in ['SF', 'PG']:
        props = [
            {"type": "Points", "line": 26.5, "over": -110, "under": -110, "hit_rate": 68},
            {"type": "Rebounds", "line": 7.5, "over": -115, "under": -105, "hit_rate": 55},
            {"type": "Assists", "line": 8.5, "over": -120, "under": 100, "hit_rate": 62},
        ]
    else:
        props = [
            {"type": "Passing Yards", "line": 275.5, "over": -110, "under": -110, "hit_rate": 58},
            {"type": "TD Passes", "line": 2.5, "over": -130, "under": 110, "hit_rate": 65},
        ]
    
    for prop in props:
        with st.expander(f"{prop['type']} - Line: {prop['line']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="background: rgba(0, 231, 1, 0.1); border-radius: 12px; padding: 1rem; text-align: center;">
                    <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Over</p>
                    <p style="color: #00e701; font-family: monospace; font-size: 1.5rem; font-weight: 600; margin: 0;">{prop['over']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: rgba(255, 77, 77, 0.1); border-radius: 12px; padding: 1rem; text-align: center;">
                    <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Under</p>
                    <p style="color: #ff4d4d; font-family: monospace; font-size: 1.5rem; font-weight: 600; margin: 0;">{prop['under']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: rgba(0, 210, 255, 0.1); border-radius: 12px; padding: 1rem; text-align: center;">
                    <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Hit Rate</p>
                    <p style="color: #00d2ff; font-size: 1.5rem; font-weight: 600; margin: 0;">{prop['hit_rate']}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Last 5 games
            st.markdown("<p style='color: #8A8F98; margin-top: 1rem;'>Last 5 Games:</p>", unsafe_allow_html=True)
            results = ['O', 'O', 'U', 'O', 'O']
            cols = st.columns(5)
            for col, result in zip(cols, results):
                color = '#00e701' if result == 'O' else '#ff4d4d'
                with col:
                    st.markdown(f"""
                    <div style="background: rgba({0 if result == 'O' else 255}, {231 if result == 'O' else 77}, {1 if result == 'O' else 77}, 0.2); 
                                border-radius: 8px; padding: 0.5rem; text-align: center;">
                        <span style="color: {color}; font-weight: 600;">{result}</span>
                    </div>
                    """, unsafe_allow_html=True)

# Trending props
st.markdown("<h3 style='margin-top: 2rem;'>📈 Trending Props</h3>", unsafe_allow_html=True)

trending = [
    {"player": "LeBron James", "prop": "Points", "line": 26.5, "movement": "+2", "odds": -110},
    {"player": "Stephen Curry", "prop": "Threes", "line": 4.5, "movement": "-0.5", "odds": -125},
    {"player": "Jayson Tatum", "prop": "Rebounds", "line": 8.5, "movement": "+1", "odds": -110},
    {"player": "Patrick Mahomes", "prop": "Pass Yds", "line": 275.5, "movement": "+5", "odds": -110},
]

cols = st.columns(4)
for col, item in zip(cols, trending):
    with col:
        movement_color = "#00e701" if item['movement'].startswith('+') else "#ff4d4d"
        st.markdown(f"""
        <div style="background: rgba(11, 14, 20, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1rem;">
            <p style="color: white; font-weight: 500; margin: 0;">{item['player']}</p>
            <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">{item['prop']} {item['line']}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{item['odds']}</span>
                <span style="color: {movement_color}; font-size: 0.875rem;">{item['movement']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
