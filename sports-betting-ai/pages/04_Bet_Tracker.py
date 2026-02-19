import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bet_tracker import BetTracker

st.set_page_config(
    page_title="Bet Tracker 💰",
    page_icon="💰",
    layout="wide"
)

# Modern Dark Theme
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
    .profit-positive { color: #00d26a; font-weight: 700; }
    .profit-negative { color: #ff4757; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Bet Tracker</div>', unsafe_allow_html=True)

# Initialize tracker
tracker = BetTracker()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Bet", "📝 Pending"])

with tab1:
    stats = tracker.get_stats()
    
    # Stats row
    cols = st.columns(4)
    with cols[0]:
        st.metric("Total Bets", stats['total_bets'])
    with cols[1]:
        st.metric("Win Rate", f"{stats['win_rate']*100:.1f}%")
    with cols[2]:
        profit_color = "normal" if stats['total_profit'] >= 0 else "inverse"
        st.metric("Total Profit", f"${stats['total_profit']:.2f}", delta_color=profit_color)
    with cols[3]:
        st.metric("ROI", f"{stats['roi']*100:.1f}%")
    
    # Chart
    bets = tracker.load_bets()
    settled = bets[bets['status'] == 'settled'] if not bets.empty else pd.DataFrame()
    
    if not settled.empty:
        st.markdown("### 📈 Profit Over Time")
        settled['cumulative'] = settled['profit'].cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=range(len(settled)),
            y=settled['cumulative'],
            mode='lines',
            line=dict(color='#00d26a', width=3),
            fill='tozeroy',
            fillcolor='rgba(0,210,106,0.2)'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### ➕ Add New Bet")
    
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL'])
        home = st.text_input("Home Team", placeholder="Lakers")
        pick = st.text_input("Your Pick", placeholder="Lakers ML")
    with col2:
        away = st.text_input("Away Team", placeholder="Warriors")
        odds = st.number_input("Odds", value=-110)
        stake = st.number_input("Stake ($)", value=10.0, min_value=1.0)
    
    if st.button("Add Bet", type="primary"):
        bet = tracker.add_bet(sport, home, away, pick, odds, stake)
        st.success(f"Bet #{bet['id']} added successfully!")

with tab3:
    pending = tracker.get_pending_bets()
    
    if not pending.empty:
        st.markdown(f"### Pending Bets ({len(pending)})")
        
        for _, bet in pending.iterrows():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f"**{bet['home_team']} vs {bet['away_team']}**")
                st.caption(f"Pick: {bet['pick']} @ {bet['odds']}")
            with col2:
                if st.button("✅ Win", key=f"w{bet['id']}"):
                    tracker.update_result(bet['id'], 'win')
                    st.rerun()
            with col3:
                if st.button("❌ Loss", key=f"l{bet['id']}"):
                    tracker.update_result(bet['id'], 'loss')
                    st.rerun()
            with col4:
                if st.button("🔄 Push", key=f"p{bet['id']}"):
                    tracker.update_result(bet['id'], 'push')
                    st.rerun()
            st.divider()
    else:
        st.info("No pending bets. Great job!")

st.markdown("---")
st.caption("Track your picks and calculate ROI")
