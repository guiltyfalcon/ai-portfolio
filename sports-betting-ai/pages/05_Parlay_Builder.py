"""
Parlay Builder - Multi-leg bet calculator with EV analysis
"""

import streamlit as st
import pandas as pd
import numpy as np

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
    .edge-positive {
        color: #00d26a;
        font-weight: 700;
    }
    .edge-negative {
        color: #ff4757;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Parlay Builder</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #a0a0c0; margin-bottom: 30px;">
    Build multi-leg parlays and calculate true probability vs implied odds
</div>
""", unsafe_allow_html=True)

# Initialize parlay in session state
if 'parlay' not in st.session_state:
    st.session_state.parlay = []

# Add new leg
st.markdown("### ➕ Add Leg to Parlay")

col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

with col1:
    game = st.text_input("Game", placeholder="LAL vs GSW", key="parlay_game")

with col2:
    pick = st.text_input("Pick", placeholder="LAL ML", key="parlay_pick")

with col3:
    odds = st.number_input("Odds", value=-110, key="parlay_odds")

with col4:
    prob = st.number_input("Win %", value=55, min_value=1, max_value=99, key="parlay_prob",
                          help="Your estimated win probability for this leg")

if st.button("➕ Add Leg", type="primary"):
    if game and pick:
        st.session_state.parlay.append({
            'game': game,
            'pick': pick,
            'odds': odds,
            'model_prob': prob / 100
        })
        st.success(f"✅ Added: {pick}")
    else:
        st.error("⚠️ Please enter game and pick")

# Display current parlay
if st.session_state.parlay:
    st.markdown("---")
    st.markdown(f"### 🎯 Your Parlay ({len(st.session_state.parlay)} legs)")
    
    total_decimal = 1.0
    true_prob = 1.0
    
    for i, leg in enumerate(st.session_state.parlay, 1):
        # Calculate decimal odds
        if leg['odds'] > 0:
            decimal = 1 + (leg['odds'] / 100)
        else:
            decimal = 1 + (100 / abs(leg['odds']))
        
        total_decimal *= decimal
        true_prob *= leg['model_prob']
        
        # Determine if leg has edge
        implied = 1 / decimal
        edge = leg['model_prob'] - implied
        
        with st.container():
            st.markdown(f"""
            <div class="leg-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Leg {i}: {leg['pick']}</strong><br/>
                        <span style="color: #888; font-size: 0.9rem;">{leg['game']}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {'#00d26a' if edge > 0 else '#ff4757'}; font-weight: 700;">
                            {leg['odds']:+d}
                        </div>
                        <div style="font-size: 0.8rem; color: #888;">
                            Model: {leg['model_prob']*100:.0f}% | Implied: {implied*100:.1f}%
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Parlay calculations
    implied_prob = 1 / total_decimal
    edge = true_prob - implied_prob
    
    # Convert back to American odds
    if total_decimal >= 2.0:
        parlay_odds = int((total_decimal - 1) * 100)
    else:
        parlay_odds = int(-100 / (total_decimal - 1))
    
    st.markdown("---")
    st.markdown("### 📊 Parlay Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Parlay Odds", f"{parlay_odds:+d}")
    
    with col2:
        st.metric("True Probability", f"{true_prob*100:.2f}%")
    
    with col3:
        st.metric("Implied Probability", f"{implied_prob*100:.2f}%")
    
    # Edge display
    st.markdown("---")
    
    if edge > 0:
        st.success(f"✅ **+{edge*100:.2f}% Edge** - This parlay has positive expected value!")
        st.caption("💡 The combined probability of winning is higher than what the odds suggest.")
    else:
        st.error(f"⚠️ **{edge*100:.2f}% Edge** - Sportsbook has the advantage")
        st.caption("💡 The implied probability from odds is higher than your estimated true probability.")
    
    # Stake calculator
    st.markdown("---")
    st.markdown("### 💰 Stake Calculator")
    
    stake_col, calc_col = st.columns(2)
    
    with stake_col:
        stake = st.number_input("Your Stake ($)", value=10.0, min_value=1.0, step=5.0)
    
    with calc_col:
        potential_win = stake * (total_decimal - 1)
        expected_value = (true_prob * potential_win) - ((1 - true_prob) * stake)
        
        st.metric("Potential Win", f"${potential_win:.2f}")
        st.metric("Expected Value", f"${expected_value:.2f}", 
                 delta="+EV" if expected_value > 0 else "-EV")
    
    # Warning for high-leg parlays
    if len(st.session_state.parlay) >= 4:
        st.warning("⚠️ **High-leg parlays are high variance!** True probability drops exponentially with each leg added.")
    
    # Clear button
    if st.button("🗑️ Clear Parlay", type="secondary"):
        st.session_state.parlay = []
        st.rerun()

else:
    st.info("👆 Add legs to your parlay above to see the analysis")

# Educational section
st.markdown("---")
st.markdown("### 📚 How Parlay EV Works")

st.markdown("""
**Key Concepts:**

1. **True Probability** - Your model's estimated chance of all legs winning multiplied together
2. **Implied Probability** - What the odds say the chance should be (1 / decimal_odds)
3. **Edge** - True probability minus implied probability (positive = +EV bet)

**The Math:**
- Decimal Odds = American odds converted to decimal (e.g., -110 → 1.91)
- Parlay Decimal = Leg1 × Leg2 × Leg3 × ...
- True Probability = Your model's win% for each leg multiplied
- Expected Value = (True Prob × Potential Win) - (Lose Prob × Stake)

**Warning:**
Parlays are fun but high variance. Even with edge, hitting a 4-leg parlay at 60% per leg is only 13% true probability!
""")

st.markdown("---")
st.caption("💡 Build +EV parlays with proper probability math | Gamble responsibly")
