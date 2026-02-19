import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Player Props 🏀", page_icon="🏀", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .prop-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Player Props</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    player = st.selectbox("Player", ["LeBron James", "Stephen Curry", "Kevin Durant", "Luka Dončić"])
with col2:
    prop = st.selectbox("Prop", ["Points", "Rebounds", "Assists", "Threes"])
with col3:
    line = st.number_input("Line", value=26.5, step=0.5)

# Mock prediction
avg = {"Points": 28, "Rebounds": 8, "Assists": 7, "Threes": 3.5}.get(prop, 20)
over_prob = 0.6 if avg > line else 0.4

st.markdown("### 📊 Prediction")
cols = st.columns(3)
cols[0].metric("Player Avg", f"{avg}")
cols[1].metric("Over %", f"{over_prob*100:.0f}%")
cols[2].metric("Under %", f"{(1-over_prob)*100:.0f}%")

# Chart of last 5 games
games = np.random.normal(avg, 5, 5)
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(1, 6)), y=games, mode='lines+markers',
    line=dict(color='#00d2ff', width=3), marker=dict(size=10)))
fig.add_hline(y=line, line_dash="dash", line_color="#ff4757", annotation_text=f"Line: {line}")
fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'), height=300)
st.plotly_chart(fig, use_container_width=True)
