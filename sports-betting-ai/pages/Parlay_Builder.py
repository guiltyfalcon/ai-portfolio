"""
Parlay Builder Page - Build your perfect parlay
"""
import streamlit as st

st.set_page_config(page_title="Parlay Builder - Sports Betting AI Pro", page_icon="🎯", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

# Shared Navigation Function
def show_page_nav():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="
                width: 40px; 
                height: 40px; 
                margin: 0 auto 0.5rem;
                background: linear-gradient(135deg, #00d2ff 0%, #00e701 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
            ">🎯</div>
            <h4 style="margin: 0; color: white; font-size: 1rem;">Sports Betting AI</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⊕  Dashboard", use_container_width=True):
            st.switch_page("Home.py")
        if st.button("◈  Odds", use_container_width=True):
            st.switch_page("pages/Live_Odds.py")
        if st.button("❖  Props", use_container_width=True):
            st.switch_page("pages/Player_Props.py")
        if st.button("⛓  Parlay", use_container_width=True):
            st.switch_page("pages/Parlay_Builder.py")
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1rem 0;'>", unsafe_allow_html=True)
        
        if st.button("○  Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

show_page_nav()

# Initialize session state
if 'parlay_legs' not in st.session_state:
    st.session_state.parlay_legs = []

st.markdown("<h1>Parlay Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8A8F98; margin-bottom: 2rem;'>Build your perfect parlay with AI insights</p>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # AI Recommended Picks
    st.markdown("<h3>🤖 AI Recommended Picks</h3>", unsafe_allow_html=True)
    
    ai_picks = [
        {"game": "Lakers vs Warriors", "pick": "Lakers +3.5", "confidence": 78, "ev": 5.2, "odds": -110},
        {"game": "Celtics vs Nuggets", "pick": "Over 224.5", "confidence": 72, "ev": 3.8, "odds": -110},
        {"game": "Chiefs vs 49ers", "pick": "Chiefs ML", "confidence": 68, "ev": 2.5, "odds": -165},
    ]
    
    pick_cols = st.columns(3)
    for col, pick in zip(pick_cols, ai_picks):
        with col:
            st.markdown(f"""
            <div style="background: rgba(0, 210, 255, 0.1); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 12px; padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="color: #00d2ff; font-size: 0.75rem;">{pick['confidence']}% Confidence</span>
                </div>
                <p style="color: white; font-weight: 500; margin: 0;">{pick['pick']}</p>
                <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">{pick['game']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                    <span style="color: #00e701; font-size: 0.75rem;">+{pick['ev']}% EV</span>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{pick['odds']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"➕ Add", key=f"add_ai_{pick['pick']}", use_container_width=True):
                leg = {
                    "id": len(st.session_state.parlay_legs),
                    "selection": pick['pick'],
                    "odds": pick['odds'],
                    "game": pick['game']
                }
                st.session_state.parlay_legs.append(leg)
                st.rerun()
    
    # Available Games
    st.markdown("<h3 style='margin-top: 2rem;'>Available Games</h3>", unsafe_allow_html=True)
    
    games = [
        {
            "sport": "NBA",
            "home": "Lakers",
            "away": "Warriors",
            "ml_home": -140,
            "ml_away": 120,
            "spread": -3.5,
            "spread_odds": -110,
            "total": 228.5,
            "total_odds": -110,
        },
        {
            "sport": "NFL",
            "home": "Chiefs",
            "away": "49ers",
            "ml_home": -165,
            "ml_away": 140,
            "spread": -3,
            "spread_odds": -110,
            "total": 47.5,
            "total_odds": -110,
        },
    ]
    
    for game in games:
        with st.expander(f"{game['sport']}: {game['home']} vs {game['away']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("<p style='color: #8A8F98; font-size: 0.75rem;'>Moneyline</p>", unsafe_allow_html=True)
                if st.button(f"{game['home']} {game['ml_home']}", key=f"ml_home_{game['home']}", use_container_width=True):
                    st.session_state.parlay_legs.append({
                        "id": len(st.session_state.parlay_legs),
                        "selection": f"{game['home']} ML",
                        "odds": game['ml_home'],
                        "game": f"{game['home']} vs {game['away']}"
                    })
                    st.rerun()
                if st.button(f"{game['away']} {game['ml_away']}", key=f"ml_away_{game['away']}", use_container_width=True):
                    st.session_state.parlay_legs.append({
                        "id": len(st.session_state.parlay_legs),
                        "selection": f"{game['away']} ML",
                        "odds": game['ml_away'],
                        "game": f"{game['home']} vs {game['away']}"
                    })
                    st.rerun()
            
            with col2:
                st.markdown("<p style='color: #8A8F98; font-size: 0.75rem;'>Spread</p>", unsafe_allow_html=True)
                if st.button(f"{game['home']} {game['spread']} ({game['spread_odds']})", key=f"spread_home_{game['home']}", use_container_width=True):
                    st.session_state.parlay_legs.append({
                        "id": len(st.session_state.parlay_legs),
                        "selection": f"{game['home']} {game['spread']}",
                        "odds": game['spread_odds'],
                        "game": f"{game['home']} vs {game['away']}"
                    })
                    st.rerun()
                if st.button(f"{game['away']} +{abs(game['spread'])} ({game['spread_odds']})", key=f"spread_away_{game['away']}", use_container_width=True):
                    st.session_state.parlay_legs.append({
                        "id": len(st.session_state.parlay_legs),
                        "selection": f"{game['away']} +{abs(game['spread'])}",
                        "odds": game['spread_odds'],
                        "game": f"{game['home']} vs {game['away']}"
                    })
                    st.rerun()
            
            with col3:
                st.markdown("<p style='color: #8A8F98; font-size: 0.75rem;'>Total</p>", unsafe_allow_html=True)
                if st.button(f"Over {game['total']} ({game['total_odds']})", key=f"over_{game['home']}", use_container_width=True):
                    st.session_state.parlay_legs.append({
                        "id": len(st.session_state.parlay_legs),
                        "selection": f"Over {game['total']}",
                        "odds": game['total_odds'],
                        "game": f"{game['home']} vs {game['away']}"
                    })
                    st.rerun()
                if st.button(f"Under {game['total']} ({game['total_odds']})", key=f"under_{game['home']}", use_container_width=True):
                    st.session_state.parlay_legs.append({
                        "id": len(st.session_state.parlay_legs),
                        "selection": f"Under {game['total']}",
                        "odds": game['total_odds'],
                        "game": f"{game['home']} vs {game['away']}"
                    })
                    st.rerun()

with col2:
    # Parlay Ticket
    st.markdown("<h3>🎫 Your Parlay</h3>", unsafe_allow_html=True)
    
    legs = st.session_state.parlay_legs
    
    if not legs:
        st.markdown("""
        <div style="background: rgba(21, 26, 38, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 2rem; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">➕</div>
            <p style="color: #8A8F98;">Add selections to build your parlay</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Calculate parlay odds
        decimal_odds = 1
        for leg in legs:
            if leg['odds'] > 0:
                decimal_odds *= (leg['odds'] / 100 + 1)
            else:
                decimal_odds *= (100 / abs(leg['odds']) + 1)
        
        if decimal_odds > 2:
            parlay_odds = int((decimal_odds - 1) * 100)
        else:
            parlay_odds = int(-100 / (decimal_odds - 1))
        
        # Display legs
        for idx, leg in enumerate(legs):
            st.markdown(f"""
            <div style="background: rgba(11, 14, 20, 0.8); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="color: #00d2ff; font-size: 0.75rem;">Leg {idx + 1}</span>
                        <p style="color: white; font-weight: 500; margin: 0; font-size: 0.875rem;">{leg['selection']}</p>
                        <p style="color: #8A8F98; font-size: 0.75rem; margin: 0;">{leg['game']}</p>
                    </div>
                    <span style="color: #00d2ff; font-family: monospace; font-weight: 600;">{leg['odds']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("❌", key=f"remove_{leg['id']}"):
                st.session_state.parlay_legs.pop(idx)
                st.rerun()
        
        # Stake input
        stake = st.number_input("Stake ($)", value=100, min_value=1)
        
        # Quick stake buttons
        cols = st.columns(4)
        for col, amount in zip(cols, [25, 50, 100, 250]):
            with col:
                if st.button(f"${amount}", key=f"stake_{amount}", use_container_width=True):
                    st.session_state.parlay_stake = amount
        
        # Calculate payout
        if parlay_odds > 0:
            payout = stake + (stake * parlay_odds / 100)
        else:
            payout = stake + (stake * 100 / abs(parlay_odds))
        
        profit = payout - stake
        
        # Summary
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1rem 0;'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<p style='color: #8A8F98; margin: 0;'>Parlay Odds</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: white; font-family: monospace; font-size: 1.5rem; font-weight: 600; margin: 0;'>{parlay_odds}</p>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p style='color: #8A8F98; margin: 0;'>Potential Payout</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00e701; font-family: monospace; font-size: 1.5rem; font-weight: 600; margin: 0;'>${payout:.2f}</p>", unsafe_allow_html=True)
        
        st.markdown(f"<p style='color: #00e701; font-weight: 600; margin-top: 0.5rem;'>+${profit:.2f} profit</p>", unsafe_allow_html=True)
        
        # Win probability
        implied_prob = (1 / decimal_odds) * 100
        st.markdown(f"<p style='color: #8A8F98; font-size: 0.875rem; margin-top: 1rem;'>Win Probability: {implied_prob:.1f}%</p>", unsafe_allow_html=True)
        st.progress(implied_prob / 100)
        
        # Action buttons
        st.button("🎯 Place Parlay", type="primary", use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("📋 Copy", use_container_width=True)
        with col2:
            st.button("📤 Share", use_container_width=True)
        
        # Risk level
        risk_level = "Low" if len(legs) <= 2 else "Medium" if len(legs) <= 4 else "High"
        risk_color = "#00e701" if risk_level == "Low" else "#F97316" if risk_level == "Medium" else "#ff4d4d"
        st.markdown(f"<p style='color: #8A8F98; margin-top: 1rem;'>Risk Level: <span style='color: {risk_color}; font-weight: 600;'>{risk_level}</span></p>", unsafe_allow_html=True)
