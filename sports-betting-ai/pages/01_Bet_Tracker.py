# AI Sports Betting App - Bet Tracker

import streamlit as st
import sys
import os
sys.path.insert(0, '/Users/djryan/.openclaw/workspace/user_upload')
from auth import check_session, login_form, logout, is_admin

# Check authentication
session = check_session()
if not session:
    st.set_page_config(page_title="Login - Bet Tracker", page_icon="🔒")
    login_form()
    st.stop()

st.set_page_config(page_title="Bet Tracker", layout="wide")

# Import bet tracker data module
try:
    from data.bet_tracker import BetTracker
    tracker = BetTracker()
    bet_tracker_available = True
except Exception as e:
    bet_tracker_available = False
    tracker = None

# Sidebar configuration
st.sidebar.title("Bet Tracker")

# Authentication section
if session:
    st.sidebar.markdown("### 👤 User")
    st.sidebar.write(f"**{session['username']}**")
    if session.get('is_admin'):
        st.sidebar.markdown("`🛡️ ADMIN`")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.markdown("---")

# Main content
st.title("📊 Bet Tracker")

if not bet_tracker_available:
    st.error("Bet Tracker module not available. Please check your installation.")
    st.stop()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 Active Bets", "➕ Add Bet", "📈 Stats & History"])

with tab1:
    st.subheader("Active Bets")
    
    # Get active bets
    active_bets = tracker.get_pending_bets()
    
    if active_bets.empty:
        st.info("No active bets. Add a bet to start tracking!")
    else:
        for _, bet in active_bets.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{bet['pick']}** vs {bet['away_team'] if bet['pick'] == bet['home_team'] else bet['home_team']}")
                    st.caption(f"{bet['sport']} • {bet.get('bet_type', 'Moneyline')}")
                with col2:
                    st.write(f"Odds: {bet['odds']}")
                    st.write(f"Stake: ${bet['stake']}")
                with col3:
                    potential = bet['stake'] * (bet['odds'] / 100) if bet['odds'] > 0 else bet['stake'] * (100 / abs(bet['odds']))
                    st.write(f"Potential: ${potential:.2f}")
                    if bet.get('model_confidence'):
                        st.caption(f"Model: {bet['model_confidence']}%")
                with col4:
                    if st.button("✓", key=f"win_{bet['id']}"):
                        tracker.update_result(int(bet['id']), 'win')
                        st.rerun()
                    if st.button("✗", key=f"loss_{bet['id']}"):
                        tracker.update_result(int(bet['id']), 'loss')
                        st.rerun()
                st.markdown("---")

with tab2:
    st.subheader("Add New Bet")
    
    with st.form("add_bet_form"):
        col1, col2 = st.columns(2)
        with col1:
            sport = st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
            team = st.text_input("Your Pick (Team)")
            opponent = st.text_input("Opponent")
        with col2:
            bet_type = st.selectbox("Bet Type", ["Moneyline", "Spread", "Over/Under", "Parlay"])
            odds = st.number_input("Odds", value=-110)
            stake = st.number_input("Stake ($)", min_value=0.0, value=10.0)
        
        model_confidence = st.slider("Model Confidence (%)", 0, 100, 50)
        notes = st.text_area("Notes (optional)")
        
        submitted = st.form_submit_button("Add Bet", use_container_width=True)
        
        if submitted:
            if team and opponent:
                bet_id = tracker.add_bet(
                    sport=sport,
                    team=team,
                    opponent=opponent,
                    bet_type=bet_type,
                    odds=odds,
                    stake=stake,
                    model_confidence=model_confidence,
                    notes=notes
                )
                st.success(f"Bet added! ID: {bet_id}")
            else:
                st.error("Please enter both team and opponent")

with tab3:
    st.subheader("Statistics & History")
    
    # Get stats
    stats = tracker.get_stats()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bets", stats['total_bets'])
    with col2:
        st.metric("Win Rate", f"{stats['win_rate']*100:.1f}%")
    with col3:
        profit_color = "normal" if stats['total_profit'] >= 0 else "inverse"
        st.metric("Total Profit", f"${stats['total_profit']:.2f}", delta_color=profit_color)
    with col4:
        st.metric("ROI", f"{stats['roi']:.1f}%")
    
    st.markdown("---")
    
    # Bet history
    st.subheader("Bet History")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox("Status", ["All", "Active", "Won", "Lost"])
    with col2:
        filter_sport = st.selectbox("Sport", ["All", "NBA", "NFL", "MLB", "NHL"])
    
    # Get all bets
    all_bets = tracker.load_bets()
    
    # Apply filters
    if filter_status != "All":
        status_map = {"Active": "pending", "Won": "won", "Lost": "lost"}
        if 'status' in all_bets.columns:
            all_bets = all_bets[all_bets['status'] == status_map.get(filter_status, all_bets['status'])]
    
    if filter_sport != "All":
        if 'sport' in all_bets.columns:
            all_bets = all_bets[all_bets['sport'] == filter_sport]
    
    if all_bets.empty:
        st.info("No bets found matching your filters")
    else:
        # Display as table
        bet_data = []
        for _, bet in all_bets.iterrows():
            bet_data.append({
                'Date': bet.get('date', ''),
                'Sport': bet.get('sport', ''),
                'Pick': bet.get('pick', ''),
                'Opponent': bet.get('away_team', '') if bet.get('pick') == bet.get('home_team') else bet.get('home_team', ''),
                'Type': bet.get('bet_type', 'Moneyline'),
                'Odds': bet.get('odds', -110),
                'Stake': f"${bet.get('stake', 0):.2f}",
                'Result': bet.get('status', 'pending').upper(),
                'P/L': f"${bet.get('profit', 0):.2f}"
            })
        
        df = pd.DataFrame(bet_data)
        st.dataframe(df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"bet_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.caption("Sports Betting AI Pro - Bet Tracker Module")
