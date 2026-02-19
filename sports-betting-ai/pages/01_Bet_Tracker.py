import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bet_tracker import BetTracker

st.set_page_config(
    page_title="Bet Tracker 💰",
    page_icon="💰",
    layout="wide"
)

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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Bet Tracker</div>', unsafe_allow_html=True)

tracker = BetTracker()

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
    col1, col2 = st.columns(2)
    
    with col1:
        sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL', 'Other'])
        home = st.text_input("Home Team", placeholder="Lakers")
        pick = st.text_input("Your Pick", placeholder="Lakers ML")
    
    with col2:
        away = st.text_input("Away Team", placeholder="Warriors")
        odds = st.number_input("Odds", value=-110)
        stake = st.number_input("Stake ($)", value=10.0, min_value=0.01)
    
    if st.button("Add Bet", type="primary", use_container_width=True):
        if home and away and pick:
            bet = tracker.add_bet(sport, home, away, pick, odds, stake)
            st.success(f"✅ Bet #{bet['id']} added!")
            st.balloons()
        else:
            st.error("Fill all fields")

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
        st.info("No pending bets!")

with tab4:
    all_bets = tracker.load_bets()
    if not all_bets.empty:
        st.dataframe(all_bets, use_container_width=True, hide_index=True)
    else:
        st.info("No bets in history")
