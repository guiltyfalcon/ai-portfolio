"""
Backtesting Dashboard - Model performance over time
Show model accuracy, ROI, and confidence calibration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Backtesting 📈", page_icon="📈")

st.title("📈 Model Backtesting")

st.markdown("""
**Track model performance over time.**

See how predictions would have performed historically.
""")

# Mock backtesting data (in production, this would load from database)
@st.cache_data
def load_backtest_data():
    """Load historical prediction data."""
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    return pd.DataFrame({
        'date': dates,
        'predictions_made': np.random.poisson(5, len(dates)),
        'correct_predictions': np.random.poisson(3, len(dates)),
        'roi': np.random.normal(0.02, 0.05, len(dates))
    })

data = load_backtest_data()
data['cumulative_roi'] = (1 + data['roi']).cumprod() - 1
data['accuracy'] = data['correct_predictions'] / (data['predictions_made'] + 0.001)

# Summary stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_preds = data['predictions_made'].sum()
    st.metric("Total Predictions", total_preds)

with col2:
    total_correct = data['correct_predictions'].sum()
    accuracy = total_correct / total_preds if total_preds > 0 else 0
    st.metric("Model Accuracy", f"{accuracy*100:.1f}%")

with col3:
    total_roi = data['cumulative_roi'].iloc[-1]
    st.metric("Cumulative ROI", f"{total_roi*100:.1f}%")

with col4:
    avg_daily = data['roi'].mean()
    st.metric("Avg Daily ROI", f"{avg_daily*100:.2f}%")

st.markdown("---")

# Charts
tab1, tab2, tab3 = st.tabs(["ROI Over Time", "Accuracy", "Calibration"])

with tab1:
    # ROI Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['cumulative_roi'] * 100,
        mode='lines',
        name='Cumulative ROI',
        line=dict(color='#2ecc71', width=3)
    ))
    fig.add_trace(go.Bar(
        x=data['date'],
        y=data['roi'] * 100,
        name='Daily ROI',
        marker_color='rgba(102, 126, 234, 0.5)'
    ))
    fig.update_layout(
        title='Model ROI Performance',
        xaxis_title='Date',
        yaxis_title='ROI (%)',
        template='plotly_white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Accuracy Chart
    fig = px.line(
        data,
        x='date',
        y='accuracy',
        title='Daily Prediction Accuracy',
        labels={'accuracy': 'Accuracy (%)', 'date': 'Date'}
    )
    fig.add_hline(y=0.52, line_dash="dash", line_color="red", 
                  annotation_text="Break-even (52%)")
    fig.update_traces(line_color='#667eea')
    st.plotly_chart(fig, use_container_width=True)
    
    # Accuracy by confidence bucket
    st.subheader("Accuracy by Confidence Bucket")
    
    # Mock confidence buckets
    buckets = pd.DataFrame({
        'confidence': ['50-55%', '55-60%', '60-65%', '65-70%', '70%+'],
        'predictions': [145, 120, 85, 45, 25],
        'wins': [71, 66, 49, 28, 17]
    })
    buckets['accuracy'] = buckets['wins'] / buckets['predictions']
    
    fig = px.bar(
        buckets,
        x='confidence',
        y='accuracy',
        title='Accuracy by Model Confidence',
        labels={'accuracy': 'Win Rate', 'confidence': 'Confidence Bucket'}
    )
    fig.add_hline(y=0.52, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Calibration plot
    st.subheader("Model Calibration")
    st.markdown("How well does predicted probability match actual win rate?")
    
    # Mock calibration data
    calibration = pd.DataFrame({
        'predicted_prob': [0.52, 0.55, 0.58, 0.62, 0.65, 0.70, 0.75],
        'actual_win_rate': [0.51, 0.53, 0.57, 0.61, 0.64, 0.71, 0.74],
        'sample_size': [100, 85, 70, 55, 40, 30, 20]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Perfect Calibration',
        line=dict(dash='dash', color='gray')
    ))
    fig.add_trace(go.Scatter(
        x=calibration['predicted_prob'],
        y=calibration['actual_win_rate'],
        mode='markers+text',
        name='Model Calibration',
        text=calibration['sample_size'].astype(str),
        textposition='top center',
        marker=dict(size=calibration['sample_size'] * 2, color='#667eea'),
        texttemplate='n=%{text}'
    ))
    fig.update_layout(
        title='Calibration Plot (n=sample size)',
        xaxis_title='Predicted Probability',
        yaxis_title='Actual Win Rate',
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if st.checkbox("Show explanation"):
        st.markdown("""
        **What is calibration?**
        
        - Points on the dashed line = perfect predictions
        - Above line = model underconfident (wins more than predicted)
        - Below line = model overconfident (wins less than predicted)
        
        **Interpretation:**
        - When we predict 70% win rate, we should win ~70% of the time
        - If we only win 60%, the model is overconfident
        """)

st.markdown("---")

# Sport breakdown
st.subheader("📊 Performance by Sport")

sport_performance = pd.DataFrame({
    'Sport': ['NBA', 'NFL', 'MLB', 'NHL'],
    'Predictions': [450, 380, 120, 240],
    'Wins': [239, 197, 58, 126],
    'ROI': [0.081, 0.052, 0.034, 0.061]
})
sport_performance['Win Rate'] = sport_performance['Wins'] / sport_performance['Predictions']

fig = px.scatter(
    sport_performance,
    x='Win Rate',
    y='ROI',
    size='Predictions',
    color='Sport',
    title='ROI vs Win Rate by Sport',
    labels={'Win Rate': 'Win Rate (%)', 'ROI': 'ROI (%)'},
    text='Sport'
)
fig.update_traces(textposition='top center')
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(sport_performance.style.format({
    'Win Rate': '{:.1%}',
    'ROI': '{:.1%}'
}), hide_index=True)

st.markdown("---")
st.caption("Backtesting shows hypothetical performance. Past results don't guarantee future success.")
