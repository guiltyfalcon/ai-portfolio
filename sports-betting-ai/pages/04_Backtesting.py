import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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

# Mock historical data
np.random.seed(42)
profits = np.random.randn(100) * 10 + 2
profits[0] = 0
cumulative = np.cumsum(profits)

st.markdown("### Performance")
cols = st.columns(4)
cols[0].metric("Total Bets", 100)
cols[1].metric("Win Rate", "55%")
cols[2].metric("Profit", f"${cumulative[-1]:.0f}")
cols[3].metric("ROI", "12.5%")

# Cumulative profit chart
fig = go.Figure()
fig.add_trace(go.Scatter(y=cumulative, mode='lines',
    line=dict(color='#00d26a', width=3), fill='tozeroy', fillcolor='rgba(0,210,106,0.2)'))
fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'), height=400)
st.plotly_chart(fig, use_container_width=True)

# Win/Loss pie
fig2 = go.Figure(data=[go.Pie(labels=['Wins', 'Losses'], values=[55, 45],
    marker_colors=['#00d26a', '#ff4757'], hole=0.4)])
fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300)
st.plotly_chart(fig2, use_container_width=True)
