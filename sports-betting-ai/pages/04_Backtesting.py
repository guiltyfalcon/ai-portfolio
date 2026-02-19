import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bet_tracker import BetTracker

st.set_page_config(page_title="Backtesting 📈", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Backtesting</div>', unsafe_allow_html=True)

tracker = BetTracker()
bets = tracker.load_bets()

if bets.empty or len(bets[bets['status'] == 'settled']) == 0:
    st.warning("⚠️ No settled bets found")
    st.info("Add some bets and mark them as win/loss to see your performance analytics here!")
    
    # Show sample chart
    st.markdown("### Sample Performance (for demo)")
    import numpy as np
    np.random.seed(42)
    sample_profits = np.random.randn(50) * 10 + 2
    sample_profits[0] = 0
    sample_cum = np.cumsum(sample_profits)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=sample_cum, mode='lines', fill='tozeroy',
        line=dict(color='#00d26a'), fillcolor='rgba(0,210,106,0.2)'))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'), height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📊 Add real bets to see your actual performance")
else:
    settled = bets[bets['status'] == 'settled']
    
    # Calculate metrics
    total_bets = len(settled)
    wins = len(settled[settled['result'] == 'win'])
    losses = len(settled[settled['result'] == 'loss'])
    pushes = len(settled[settled['result'] == 'push'])
    total_profit = settled['profit'].sum()
    roi = (total_profit / settled['stake'].sum()) * 100 if settled['stake'].sum() > 0 else 0
    win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
    
    st.markdown("### Performance Summary")
    cols = st.columns(4)
    cols[0].metric("Total Bets", total_bets)
    cols[1].metric("Win Rate", f"{win_rate*100:.1f}%")
    cols[2].metric("Total Profit", f"${total_profit:.2f}")
    cols[3].metric("ROI", f"{roi:.1f}%")
    
    # Cumulative profit chart
    st.markdown("### Cumulative Profit")
    settled_sorted = settled.sort_values('date')
    settled_sorted['cumulative'] = settled_sorted['profit'].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=settled_sorted['date'],
        y=settled_sorted['cumulative'],
        mode='lines',
        line=dict(color='#00d26a', width=3),
        fill='tozeroy',
        fillcolor='rgba(0,210,106,0.2)'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        xaxis_title="Date",
        yaxis_title="Profit ($)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Win/Loss breakdown by sport
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Win/Loss")
        fig2 = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses', 'Pushes'],
            values=[wins, losses, pushes],
            marker_colors=['#00d26a', '#ff4757', '#ffa502'],
            hole=0.4
        )])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("### By Sport")
        sport_stats = settled.groupby('sport').agg({
            'profit': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'bets'}).reset_index()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=sport_stats['sport'],
            y=sport_stats['profit'],
            marker_color=['#00d26a' if p >= 0 else '#ff4757' for p in sport_stats['profit']]
        ))
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=300,
            xaxis_title="Sport",
            yaxis_title="Profit ($)"
        )
        st.plotly_chart(fig3, use_container_width=True)
