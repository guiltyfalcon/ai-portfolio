import streamlit as st
import numpy as np

st.set_page_config(page_title="Parlay Builder 🎯", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa502 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .leg-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
        padding: 15px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Parlay Builder</div>', unsafe_allow_html=True)

if 'parlay' not in st.session_state:
    st.session_state.parlay = []

st.markdown("### Add Leg")
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
with col1: game = st.text_input("Game", placeholder="LAL vs GSW")
with col2: pick = st.text_input("Pick", placeholder="LAL ML")
with col3: odds = st.number_input("Odds", value=-110)
with col4: prob = st.number_input("Win %", value=55, min_value=1, max_value=99)

if st.button("➕ Add Leg"):
    if game and pick:
        st.session_state.parlay.append({'game': game, 'pick': pick, 'odds': odds, 'prob': prob/100})
        st.success(f"Added: {pick}")

if st.session_state.parlay:
    st.markdown("### Your Parlay")
    total_decimal = 1
    true_prob = 1
    
    for i, leg in enumerate(st.session_state.parlay, 1):
        decimal = 1 + (leg['odds']/100) if leg['odds'] > 0 else 1 + (100/abs(leg['odds']))
        total_decimal *= decimal
        true_prob *= leg['prob']
        
        st.markdown(f'''
        <div class="leg-card">
            <strong>Leg {i}:</strong> {leg['pick']} ({leg['odds']:+})<br/>
            <span style="color: #888;">{leg['game']}</span>
        </div>
        ''', unsafe_allow_html=True)
    
    implied = 1 / total_decimal
    edge = true_prob - implied
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Parlay Odds", f"{int((total_decimal-1)*100):+}")
    col2.metric("True Prob", f"{true_prob*100:.1f}%")
    col3.metric("Implied", f"{implied*100:.1f}%")
    
    if edge > 0:
        st.success(f"✅ +{edge*100:.1f}% Edge - +EV!")
    else:
        st.error(f"⚠️ {edge*100:.1f}% Edge - Book has advantage")
    
    if st.button("🗑️ Clear"):
        st.session_state.parlay = []
        st.rerun()
