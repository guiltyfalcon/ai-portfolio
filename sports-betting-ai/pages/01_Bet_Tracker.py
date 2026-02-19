"""
Bet Tracker - Enhanced with CSV export, filters, charts, and bankroll management
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bet_tracker import BetTracker

st.set_page_config(
    page_title="Bet Tracker 💰",
    page_icon="💰",
    layout="wide"
)

# Modern Dark Theme CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #00d26a 0%, #2ecc71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .bet-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .bet-card:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(255,255,255,0.2);
    }
    .win { border-left: 4px solid #00d26a; }
    .loss { border-left: 4px solid #ff4757; }
    .push { border-left: 4px solid #ffa502; }
    .profit-positive { color: #00d26a; font-weight: 700; }
    .profit-negative { color: #ff4757; font-weight: 700; }
    .profit-neutral { color: #ffa502; font-weight: 700; }
    .stat-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .filter-section {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .quick-btn {
        background: rgba(0,210,106,0.2);
        border: 1px solid #00d26a;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 0.8rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Bet Tracker Pro</div>', unsafe_allow_html=True)

# Initialize tracker
tracker = BetTracker()

# Sidebar - Bankroll & Settings
with st.sidebar:
    st.markdown("### 💵 Bankroll Management")
    
    # Get current bankroll
    current_bankroll = st.session_state.get('bankroll', 1000.0)
    new_bankroll = st.number_input(
        "Starting Bankroll ($)", 
        value=float(current_bankroll), 
        min_value=10.0, 
        step=50.0
    )
    
    if new_bankroll != current_bankroll:
        st.session_state['bankroll'] = new_bankroll
        st.success("✅ Bankroll updated!")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Actions")
    
    # Export bets
    if st.button("📥 Export to CSV", use_container_width=True):
        csv = tracker.export_to_csv()
        if csv:
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"bets_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No bets to export")
    
    # Clear all
    if st.button("🗑️ Clear All Bets", type="secondary", use_container_width=True):
        confirm = st.checkbox("⚠️ Confirm delete all bets?")
        if confirm:
            tracker.clear_all()
            st.success("✅ All bets cleared!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏆 Performance by Sport")
    
    # Sport breakdown
    sport_perf = tracker.get_performance_by_sport()
    if not sport_perf.empty:
        st.dataframe(sport_perf, use_container_width=True, hide_index=True)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Bet", "📝 Pending Bets", "📜 History"])

with tab1:
    stats = tracker.get_stats()
    
    # Stats row
    st.markdown("### 📊 Overall Statistics")
    cols = st.columns(5)
    
    with cols[0]:
        st.metric("Total Bets", stats['total_bets'])
    with cols[1]:
        st.metric("Wins", stats['wins'], delta=f"{stats['win_rate']*100:.1f}%")
    with cols[2]:
        st.metric("Losses", stats['losses'])
    with cols[3]:
        profit_color = "normal" if stats['total_profit'] >= 0 else "inverse"
        st.metric("Total Profit", f"${stats['total_profit']:.2f}", delta_color=profit_color)
    with cols[4]:
        st.metric("ROI", f"{stats['roi']*100:.1f}%")
    
    # Additional stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Win Rate", f"{stats['win_rate']*100:.1f}%")
    with col2:
        st.metric("Total Staked", f"${stats['total_staked']:.2f}")
    with col3:
        st.metric("Avg Odds", f"{stats['avg_odds']:.0f}")
    
    # Charts
    bets = tracker.load_bets()
    settled = bets[bets['status'] == 'settled'] if not bets.empty else pd.DataFrame()
    
    if not settled.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Profit Over Time")
            settled_sorted = settled.sort_values('date')
            settled_sorted['cumulative'] = settled_sorted['profit'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(len(settled_sorted))),
                y=settled_sorted['cumulative'],
                mode='lines+markers',
                line=dict(color='#00d26a', width=3),
                fill='tozeroy',
                fillcolor='rgba(0,210,106,0.2)',
                name='Cumulative Profit'
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300,
                xaxis_title="Bet #",
                yaxis_title="Profit ($)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Win/Loss Distribution")
            win_count = len(settled[settled['result'] == 'win'])
            loss_count = len(settled[settled['result'] == 'loss'])
            push_count = len(settled[settled['result'] == 'push'])
            
            fig2 = go.Figure(data=[go.Pie(
                labels=['Wins', 'Losses', 'Pushes'],
                values=[win_count, loss_count, push_count],
                marker_colors=['#00d26a', '#ff4757', '#ffa502'],
                hole=0.4
            )])
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Sport breakdown chart
        st.markdown("### 🏆 Performance by Sport")
        sport_perf = tracker.get_performance_by_sport()
        if not sport_perf.empty:
            fig3 = px.bar(
                sport_perf,
                x='sport',
                y='profit',
                color='profit',
                color_continuous_scale=['#ff4757', '#ffa502', '#00d26a'],
                title="Profit by Sport"
            )
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("🎯 No settled bets yet. Start tracking to see your performance!")

with tab2:
    st.markdown("### ➕ Add New Bet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sport = st.selectbox(
            "Sport",
            ['NBA', 'NFL', 'MLB', 'NHL', 'NCAAB', 'NCAAF', 'Soccer', 'Other']
        )
        home = st.text_input("Home Team", placeholder="e.g., Lakers")
        pick = st.text_input(
            "Your Pick",
            value=st.session_state.get('quick_pick', ''),
            placeholder="e.g., Lakers ML or Lakers -5.5"
        )
        
        # Quick pick buttons
        st.caption("⚡ Quick Pick:")
        qcol1, qcol2, qcol3 = st.columns(3)
        with qcol1:
            if st.button("🏠 Home ML", use_container_width=True):
                if home:
                    st.session_state['quick_pick'] = f"{home} ML"
                    st.rerun()
        with qcol2:
            away_team = st.session_state.get('away_team_input', '')
            if st.button("✈️ Away ML", use_container_width=True):
                if away_team:
                    st.session_state['quick_pick'] = f"{away_team} ML"
                    st.rerun()
        with qcol3:
            if st.button("🎯 Over", use_container_width=True):
                st.session_state['quick_pick'] = "Over"
                st.rerun()
    
    with col2:
        away = st.text_input(
            "Away Team",
            placeholder="e.g., Warriors",
            key="away_team_input"
        )
        
        odds_col, stake_col = st.columns(2)
        with odds_col:
            odds = st.number_input(
                "Odds",
                value=-110,
                help="American odds. -110 is standard, +150 is underdog"
            )
        with stake_col:
            stake = st.number_input(
                "Stake ($)",
                value=10.0,
                min_value=0.01,
                step=5.0
            )
        
        # Kelly Criterion calculator
        st.markdown("---")
        st.caption("💡 Kelly Criterion Calculator")
        kelly_prob = st.slider("Your Estimated Win %", 0, 100, 50) / 100
        
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        kelly = ((decimal_odds - 1) * kelly_prob - (1 - kelly_prob)) / (decimal_odds - 1)
        kelly_stake = max(0, kelly * st.session_state.get('bankroll', 1000) * 0.25)
        
        st.caption(f"💰 Recommended stake (Quarter Kelly): **${kelly_stake:.2f}**")
        
        if st.button("➕ Add Bet", type="primary", use_container_width=True):
            if home and away and pick:
                bet, error = tracker.add_bet(sport, home, away, pick, odds, stake)
                if bet:
                    st.success(f"✅ Bet #{bet['id']} added successfully!")
                    st.balloons()
                else:
                    st.error(f"❌ {error}")
            else:
                st.error("⚠️ Please fill in all fields")

with tab3:
    # Filters
    st.markdown("### 🔍 Filters")
    
    with st.container():
        fcol1, fcol2, fcol3 = st.columns(3)
        
        with fcol1:
            filter_sport = st.multiselect(
                "Filter by Sport",
                ['NBA', 'NFL', 'MLB', 'NHL', 'NCAAB', 'NCAAF', 'Soccer', 'Other']
            )
        
        with fcol2:
            date_range = st.date_input(
                "Date Range",
                [datetime.now() - timedelta(days=30), datetime.now() + timedelta(days=7)],
                key="date_filter"
            )
        
        with fcol3:
            sort_by = st.selectbox(
                "Sort By",
                ["Date (Newest)", "Date (Oldest)", "Stake (High)", "Odds"]
            )
    
    pending = tracker.get_pending_bets()
    
    # Apply filters
    if not pending.empty:
        if filter_sport:
            pending = pending[pending['sport'].isin(filter_sport)]
        
        if len(date_range) == 2:
            pending['date'] = pd.to_datetime(pending['date'])
            pending = pending[
                (pending['date'] >= pd.Timestamp(date_range[0])) &
                (pending['date'] <= pd.Timestamp(date_range[1]))
            ]
        
        # Sort
        if sort_by == "Date (Newest)":
            pending = pending.sort_values('date', ascending=False)
        elif sort_by == "Date (Oldest)":
            pending = pending.sort_values('date', ascending=True)
        elif sort_by == "Stake (High)":
            pending = pending.sort_values('stake', ascending=False)
        elif sort_by == "Odds":
            pending = pending.sort_values('odds', ascending=False)
    
    if not pending.empty:
        st.markdown(f"### 📝 Pending Bets ({len(pending)})")
        
        for _, bet in pending.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{bet['home_team']} vs {bet['away_team']}**")
                    st.caption(f"📅 {pd.to_datetime(bet['date']).strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    st.markdown(f"🎯 **{bet['pick']}**")
                    st.caption(f"Odds: {bet['odds']} | Stake: ${bet['stake']:.2f}")
                
                with col3:
                    if st.button("✅ Win", key=f"w{bet['id']}", type="primary"):
                        tracker.update_result(bet['id'], 'win')
                        st.rerun()
                
                with col4:
                    if st.button("❌ Loss", key=f"l{bet['id']}"):
                        tracker.update_result(bet['id'], 'loss')
                        st.rerun()
                
                with col5:
                    if st.button("🔄 Push", key=f"p{bet['id']}"):
                        tracker.update_result(bet['id'], 'push')
                        st.rerun()
                
                st.divider()
    else:
        st.info("🎉 No pending bets. Great job keeping up!")

with tab4:
    st.markdown("### 📜 Bet History")
    
    all_bets = tracker.load_bets()
    
    if not all_bets.empty:
        # Format for display
        display_df = all_bets.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
        display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        display_df['stake'] = display_df['stake'].apply(lambda x: f"${x:.2f}")
        display_df['odds'] = display_df['odds'].apply(lambda x: f"{int(x)}" if pd.notna(x) else "-")
        
        # Color code results
        def color_result(val):
            if val == 'win':
                return 'background-color: rgba(0,210,106,0.3)'
            elif val == 'loss':
                return 'background-color: rgba(255,71,87,0.3)'
            elif val == 'push':
                return 'background-color: rgba(255,165,2,0.3)'
            return ''
        
        styled_df = display_df.style.applymap(color_result, subset=['result'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No bets in history yet.")

st.markdown("---")
st.caption("💡 **Tip:** Use the Kelly Criterion calculator to optimize your bet sizing based on your edge.")
