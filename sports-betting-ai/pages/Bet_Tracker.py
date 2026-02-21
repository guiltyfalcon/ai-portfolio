"""
Bet Tracker Page - Track and manage your bets
"""
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Bet Tracker - Sports Betting AI Pro", page_icon="📊", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .bet-card {
        background: rgba(21, 26, 38, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .badge-win { background: rgba(0, 231, 1, 0.15); color: #00e701; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .badge-loss { background: rgba(255, 77, 77, 0.15); color: #ff4d4d; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .badge-pending { background: rgba(0, 210, 255, 0.15); color: #00d2ff; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Bet Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Manage and analyze your bets</p>", unsafe_allow_html=True)

# Initialize bets in session state
if 'bets' not in st.session_state:
    st.session_state.bets = [
        {"id": 1, "event": "Lakers vs Warriors", "selection": "Lakers +3.5", "odds": -110, "stake": 100, "status": "win", "profit": 90.91, "sport": "NBA", "date": "2024-01-15"},
        {"id": 2, "event": "Celtics vs Nuggets", "selection": "Celtics ML", "odds": -145, "stake": 145, "status": "loss", "profit": -145, "sport": "NBA", "date": "2024-01-14"},
        {"id": 3, "event": "Chiefs vs 49ers", "selection": "Over 47.5", "odds": -110, "stake": 110, "status": "win", "profit": 100, "sport": "NFL", "date": "2024-01-13"},
        {"id": 4, "event": "Ravens vs Lions", "selection": "Ravens -3", "odds": -105, "stake": 105, "status": "win", "profit": 100, "sport": "NFL", "date": "2024-01-12"},
        {"id": 5, "event": "Yankees vs Dodgers", "selection": "Yankees ML", "odds": 135, "stake": 100, "status": "loss", "profit": -100, "sport": "MLB", "date": "2024-01-10"},
    ]

# Stats
bets = st.session_state.bets
wins = len([b for b in bets if b["status"] == "win"])
losses = len([b for b in bets if b["status"] == "loss"])
pending = len([b for b in bets if b["status"] == "pending"])
total_profit = sum(b["profit"] for b in bets)
win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bets", len(bets))
with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%")
with col3:
    st.metric("Total Profit", f"${total_profit:.2f}", delta=f"{total_profit/1000*100:.1f}% ROI")
with col4:
    st.metric("Current Streak", "+3")

# Add Bet Button
if st.button("➕ Add New Bet", use_container_width=True):
    st.session_state.show_add_bet = True

# Add Bet Form
if st.session_state.get('show_add_bet', False):
    with st.form("add_bet_form"):
        st.subheader("Add New Bet")
        col1, col2 = st.columns(2)
        with col1:
            sport = st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL", "NCAAB", "NCAAF", "Soccer", "UFC"])
            event = st.text_input("Event", placeholder="Lakers vs Warriors")
            bet_type = st.selectbox("Bet Type", ["Moneyline", "Spread", "Total", "Parlay", "Prop"])
        with col2:
            selection = st.text_input("Selection", placeholder="Lakers +3.5")
            odds = st.number_input("Odds", value=-110)
            stake = st.number_input("Stake ($)", value=100.0, min_value=1.0)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Cancel"):
                st.session_state.show_add_bet = False
                st.rerun()
        with col2:
            if st.form_submit_button("Add Bet", type="primary"):
                potential_payout = stake + (stake * abs(odds) / 100) if odds < 0 else stake + (stake * odds / 100)
                new_bet = {
                    "id": len(st.session_state.bets) + 1,
                    "sport": sport,
                    "event": event,
                    "selection": selection,
                    "odds": odds,
                    "stake": stake,
                    "status": "pending",
                    "profit": 0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.bets.append(new_bet)
                st.session_state.show_add_bet = False
                st.success("Bet added successfully!")
                st.rerun()

# Filters
st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1.5rem 0;'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    filter_sport = st.selectbox("Filter by Sport", ["All", "NBA", "NFL", "MLB", "NHL"])
with col2:
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Win", "Loss"])
with col3:
    search = st.text_input("Search", placeholder="Search events...")

# Filter bets
filtered_bets = bets
if filter_sport != "All":
    filtered_bets = [b for b in filtered_bets if b["sport"] == filter_sport]
if filter_status != "All":
    filtered_bets = [b for b in filtered_bets if b["status"].lower() == filter_status.lower()]
if search:
    filtered_bets = [b for b in filtered_bets if search.lower() in b["event"].lower()]

# Display bets
st.subheader(f"Your Bets ({len(filtered_bets)})")

for bet in filtered_bets:
    status_class = f"badge-{bet['status']}"
    profit_color = "#00e701" if bet["profit"] > 0 else "#ff4d4d" if bet["profit"] < 0 else "#8A8F98"
    profit_sign = "+" if bet["profit"] > 0 else ""
    
    with st.container():
        st.markdown(f"""
        <div class="bet-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                        <span style="color: #00d2ff; font-size: 0.75rem; font-weight: 500;">{bet['sport']}</span>
                        <span style="color: #8A8F98; font-size: 0.75rem;">•</span>
                        <span style="color: #8A8F98; font-size: 0.75rem;">{bet['date']}</span>
                    </div>
                    <p style="color: white; font-weight: 500; margin: 0;">{bet['event']}</p>
                    <p style="color: #8A8F98; font-size: 0.875rem; margin: 0;">{bet['selection']}</p>
                </div>
                <div style="text-align: right;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div>
                            <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Odds</p>
                            <p style="color: white; font-family: monospace; margin: 0;">{bet['odds']}</p>
                        </div>
                        <div>
                            <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Stake</p>
                            <p style="color: white; font-family: monospace; margin: 0;">${bet['stake']:.0f}</p>
                        </div>
                        <div>
                            <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">Profit</p>
                            <p style="color: {profit_color}; font-family: monospace; margin: 0;">{profit_sign}${bet['profit']:.2f}</p>
                        </div>
                        <span class="{status_class}">{bet['status'].upper()}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons for pending bets
        if bet["status"] == "pending":
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("✅ Win", key=f"win_{bet['id']}"):
                    bet["status"] = "win"
                    if bet["odds"] < 0:
                        bet["profit"] = bet["stake"] * (100 / abs(bet["odds"]))
                    else:
                        bet["profit"] = bet["stake"] * (bet["odds"] / 100)
                    st.rerun()
            with col2:
                if st.button("❌ Loss", key=f"loss_{bet['id']}"):
                    bet["status"] = "loss"
                    bet["profit"] = -bet["stake"]
                    st.rerun()

# Export/Import buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Export to CSV"):
        df = pd.DataFrame(st.session_state.bets)
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "bets.csv", "text/csv")
with col2:
    st.button("📤 Import from CSV")
