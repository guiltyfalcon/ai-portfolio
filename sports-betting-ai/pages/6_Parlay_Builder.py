"""
Parlay Builder - Build +EV parlays with true probability calculations
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Parlay Builder 🎯", page_icon="🎯")

st.title("🎯 Parlay Builder")

st.markdown("""
Build parlays and see the **true probability** vs **what sportsbooks imply**.

**How it works:**
- Add picks to your parlay
- We calculate the **combined true probability** (using model predictions)
- Compare to **implied parlay odds** 
- Find +EV parlays where true prob > implied
""")

# Initialize parlay in session state
if 'parlay' not in st.session_state:
    st.session_state.parlay = []

# Add new pick
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

with col1:
    game = st.text_input("Game", placeholder="Lakers vs Warriors")
with col2:
    pick = st.text_input("Pick", placeholder="Lakers ML")
with col3:
    odds = st.number_input("Odds", value=-110)
with col4:
    model_prob = st.number_input("Model %", value=55.0, min_value=1.0, max_value=99.0) / 100

if st.button("➕ Add to Parlay"):
    st.session_state.parlay.append({
        'game': game,
        'pick': pick,
        'odds': odds,
        'model_prob': model_prob
    })
    st.success(f"Added {pick} to parlay")

# Display parlay
if st.session_state.parlay:
    st.markdown("---")
    st.subheader(f"Your Parlay ({len(st.session_state.parlay)} legs)")
    
    parlay_df = pd.DataFrame(st.session_state.parlay)
    st.dataframe(parlay_df, hide_index=True)
    
    # Calculate parlay
    st.markdown("---")
    st.subheader("📊 Parlay Analysis")
    
    # Convert American to decimal
    def american_to_decimal(american):
        if american > 0:
            return 1 + (american / 100)
        else:
            return 1 + (100 / abs(american))
    
    # Combined odds
    combined_decimal = 1
    for pick in st.session_state.parlay:
        combined_decimal *= american_to_decimal(pick['odds'])
    
    # Convert back to American
    if combined_decimal >= 2:
        combined_american = int((combined_decimal - 1) * 100)
    else:
        combined_american = int(-100 / (combined_decimal - 1))
    
    # True probability (model)
    true_prob = 1
    for pick in st.session_state.parlay:
        true_prob *= pick['model_prob']
    
    # Implied probability (sportsbook)
    implied_prob = 1 / combined_decimal
    
    # Edge
    edge = true_prob - implied_prob
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Parlay Odds", f"{combined_american:+}")
        st.caption(f"Decimal: {combined_decimal:.2f}x")
    with col2:
        st.metric("True Probability", f"{true_prob*100:.1f}%")
    with col3:
        st.metric("Implied Probability", f"{implied_prob*100:.1f}%")
    
    # EV calculation
    stake = st.number_input("Stake ($)", value=10.0, min_value=1.0)
    expected_value = (true_prob * stake * combined_decimal) - stake
    
    if edge > 0:
        st.markdown(f"""
        ### ✅ +EV Parlay Detected!
        **Edge:** +{edge*100:.1f}%
        **Expected Value:** ${expected_value:.2f} on ${stake:.0f} stake
        """)
        st.balloons()
    else:
        st.markdown(f"""
        ### ❌ -EV Bet
        **Edge:** {edge*100:.1f}%
        **Expected Value:** ${expected_value:.2f}
        
        *Sportsbook has the edge here*
        """)
    
    # Parlay vs Singles comparison
    st.markdown("---")
    st.subheader("Parlay vs Singles")
    
    single_ev = sum([(p['model_prob'] * stake * american_to_decimal(p['odds'])) - stake 
                     for p in st.session_state.parlay])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Parlay EV", f"${expected_value:.2f}")
    with col2:
        st.metric("Singles EV (same total stake)", f"${single_ev:.2f}")
    
    if expected_value > single_ev:
        st.success("Parlay is better value! 🎉")
    else:
        st.info("Singles have better expected value.")
    
    # Clear button
    if st.button("🗑️ Clear Parlay"):
        st.session_state.parlay = []
        st.rerun()

else:
    st.info("Add your first pick to build a parlay")

st.markdown("---")
st.caption("Parlay Builder - calculate true probability, find +EV parlays")
