import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bet_tracker import BetTracker
from api.espn import ESPNAPI

st.set_page_config(
    page_title="Bet Tracker 💰",
    page_icon="💰",
    layout="wide"
)

# 💎 PREMIUM CHECK
is_supporter = st.session_state.get('is_supporter', False)
if not is_supporter:
    st.markdown("# 💎 Bet Tracker")
    st.markdown("---")
    st.warning("🔒 Premium Feature Locked")
    st.markdown("""
        <div style="background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.3); border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center;">
            <h3>💎 Unlock Premium</h3>
            <p>Track your bets, calculate ROI, and analyze your performance.</p>
            <a href="https://buy.stripe.com/4gM28k5L17246LNfubfjG00" target="_blank" style="background: #2ecc71; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">Subscribe — $5/mo</a>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #00d26a 0%, #2ecc71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .bet-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
    }
    .win { border-left: 4px solid #00d26a; }
    .loss { border-left: 4px solid #ff4757; }
    .push { border-left: 4px solid #ffa502; }
    .profit-positive { color: #00d26a; font-weight: 700; }
    .profit-negative { color: #ff4757; font-weight: 700; }
    .vs-divider {
        text-align: center;
        color: #00d2ff;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Bet Tracker</div>', unsafe_allow_html=True)

tracker = BetTracker()

# Initialize ESPN API for team data
@st.cache_data(ttl=3600)
def get_teams_for_sport(sport):
    """Fetch teams for selected sport."""
    try:
        espn = ESPNAPI()
        teams_df = espn.get_teams(sport.lower())
        if not teams_df.empty and 'name' in teams_df.columns:
            return teams_df['name'].tolist()
    except:
        pass
    return []

# Default teams by sport (fallback if API fails)
DEFAULT_TEAMS = {
    'NBA': ['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
            'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
            'Houston Rockets', 'Indiana Pacers', 'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies',
            'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
            'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
            'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'],
    'NFL': ['Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills', 'Carolina Panthers',
            'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns', 'Dallas Cowboys', 'Denver Broncos',
            'Detroit Lions', 'Green Bay Packers', 'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars',
            'Kansas City Chiefs', 'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants', 'New York Jets',
            'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers', 'Seattle Seahawks', 'Tampa Bay Buccaneers',
            'Tennessee Titans', 'Washington Commanders'],
    'MLB': ['Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs',
            'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians', 'Colorado Rockies', 'Detroit Tigers',
            'Houston Astros', 'Kansas City Royals', 'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins',
            'Milwaukee Brewers', 'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics',
            'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants', 'Seattle Mariners',
            'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals'],
    'NHL': ['Anaheim Ducks', 'Arizona Coyotes', 'Boston Bruins', 'Buffalo Sabres', 'Calgary Flames',
            'Carolina Hurricanes', 'Chicago Blackhawks', 'Colorado Avalanche', 'Columbus Blue Jackets', 'Dallas Stars',
            'Detroit Red Wings', 'Edmonton Oilers', 'Florida Panthers', 'Los Angeles Kings', 'Minnesota Wild',
            'Montreal Canadiens', 'Nashville Predators', 'New Jersey Devils', 'New York Islanders', 'New York Rangers',
            'Ottawa Senators', 'Philadelphia Flyers', 'Pittsburgh Penguins', 'San Jose Sharks', 'Seattle Kraken',
            'St. Louis Blues', 'Tampa Bay Lightning', 'Toronto Maple Leafs', 'Utah Hockey Club', 'Vancouver Canucks',
            'Vegas Golden Knights', 'Winnipeg Jets'],
    'Other': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']
}

with st.sidebar:
    st.markdown("### 💵 Bankroll")
    current_bankroll = st.session_state.get('bankroll', 1000.0)
    new_bankroll = st.number_input("Starting Bankroll ($)", value=float(current_bankroll), min_value=10.0, step=50.0)
    if new_bankroll != current_bankroll:
        st.session_state['bankroll'] = new_bankroll
    
    if st.button("📥 Export CSV"):
        csv = tracker.export_to_csv()
        if csv:
            st.download_button("Download", csv, f"bets_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No bets to export")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Bet", "📝 Pending", "📜 History"])

with tab1:
    stats = tracker.get_stats()
    cols = st.columns(5)
    cols[0].metric("Total Bets", stats['total_bets'])
    cols[1].metric("Wins", stats['wins'])
    cols[2].metric("Losses", stats['losses'])
    profit_color = "normal" if stats['total_profit'] >= 0 else "inverse"
    cols[3].metric("Profit", f"${stats['total_profit']:.2f}", delta_color=profit_color)
    cols[4].metric("ROI", f"{stats['roi']*100:.1f}%")
    
    bets = tracker.load_bets()
    settled = bets[bets['status'] == 'settled'] if not bets.empty else pd.DataFrame()
    
    if not settled.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Profit Over Time")
            settled_sorted = settled.sort_values('date')
            settled_sorted['cumulative'] = settled_sorted['profit'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(range(len(settled_sorted))), y=settled_sorted['cumulative'], mode='lines+markers', line=dict(color='#00d26a', width=3), fill='tozeroy', fillcolor='rgba(0,210,106,0.2)'))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Win/Loss")
            win_count = len(settled[settled['result'] == 'win'])
            loss_count = len(settled[settled['result'] == 'loss'])
            push_count = len(settled[settled['result'] == 'push'])
            fig2 = go.Figure(data=[go.Pie(labels=['Wins', 'Losses', 'Pushes'], values=[win_count, loss_count, push_count], marker_colors=['#00d26a', '#ff4757', '#ffa502'], hole=0.4)])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300)
            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### ➕ Add New Bet")
    
    # Sport selection first
    sport = st.selectbox("Select Sport", ['NBA', 'NFL', 'MLB', 'NHL', 'Other'], key="bet_sport")
    
    # Get teams for selected sport
    teams = get_teams_for_sport(sport) if sport != 'Other' else DEFAULT_TEAMS['Other']
    if not teams:
        teams = DEFAULT_TEAMS.get(sport, DEFAULT_TEAMS['Other'])
    
    # Team selection with dropdowns
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        home_team = st.selectbox("Home Team", teams, key="home_team_select")
    
    with col2:
        st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)
    
    with col3:
        # Filter out home team from away options
        away_teams = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_teams, key="away_team_select")
    
    # Pick selection
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Auto-generate pick options based on teams
        pick_options = [
            f"{home_team} ML",
            f"{away_team} ML",
            f"{home_team} Spread",
            f"{away_team} Spread",
            f"Over",
            f"Under",
            "Other"
        ]
        pick = st.selectbox("Your Pick", pick_options, key="pick_select")
        
        if pick == "Other":
            pick = st.text_input("Custom Pick", placeholder="Enter your pick")
    
    with col2:
        # Initialize odds in session state if not present
        if 'odds_value' not in st.session_state:
            st.session_state['odds_value'] = -110
        
        odds = st.number_input("Odds", value=st.session_state['odds_value'], key="odds_input_widget")
        stake = st.number_input("Stake ($)", value=10.0, min_value=0.01, step=5.0, key="stake_input")
    
    # Quick odds buttons - update session state before widget renders next time
    st.caption("Quick Odds:")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    with qcol1:
        if st.button("-110", use_container_width=True, key="btn_110"):
            st.session_state['odds_value'] = -110
            st.rerun()
    with qcol2:
        if st.button("+150", use_container_width=True, key="btn_150"):
            st.session_state['odds_value'] = 150
            st.rerun()
    with qcol3:
        if st.button("+200", use_container_width=True, key="btn_200"):
            st.session_state['odds_value'] = 200
            st.rerun()
    with qcol4:
        if st.button("-200", use_container_width=True, key="btn_minus200"):
            st.session_state['odds_value'] = -200
            st.rerun()
    
    if st.button("Add Bet", type="primary", use_container_width=True):
        if home_team and away_team and pick and pick != "Other":
            bet, error = tracker.add_bet(sport, home_team, away_team, pick, odds, stake)
            if bet:
                st.success(f"✅ Bet #{bet['id']} added! {home_team} vs {away_team} - {pick}")
                st.balloons()
            else:
                st.error(f"Error: {error}")
        else:
            st.error("⚠️ Please select teams and pick")

with tab3:
    pending = tracker.get_pending_bets()
    if not pending.empty:
        st.markdown(f"### 📝 Pending Bets ({len(pending)})")
        for _, bet in pending.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            with col1:
                st.markdown(f"**{bet['home_team']} vs {bet['away_team']}**")
            with col2:
                st.markdown(f"🎯 {bet['pick']} @ {bet['odds']}")
            with col3:
                if st.button("✅ Win", key=f"w{bet['id']}", type="primary"):
                    tracker.update_result(bet['id'], 'win')
                    st.rerun()
            with col4:
                if st.button("❌ Loss", key=f"l{bet['id']}"):
                    tracker.update_result(bet['id'], 'loss')
                    st.rerun()
            with col5:
                if st.button("🔄 Push", key=f"p{bet['id']}"):
                    tracker.update_result(bet['id'], 'push')
                    st.rerun()
            st.divider()
    else:
        st.info("🎉 No pending bets! Time to add some!")

with tab4:
    all_bets = tracker.load_bets()
    if not all_bets.empty:
        # Format for display
        display_df = all_bets.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
        display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        display_df['stake'] = display_df['stake'].apply(lambda x: f"${x:.2f}")
        display_df['odds'] = display_df['odds'].apply(lambda x: f"{int(x)}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No bets in history yet.")
