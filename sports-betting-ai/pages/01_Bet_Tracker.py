# Bet Tracker Page
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bet Tracker", layout="wide")

st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Bet Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Track your bets and analyze performance</p>', unsafe_allow_html=True)

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bets", "0", "+0")
with col2:
    st.metric("Win Rate", "0%", "+0%")
with col3:
    st.metric("Profit", "$0", "$0")
with col4:
    st.metric("ROI", "0%", "+0%")

st.markdown("---")

# Add bet form
with st.expander("➕ Add New Bet"):
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
        st.text_input("Your Pick")
    with col2:
        st.number_input("Odds", value=-110)
        st.number_input("Stake ($)", value=10.0)
    st.button("Add Bet", use_container_width=True)

# Sample bets table
st.markdown("### 📋 Your Bets")
sample_bets = {
    'Date': ['2024-01-15', '2024-01-14', '2024-01-13'],
    'Sport': ['NBA', 'NFL', 'NBA'],
    'Pick': ['Lakers', 'Chiefs', 'Celtics'],
    'Odds': ['-150', '+200', '-110'],
    'Stake': ['$50', '$100', '$75'],
    'Result': ['Win', 'Win', 'Loss'],
    'P/L': ['+$33', '+$200', '-$75']
}
st.dataframe(pd.DataFrame(sample_bets), use_container_width=True, hide_index=True)
