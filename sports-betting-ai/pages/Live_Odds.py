"""
Live Odds Page - Compare odds across bookmakers
"""
import streamlit as st

st.set_page_config(page_title="Live Odds - Sports Betting AI Pro", page_icon="📈", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

st.markdown("<h1>Live Odds</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Compare odds across bookmakers</p>", unsafe_allow_html=True)

# Sport filter
sports = ["All Sports", "NBA", "NFL", "MLB", "NHL", "NCAAB", "NCAAF"]
selected_sport = st.segmented_control("Select Sport", sports, default="All Sports")

# Mock games data
games = [
    {
        "sport": "NBA",
        "home": "Los Angeles Lakers",
        "away": "Golden State Warriors",
        "home_abbr": "LAL",
        "away_abbr": "GSW",
        "home_record": "32-18",
        "away_record": "28-22",
        "time": "7:30 PM ET",
        "status": "upcoming",
        "ml_home": -140,
        "ml_away": 120,
        "spread": -3.5,
        "spread_home": -110,
        "spread_away": -110,
        "total": 228.5,
        "over": -110,
        "under": -110,
    },
    {
        "sport": "NBA",
        "home": "Boston Celtics",
        "away": "Denver Nuggets",
        "home_abbr": "BOS",
        "away_abbr": "DEN",
        "home_record": "38-12",
        "away_record": "35-15",
        "time": "8:00 PM ET",
        "status": "upcoming",
        "ml_home": -180,
        "ml_away": 155,
        "spread": -4.5,
        "spread_home": -110,
        "spread_away": -110,
        "total": 224.5,
        "over": -105,
        "under": -115,
    },
    {
        "sport": "NFL",
        "home": "Kansas City Chiefs",
        "away": "San Francisco 49ers",
        "home_abbr": "KC",
        "away_abbr": "SF",
        "home_record": "14-3",
        "away_record": "13-4",
        "time": "6:30 PM ET",
        "status": "upcoming",
        "ml_home": -165,
        "ml_away": 140,
        "spread": -3,
        "spread_home": -110,
        "spread_away": -110,
        "total": 47.5,
        "over": -110,
        "under": -110,
    },
    {
        "sport": "NHL",
        "home": "Toronto Maple Leafs",
        "away": "Colorado Avalanche",
        "home_abbr": "TOR",
        "away_abbr": "COL",
        "home_record": "35-18-5",
        "away_record": "38-15-4",
        "time": "LIVE",
        "status": "live",
        "score": {"home": 2, "away": 1},
        "ml_home": -130,
        "ml_away": 110,
        "spread": -1.5,
        "spread_home": 110,
        "spread_away": -130,
        "total": 6.5,
        "over": -105,
        "under": -115,
    },
]

# Filter games
if selected_sport != "All Sports":
    games = [g for g in games if g["sport"] == selected_sport]

# Bookmakers
bookmakers = ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"]

# Display games
for game in games:
    is_live = game["status"] == "live"
    live_badge = '<span style="background: rgba(0, 231, 1, 0.15); color: #00e701; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; animation: pulse 2s infinite;">● LIVE</span>' if is_live else ""
    score_display = f"{game['score']['home']} - {game['score']['away']}" if is_live else game["time"]
    
    st.markdown(f"""
    <div style="background: rgba(21, 26, 38, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: #00d2ff; font-weight: 500;">{game['sport']}</span>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    {live_badge}
                    <span style="color: #8A8F98;">{score_display}</span>
                </div>
            </div>
            <button style="background: none; border: none; color: #8A8F98; cursor: pointer;">⭐</button>
        </div>
        
        <div style="display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 1rem;">
            <!-- Teams -->
            <div>
                <div style="margin-bottom: 0.75rem;">
                    <p style="color: white; font-weight: 500; margin: 0;">{game['home']}</p>
                    <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">{game['home_record']}</p>
                </div>
                <div>
                    <p style="color: white; font-weight: 500; margin: 0;">{game['away']}</p>
                    <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">{game['away_record']}</p>
                </div>
            </div>
            
            <!-- Moneyline -->
            <div>
                <p style="color: #8A8F98; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem;">Moneyline</p>
                <div style="background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 0.5rem; text-align: center;">
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{game['ml_home']}</span>
                </div>
                <div style="background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.5rem 1rem; text-align: center;">
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{game['ml_away']}</span>
                </div>
            </div>
            
            <!-- Spread -->
            <div>
                <p style="color: #8A8F98; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem;">Spread</p>
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 0.5rem;">
                    <span style="color: #8A8F98; font-size: 0.875rem;">{game['spread']}</span>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{game['spread_home']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.5rem 1rem;">
                    <span style="color: #8A8F98; font-size: 0.875rem;">+{abs(game['spread'])}</span>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{game['spread_away']}</span>
                </div>
            </div>
            
            <!-- Total -->
            <div>
                <p style="color: #8A8F98; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem;">Total</p>
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 0.5rem;">
                    <span style="color: #8A8F98; font-size: 0.875rem;">O {game['total']}</span>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{game['over']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.5rem 1rem;">
                    <span style="color: #8A8F98; font-size: 0.875rem;">U {game['total']}</span>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{game['under']}</span>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="color: #8A8F98; font-size: 0.75rem; margin: 0 0 0.5rem 0;">Available at:</p>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                {''.join([f'<span style="background: rgba(11, 14, 20, 0.8); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; color: #8A8F98;">{book}</span>' for book in bookmakers])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Arbitrage Alert
st.markdown("""
<div style="background: rgba(249, 115, 22, 0.1); border: 1px solid rgba(249, 115, 22, 0.3); border-radius: 12px; padding: 1rem; margin-top: 1rem;">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="width: 40px; height: 40px; background: rgba(249, 115, 22, 0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center;">⚡</div>
        <div>
            <p style="color: white; font-weight: 600; margin: 0;">Arbitrage Opportunity Detected</p>
            <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">Lakers vs Warriors - 2.3% guaranteed profit</p>
        </div>
        <button style="margin-left: auto; background: #F97316; color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 500; cursor: pointer;">View Details</button>
    </div>
</div>
""", unsafe_allow_html=True)
