import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
import pandas as pd

# Admin credentials (in production, use proper auth)
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@betai.pro"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# Session management
SESSION_DURATION = 24 * 60 * 60  # 24 hours in seconds

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
    if 'auth_session' not in st.session_state:
        return None
    
    session = st.session_state['auth_session']
    
    # Check if session expired
    if time.time() > session.get('expires_at', 0):
        del st.session_state['auth_session']
        return None
    
    return session

def logout():
    """Clear user session"""
    if 'auth_session' in st.session_state:
        del st.session_state['auth_session']
    st.rerun()

def is_admin():
    """Check if current user is admin"""
    session = check_session()
    return session and session.get('is_admin', False)

# User storage (in production, use a database)
USERS_FILE = ".users.json"

def load_users():
    """Load users from file"""
    import json
    import os
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file"""
    import json
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
    """Display modern login form matching the React app design"""
    
    # Initialize tab state
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "Login"
    
    # Modern dark theme CSS matching the React app
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    .login-container {
        font-family: 'Inter', system-ui, sans-serif;
        background: linear-gradient(135deg, #0B0E14 0%, #151A26 50%, #0B0E14 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    /* Animated gradient orbs */
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(100px);
        animation: pulse 4s ease-in-out infinite;
    }
    
    .orb-1 {
        top: 25%;
        left: 25%;
        width: 400px;
        height: 400px;
        background: rgba(0, 210, 255, 0.1);
    }
    
    .orb-2 {
        bottom: 25%;
        right: 25%;
        width: 400px;
        height: 400px;
        background: rgba(0, 231, 1, 0.1);
        animation-delay: 1s;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.1); }
    }
    
    /* Glass card */
    .glass-card {
        background: rgba(21, 26, 38, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1rem;
        padding: 2rem;
        width: 100%;
        max-width: 400px;
        position: relative;
        z-index: 10;
    }
    
    /* Logo container */
    .logo-container {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
        border-radius: 1rem;
        background: linear-gradient(135deg, #00D2FF 0%, #00E701 100%);
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #00D2FF 0%, #3A7BD5 50%, #00D2FF 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Tab buttons */
    .tab-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        padding: 0.25rem;
        background: #0B0E14;
        border-radius: 0.75rem;
    }
    
    .tab-btn {
        flex: 1;
        padding: 0.625rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.3s;
        border: none;
        cursor: pointer;
    }
    
    .tab-btn.active {
        background: rgba(0, 210, 255, 0.1);
        color: #00D2FF;
    }
    
    .tab-btn:not(.active) {
        background: transparent;
        color: #8A8F98;
    }
    
    .tab-btn:not(.active):hover {
        color: white;
    }
    
    /* Input fields */
    .input-modern {
        width: 100%;
        padding: 0.875rem 1rem 0.875rem 3rem;
        background: #0B0E14;
        border: 1px solid #2A3142;
        border-radius: 0.75rem;
        color: white;
        font-size: 0.875rem;
        transition: all 0.3s;
    }
    
    .input-modern:focus {
        outline: none;
        border-color: #00D2FF;
        box-shadow: 0 0 0 3px rgba(0, 210, 255, 0.1);
    }
    
    .input-modern::placeholder {
        color: #5A6070;
    }
    
    /* Primary button */
    .btn-primary {
        padding: 0.875rem 1.5rem;
        background: linear-gradient(135deg, #00D2FF 0%, #00E701 100%);
        border: none;
        border-radius: 0.75rem;
        color: #0B0E14;
        font-weight: 600;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
    }
    
    .btn-primary::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .btn-primary:hover::after {
        left: 100%;
    }
    
    /* Footer text */
    .footer-text {
        text-align: center;
        color: #8A8F98;
        font-size: 0.75rem;
        margin-top: 2rem;
    }
    
    /* Error message */
    .error-message {
        padding: 0.75rem;
        background: rgba(255, 77, 77, 0.1);
        border: 1px solid rgba(255, 77, 77, 0.3);
        border-radius: 0.5rem;
        color: #FF4D4D;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    </style>
    <div class="login-container">
        <!-- Animated orbs -->
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        
        <!-- Glass card -->
        <div class="glass-card">
            <!-- Logo -->
            <div style="text-align: center; margin-bottom: 2rem;">
                <div class="logo-container">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #0B0E14;">
                        <circle cx="12" cy="12" r="10"/>
                        <circle cx="12" cy="12" r="6"/>
                        <circle cx="12" cy="12" r="2"/>
                    </svg>
                </div>
                <h1 class="gradient-text" style="font-size: 1.875rem; font-weight: 700; margin-bottom: 0.5rem;">Sports Betting AI Pro</h1>
                <p style="color: #8A8F98; font-size: 0.875rem;">AI-powered predictions & analytics</p>
            </div>
            
            <!-- Tabs -->
            <div class="tab-container">
                <button 
                    class="tab-btn {('active' if st.session_state.auth_tab == 'Login' else '')}"
                    onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Login'}}, '*')"
                >
                    Sign In
                </button>
                <button 
                    class="tab-btn {('active' if st.session_state.auth_tab == 'Signup' else '')}"
                    onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Signup'}}, '*')"
                >
                    Sign Up
                </button>
            </div>
            
            <!-- Form content will be rendered by Streamlit -->
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab selection
    tab_col1, tab_col2 = st.columns(2)
    with tab_col1:
        if st.button("Sign In", use_container_width=True, 
                    type="primary" if st.session_state.auth_tab == "Login" else "secondary"):
            st.session_state.auth_tab = "Login"
            st.rerun()
    with tab_col2:
        if st.button("Sign Up", use_container_width=True,
                    type="primary" if st.session_state.auth_tab == "Signup" else "secondary"):
            st.session_state.auth_tab = "Signup"
            st.rerun()
    
    # Form
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
                return False
            
            if st.session_state.auth_tab == "Signup":
                if not username:
                    st.error("Please enter a username")
                    return False
                
                if len(password) < 5:
                    st.error("Password must be at least 5 characters")
                    return False
                
                success, message = signup_user(username, email, password)
                if success:
                    st.success(f"✅ {message}! Please sign in.")
                    st.session_state.auth_tab = "Login"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
                    return False
            else:
                # Check admin credentials first
                is_admin_login = (email == ADMIN_EMAIL or email == ADMIN_USERNAME) and hash_password(password) == ADMIN_PASSWORD_HASH
                
                if is_admin_login:
                    session = create_session(ADMIN_USERNAME, is_admin=True)
                    st.success(f"✅ Welcome back, Admin!")
                    st.rerun()
                    return True
                
                # Check regular user credentials
                users = load_users()
                user_found = None
                for user_email, user_data in users.items():
                    if (email == user_email or email == user_data.get('username')) and user_data.get('password_hash') == hash_password(password):
                        user_found = user_data
                        break
                
                if user_found:
                    session = create_session(user_found['username'], is_admin=False)
                    st.success(f"✅ Welcome back, {user_found['username']}!")
                    st.rerun()
                    return True
                else:
                    st.error("Invalid email or password")
                    return False
    
    return False