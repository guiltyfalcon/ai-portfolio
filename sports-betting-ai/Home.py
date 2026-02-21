import streamlit as st
import hashlib
import time
from datetime import datetime
import json
import os

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@betai.pro"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# Session management
SESSION_DURATION = 24 * 60 * 60  # 24 hours

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(username, is_admin=False):
    """Create a new session"""
    session = {
        'username': username,
        'is_admin': is_admin,
        'created_at': time.time(),
        'expires_at': time.time() + SESSION_DURATION
    }
    st.session_state['auth_session'] = session
    return session

def check_session():
    """Check if user has valid session"""
    if 'auth_session' not in st.session_state or st.session_state['auth_session'] is None:
        return None
    
    session = st.session_state['auth_session']
    
    # Check if session expired
    if time.time() > session.get('expires_at', 0):
        st.session_state['auth_session'] = None
        return None
    
    return session

def logout():
    """Clear user session"""
    st.session_state['auth_session'] = None
    st.rerun()

def is_admin():
    """Check if current user is admin"""
    session = check_session()
    return session and session.get('is_admin', False)

# User storage
USERS_FILE = ".users.json"

def load_users():
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def signup_user(username, email, password):
    """Register a new user"""
    users = load_users()
    
    # Check if user exists
    if email in users or username in users:
        return False, "User already exists"
    
    # Create new user
    users[email] = {
        'username': username,
        'email': email,
        'password_hash': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    return True, "Account created successfully"

def login_form():
    """Display modern login form"""
    
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "Login"
    
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #0B0E14 0%, #151A26 50%, #0B0E14 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .glass-card {
        background: rgba(21, 26, 38, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1rem;
        padding: 2rem;
        max-width: 400px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">Sports Betting AI Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered predictions & analytics</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True, 
                    type="primary" if st.session_state.auth_tab == "Login" else "secondary"):
            st.session_state.auth_tab = "Login"
            st.rerun()
    with col2:
        if st.button("Sign Up", use_container_width=True,
                    type="primary" if st.session_state.auth_tab == "Signup" else "secondary"):
            st.session_state.auth_tab = "Signup"
            st.rerun()
    
    with st.form("auth_form"):
        if st.session_state.auth_tab == "Signup":
            username = st.text_input("Username", placeholder="Choose a username")
        
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submit = st.form_submit_button(
            "Sign In" if st.session_state.auth_tab == "Login" else "Create Account",
            use_container_width=True
        )
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            elif st.session_state.auth_tab == "Signup":
                if len(password) < 5:
                    st.error("Password must be at least 5 characters")
                else:
                    st.success("✅ Account created! Please sign in.")
                    st.session_state.auth_tab = "Login"
                    st.rerun()
            else:
                session = create_session(email.split('@')[0], is_admin=False)
                st.success(f"✅ Welcome back!")
                st.rerun()
    
    st.stop()

# Get session for sidebar
session = st.session_state.get('auth_session')

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, #00D2FF 0%, #00E701 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
        ">
            <span style="font-size: 24px;">🎯</span>
        </div>
        <h3 style="margin: 0; color: white; font-size: 1rem;">Sports Betting AI</h3>
        <p style="margin: 0; color: #8A8F98; font-size: 0.75rem;">Pro</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    
    pages = {
        "dashboard": "🏠 Dashboard",
        "predictions": "📊 Predictions", 
        "bet_tracker": "💰 Bet Tracker",
        "live_odds": "📈 Live Odds",
        "player_props": "👤 Player Props",
        "parlay_builder": "🔗 Parlay Builder"
    }
    
    for page_id, page_label in pages.items():
        if st.button(page_label, use_container_width=True, key=f"nav_{page_id}",
                    type="primary" if st.session_state.current_page == page_id else "secondary"):
            st.session_state.current_page = page_id
            st.rerun()
    
    st.markdown("---")
    
    # User info
    if session:
        st.markdown(f"**👤 {session['username']}**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

# Main content
page = st.session_state.current_page

if page == "dashboard":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your betting dashboard overview</p>', unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem; font-weight: 700; color: #00D2FF;">+12.5%</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">ROI This Month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem; font-weight: 700; color: #00E701;">68%</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem; font-weight: 700; color: #8B5CF6;">24</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Active Bets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem; font-weight: 700; color: #F97316;">$1,250</div>
            <div style="color: #8A8F98; font-size: 0.875rem;">Total Profit</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Profit Trend")
        dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        profits = [120, 85, -45, 200, 150, -30, 180]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=profits,
            mode='lines+markers',
            line=dict(color='#00D2FF', width=3),
            marker=dict(size=8, color='#00D2FF'),
            fill='tozeroy',
            fillcolor='rgba(0, 210, 255, 0.1)'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True),
            margin=dict(l=40, r=40, t=40, b=40),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Win/Loss Distribution")
        labels = ['Wins', 'Losses', 'Pushes']
        values = [45, 20, 5]
        colors = ['#00E701', '#FF4D4D', '#00D2FF']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color='#0B0E14', width=2)),
            textinfo='percent',
            textfont=dict(color='white', size=12)
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5, font=dict(color='white')),
            margin=dict(l=40, r=40, t=40, b=60),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "predictions":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Predictions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered game predictions and analysis</p>', unsafe_allow_html=True)
    
    sport = st.selectbox("Select Sport", ["NBA", "NFL", "MLB", "NHL"], key="pred_sport")
    
    st.info("🔄 Loading predictions...")
    
    for i in range(3):
        st.markdown(f"""
        <div class="game-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: white;">Team {i*2+1}</div>
                    <div style="color: #8A8F98; font-size: 0.8rem;">Home</div>
                </div>
                <div style="color: #00D2FF; font-weight: 700;">VS</div>
                <div style="text-align: right;">
                    <div style="font-weight: 600; font-size: 1.1rem; color: white;">Team {i*2+2}</div>
                    <div style="color: #8A8F98; font-size: 0.8rem;">Away</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "bet_tracker":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Bet Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Track your bets and analyze performance</p>', unsafe_allow_html=True)
    
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
    
    with st.expander("➕ Add New Bet"):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
            st.text_input("Your Pick")
        with col2:
            st.number_input("Odds", value=-110)
            st.number_input("Stake ($)", value=10.0)
        st.button("Add Bet", use_container_width=True)

elif page == "live_odds":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Live Odds</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time odds from multiple bookmakers</p>', unsafe_allow_html=True)
    
    st.info("📊 Live odds data will appear here")
    
    sample_data = {
        'Game': ['Lakers vs Warriors', 'Celtics vs Heat', 'Nets vs Bucks'],
        'Home ML': ['-150', '-200', '+120'],
        'Away ML': ['+130', '+170', '-140'],
        'Spread': ['LAL -3.5', 'BOS -5.5', 'BKN +3.5'],
        'Total': ['225.5', '218.5', '230.5']
    }
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True, hide_index=True)

elif page == "player_props":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Player Props</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Player-specific betting markets</p>', unsafe_allow_html=True)
    
    st.info("👤 Player prop data will appear here")

elif page == "parlay_builder":
    st.markdown('<h1 class="main-header" style="font-size: 2.5rem;">Parlay Builder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Build and analyze multi-leg parlays</p>', unsafe_allow_html=True)
    
    st.info("🔗 Parlay builder will appear here")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #5A6070; font-size: 0.75rem; padding: 1rem;">
    <b>18+ Only</b> • Please Gamble Responsibly
</div>
""", unsafe_allow_html=True)