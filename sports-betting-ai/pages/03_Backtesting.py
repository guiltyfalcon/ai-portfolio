import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Backtesting 📈",
    page_icon="📈",
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
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .stat-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #a8edea;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Model Backtesting</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Historical performance and model accuracy
</div>
""", unsafe_allow_html=True)

# Stats
st.markdown("### 📊 Performance Summary")

cols = st.columns(4)
stats = [
    ("Total Bets", "247", "+12%"),
    ("Win Rate", "58.3%", "+3.2%"),
    ("Total ROI", "+8.7%", "+1.5%"),
    ("Avg Edge", "4.2%", "+0.8%")
]

for col, (label, value, delta) in zip(cols, stats):
    with col:
        st.markdown(f'''
        <div class="stat-card">
            <div style="color: #a0a0c0; font-size: 0.9rem; margin-bottom: 10px;">{label}</div>
            <div class="stat-value">{value}</div>
            <div style="color: #2ecc71; font-size: 0.8rem;">{delta}</div>
        </div>
        ''', unsafe_allow_html=True)

# Sample chart
st.markdown("---")
st.markdown("### 📉 ROI Over Time")

import numpy as np
import plotly.graph_objects as go

# Mock data
dates = pd.date_range('2025-01-01', periods=30, freq='D')
roi = np.cumsum(np.random.randn(30) * 0.02) + 100

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates, y=roi,
    fill='tozeroy',
    fillcolor='rgba(102,126,234,0.2)',
    line=dict(color='#667eea', width=3)
))
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=400
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Backtesting shows hypothetical performance")
