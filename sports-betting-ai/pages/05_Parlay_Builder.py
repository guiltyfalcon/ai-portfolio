import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Parlay Builder 🎯",
    page_icon="🎯",
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
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa502 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .leg-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    .parlay-odds {
        background: linear-gradient(135deg, rgba(255,107,107,0.2) 0%, rgba(255,165,2,0.2) 100%);
        border: 1px solid rgba(255,107,107,0.3);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Parlay Builder</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Build parlays and calculate true probability vs implied odds
</div>
""", unsafe_allow_html=True)

# Parlay Legs
if 'parlay' not in st.session_state:
    st.session_state.parlay = []

# Add new leg
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
with col1:
    game = st.text_input("Game", placeholder="LAL vs GSW", key="parlay_game")
with col2:
    pick = st.text_input("Pick", placeholder="LAL ML", key="parlay_pick")
with col3:
    odds = st.number_input("Odds", value=-110, key="parlay_odds")
with col4:
    prob = st.number_input("Model %", value=55, min_value=1, max_value=99, key="parlay_prob")

if st.button("➕ Add Leg", type="primary"):
    if game and pick:
        st.session_state.parlay.append({
            'game': game, 'pick': pick, 'odds': odds, 'model_prob': prob/100
        })
        st.success(f"Added {pick}")

# Display parlay
if st.session_state.parlay:
    st.markdown("### Your Parlay")
    
    total_decimal = 1
    true_prob = 1
    
    for i, leg in enumerate(st.session_state.parlay):
        st.markdown(f'''
        <div class="leg-card">
            <div style="display: flex; justify-content: space-between;">
                <span><b>Leg {i+1}:</b> {leg['pick']}</span>
                <span style="color: #ff6b6b; font-weight: 700;">{leg['odds']:+d}</span>
            </div>
            <div style="color: #a0a0c0; font-size: 0.9rem;">{leg['game']} • Model: {leg['model_prob']*100:.0f}%</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Calculate
        if leg['odds'] > 0:
            dec = 1 + (leg['odds']/100)
        else:
            dec = 1 + (100/abs(leg['odds']))
        total_decimal *= dec
        true_prob *= leg['model_prob']
    
    # Summary
    implied = 1 / total_decimal
    edge = true_prob - implied
    
    st.markdown("---")
    st.markdown("### 📊 Analysis")
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Parlay Odds", f"{int((total_decimal-1)*100) if total_decimal > 2 else int(-100/(total_decimal-1)):+}")
    with cols[1]:
        st.metric("True Probability", f"{true_prob*100:.1f}%")
    with cols[2]:
        st.metric("Implied Probability", f"{implied*100:.1f}%")
    
    if edge > 0:
        st.success(f"✅ +{edge*100:.1f}% Edge - Good value!")
    else:
        st.warning(f"⚠️ {edge*100:.1f}% Edge - Sportsbook has advantage")
    
    if st.button("🗑️ Clear Parlay", type="secondary"):
        st.session_state.parlay = []
        st.rerun()

st.markdown("---")
st.caption("Build +EV parlays with proper probability math")
