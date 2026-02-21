# Live Odds Page
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Live Odds", layout="wide")

st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Live Odds</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time odds from multiple bookmakers</p>', unsafe_allow_html=True)

st.info("📊 Live odds data will appear here")

# Sample odds table
sample_data = {
    'Game': ['Lakers vs Warriors', 'Celtics vs Heat', 'Nets vs Bucks'],
    'Home ML': ['-150', '-200', '+120'],
    'Away ML': ['+130', '+170', '-140'],
    'Spread': ['LAL -3.5', 'BOS -5.5', 'BKN +3.5'],
    'Total': ['225.5', '218.5', '230.5']
}
st.dataframe(pd.DataFrame(sample_data), use_container_width=True, hide_index=True)
