"""
Bet Tracker Dashboard - Full betting history and ROI tracking
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bet_tracker import BetTracker

st.set_page_config(page_title="Bet Tracker 💰", page_icon="💰")

st.title("💰 Bet Tracker & ROI")

# Initialize tracker
tracker = BetTracker()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Bet", "📝 Pending Bets", "📈 Analytics"])

# TAB 1: Dashboard
with tab1:
    stats = tracker.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bets", stats['total_bets'])
    with col2:
        st.metric("Win Rate", f"{stats['win_rate']*100:.1f}%")
    with col3:
        profit = stats['total_profit']
        delta = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
        st.metric("Total Profit", f"${profit:.2f}", delta=delta.split('$')[1] if '$' in delta else delta)
    with col4:
        st.metric("ROI", f"{stats['roi']*100:.1f}%")
    
    st.markdown("---")
    
    # Bankroll growth chart
    bets = tracker.load_bets()
    settled = bets[bets['status'] == 'settled'].copy()
    
    if not settled.empty:
        settled['date'] = pd.to_datetime(settled['date'])
        settled = settled.sort_values('date')
        settled['cumulative_profit'] = settled['profit'].cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=settled['date'],
            y=settled['cumulative_profit'],
            mode='lines+markers',
            name='Cumulative Profit',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            title='Bankroll Over Time',
            xaxis_title='Date',
            yaxis_title='Profit ($)',
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No settled bets yet. Start tracking!")

# TAB 2: Add Bet
with tab2:
    st.subheader("Add New Bet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sport = st.selectbox("Sport", ['NBA', 'NFL', 'MLB', 'NHL'])
        home_team = st.text_input("Home Team")
        pick = st.selectbox("Your Pick", [home_team, "Away Team"])
    
    with col2:
        away_team = st.text_input("Away Team")
        odds = st.number_input("Odds", value=-110)
        stake = st.number_input("Stake ($)", value=10.0, min_value=1.0)
    
    # Kelly Calculator
    st.markdown("---")
    st.subheader("Kelly Criterion Calculator")
    model_prob = st.slider("Model Win Probability (%)", 1, 99, 55) / 100
    kelly = tracker.calculate_kelly_criterion(model_prob, odds)
    recommended = kelly * 100  # Assuming $100 bankroll for display
    
    st.markdown(f"**Recommended stake (Kelly):** {kelly*100:.1f}% of bankroll")
    st.markdown(f"**If $100 bankroll:** Bet ${recommended:.2f}")
    
    if st.button("Add Bet 💾", type="primary"):
        bet = tracker.add_bet(sport, home_team, away_team, pick, odds, stake)
        st.success(f"Bet added! ID: {bet['id']}")

# TAB 3: Pending Bets
with tab3:
    pending = tracker.get_pending_bets()
    
    if not pending.empty:
        st.subheader(f"Pending Bets ({len(pending)})")
        
        for _, bet in pending.iterrows():
            with st.expander(f"{bet['home_team']} vs {bet['away_team']} - ${bet['stake']}"):
                st.write(f"**Pick:** {bet['pick']}")
                st.write(f"**Odds:** {bet['odds']}")
                st.write(f"**Stake:** ${bet['stake']}")
                st.write(f"**Date:** {bet['date'][:10]}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ Win", key=f"win_{bet['id']}"):
                        tracker.update_result(bet['id'], 'win')
                        st.rerun()
                with col2:
                    if st.button(f"❌ Loss", key=f"loss_{bet['id']}"):
                        tracker.update_result(bet['id'], 'loss')
                        st.rerun()
                with col3:
                    if st.button(f"↩️ Push", key=f"push_{bet['id']}"):
                        tracker.update_result(bet['id'], 'push')
                        st.rerun()
    else:
        st.info("No pending bets. Great job!")

# TAB 4: Analytics
with tab4:
    st.subheader("📈 Performance by Sport")
    
    performance = tracker.get_performance_by_sport()
    if not performance.empty:
        performance['roi'] = performance['profit'] / performance['stake']
        
        fig = px.bar(
            performance,
            x='sport',
            y='roi',
            title='ROI by Sport',
            labels={'roi': 'ROI (%)', 'sport': 'Sport'},
            color='roi',
            color_continuous_scale=['red', 'yellow', 'green']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            performance.rename(columns={
                'sport': 'Sport',
                'profit': 'Profit',
                'stake': 'Total Staked',
                'result': 'Win Rate'
            }),
            hide_index=True
        )
    else:
        st.info("No settled bets to analyze.")
    
    # Export
    st.markdown("---")
    if st.button("📥 Export to CSV"):
        tracker.export_to_csv("bets_export.csv")
        st.success("Exported to bets_export.csv")

st.markdown("---")
st.caption("Track picks, calculate ROI, manage bankroll")
