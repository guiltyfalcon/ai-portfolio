import streamlit as st

st.set_page_config(
    page_title="Live Odds 📊",
    page_icon="📊",
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
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .odds-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    .bookmaker {
        background: rgba(0,210,255,0.1);
        border: 1px solid rgba(0,210,255,0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: #00d2ff;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Live Odds Comparison</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Compare odds across top sportsbooks
</div>
""", unsafe_allow_html=True)

st.info("🔌 Connect The Odds API to see live odds from DraftKings, FanDuel, BetMGM, and more")

# Supported bookmakers
st.markdown("### 📚 Supported Bookmakers")

cols = st.columns(5)
bookmakers = [
    ("DraftKings", "#1f77b4"),
    ("FanDuel", "#17becf"),
    ("BetMGM", "#d62728"),
    ("bet365", "#2ca02c"),
    ("Caesars", "#ff7f0e")
]

for (name, color), col in zip(bookmakers, cols):
    with col:
        st.markdown(f'''
        <div style="background: {color}20; border: 1px solid {color}; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="color: {color}; font-weight: 700; font-size: 1.1rem;">{name}</div>
        </div>
        ''', unsafe_allow_html=True)

st.markdown("---")
st.caption("Use the API key to unlock live odds comparison")
