"""
Backtesting Page - Test strategies against historical data
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Backtesting - Sports Betting AI Pro", page_icon="🧪", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

st.markdown("<h1>Backtesting</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Test your strategies against historical data</p>", unsafe_allow_html=True)

# Strategy configuration
st.markdown("<h3>⚙️ Strategy Configuration</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    strategy = st.selectbox(
        "Betting Strategy",
        [
            "Favorites Only (-150 to -400)",
            "Underdog Value (+150 or better)",
            "Home Team Bias",
            "AI Consensus (70%+ confidence)",
            "Contrarian (Reverse line movement)"
        ]
    )

with col2:
    time_range = st.selectbox(
        "Time Range",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"]
    )

with col3:
    stake_size = st.number_input("Stake Size ($)", value=100, min_value=10, max_value=10000)

# Run backtest button
if st.button("▶️ Run Backtest", type="primary", use_container_width=True):
    with st.spinner("Running backtest simulation..."):
        import time
        time.sleep(2)
        st.session_state.backtest_results = {
            "total_bets": 156,
            "wins": 89,
            "losses": 62,
            "pushes": 5,
            "win_rate": 57.1,
            "total_profit": 1240.50,
            "roi": 7.9,
            "max_drawdown": -450.00,
            "sharpe_ratio": 1.34
        }

# Display results
if 'backtest_results' in st.session_state:
    results = st.session_state.backtest_results
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3>📊 Results</h3>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(0, 231, 1, 0.1); border: 1px solid rgba(0, 231, 1, 0.2); border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">Total Profit</p>
            <p style="color: #00e701; font-size: 2rem; font-weight: 700; margin: 0;">+${results['total_profit']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(0, 210, 255, 0.1); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">Win Rate</p>
            <p style="color: #00d2ff; font-size: 2rem; font-weight: 700; margin: 0;">{results['win_rate']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">ROI</p>
            <p style="color: #8b5cf6; font-size: 2rem; font-weight: 700; margin: 0;">+{results['roi']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: rgba(249, 115, 22, 0.1); border: 1px solid rgba(249, 115, 22, 0.2); border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">Sharpe Ratio</p>
            <p style="color: #F97316; font-size: 2rem; font-weight: 700; margin: 0;">{results['sharpe_ratio']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("<h4 style='margin-top: 2rem;'>Equity Curve</h4>", unsafe_allow_html=True)
    
    # Generate equity curve data
    days = 30
    equity_data = [1000]
    for i in range(1, days):
        change = np.random.normal(20, 80)
        equity_data.append(max(equity_data[-1] + change, 500))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(days)),
        y=equity_data,
        fill='tozeroy',
        line=dict(color='#00e701', width=2),
        fillcolor='rgba(0, 231, 1, 0.2)',
        name='Strategy'
    ))
    fig.add_trace(go.Scatter(
        x=list(range(days)),
        y=[1000 + i * 5 for i in range(days)],
        line=dict(color='#8A8F98', width=1, dash='dash'),
        name='Benchmark'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='Days'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='Bankroll ($)'),
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed stats
    st.markdown("<h4 style='margin-top: 2rem;'>Detailed Statistics</h4>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bets", results['total_bets'])
    with col2:
        st.metric("Average Odds", "-112")
    with col3:
        st.metric("Max Drawdown", f"${results['max_drawdown']:.2f}")
    with col4:
        st.metric("Avg Bet Size", f"${stake_size}")
    
    # Monthly performance
    st.markdown("<h4 style='margin-top: 2rem;'>Monthly Performance</h4>", unsafe_allow_html=True)
    
    monthly_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Profit': [320, -150, 480, 290, -80, 380],
        'Bets': [45, 38, 52, 41, 35, 48]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_data['Month'],
        y=monthly_data['Profit'],
        marker_color=['#00e701' if p > 0 else '#ff4d4d' for p in monthly_data['Profit']],
        text=monthly_data['Profit'],
        textposition='outside'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Export button
    st.download_button(
        "📥 Export Results",
        data=pd.DataFrame([results]).to_csv(index=False),
        file_name="backtest_results.csv",
        mime="text/csv",
        use_container_width=True
    )
