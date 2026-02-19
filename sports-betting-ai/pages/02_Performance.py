import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Performance", page_icon="📈")

st.title("📈 Model Performance & ROI Tracking")

# Mock data for visualization
dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
roi = [100 + (i * 2 + (i % 5) * 3 - (i % 7)) for i in range(30)]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates,
    y=roi,
    mode='lines+markers',
    name='Bankroll',
    fill='tozeroy',
    line=dict(color='#667eea', width=2)
))
fig.update_layout(
    title='Bankroll Over Time',
    xaxis_title='Date',
    yaxis_title='Units',
    template='plotly_white',
    height=400
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### Key Metrics
- **Total Bets**: 0
- **Win Rate**: 0%
- **ROI**: 0%
- **Avg Edge**: 0%
- **Current Bankroll**: 100 units

*Start making predictions to see your performance!*
""")
