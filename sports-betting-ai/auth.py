"""
Authentication module for Sports Betting AI Pro
Simple username/password with admin privileges
"""

import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta

# Admin credentials
ADMIN_USERNAME = "Hitman24"
ADMIN_EMAIL = "dariusr26@gmail.com"
# Password hash for "Hitman24" (you can change this)
ADMIN_PASSWORD_HASH = hashlib.sha256("Hitman24".encode()).hexdigest()

# Session management
SESSION_DURATION_HOURS = 24

def hash_password(password):
    """Hash password for storage/comparison"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(username, is_admin=False):
    """Create a new session"""
    session_token = secrets.token_urlsafe(32)
    expiry = datetime.now() + timedelta(hours=SESSION_DURATION_HOURS)
    
    session_data = {
        "token": session_token,
        "username": username,
        "is_admin": is_admin,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry.isoformat()
    }
    
    # Store in session state
    st.session_state["auth_session"] = session_data
    return session_data

def check_session():
    """Check if current session is valid"""
    if "auth_session" not in st.session_state:
        return None
    
    session = st.session_state["auth_session"]
    expiry = datetime.fromisoformat(session["expires_at"])
    
    if datetime.now() > expiry:
        # Session expired
        del st.session_state["auth_session"]
        return None
    
    return session

def is_admin():
    """Check if current user is admin"""
    session = check_session()
    if session:
        return session.get("is_admin", False)
    return False

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
    """Display login form with signup option"""
    
    # Initialize tab state
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "Login"
    
    st.markdown("""
    <style>
    @keyframes breathe-glow {
        0%, 100% { 
            text-shadow: 0 0 20px rgba(0,210,255,0.4), 0 0 40px rgba(0,210,255,0.2);
            filter: brightness(1);
        }
        50% { 
            text-shadow: 0 0 40px rgba(0,210,255,0.8), 0 0 80px rgba(0,210,255,0.4);
            filter: brightness(1.2);
        }
    }
    .login-header {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 50%, #00d2ff 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 3s ease infinite, breathe-glow 2s ease-in-out infinite;
        margin-bottom: 10px;
    }
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    <div style="text-align: center; padding: 40px;">
        <div class="login-header">
            Sports Betting AI Pro
        </div>
        <p style="color: #a0a0c0; font-size: 1.2rem;">Please log in or sign up to access the platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Tabs for Login/Signup
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email or Username", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                submit = st.form_submit_button("Log In", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("Please enter both email and password")
                        return False
                    
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
        
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="Enter your email")
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                submit_signup = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_signup:
                    if not new_username or not new_email or not new_password:
                        st.error("Please fill in all fields")
                        return False
                    
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                        return False
                    
                    if len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                        return False
                    
                    success, message = signup_user(new_username, new_email, new_password)
                    if success:
                        st.success(f"✅ {message}! Please log in.")
                    else:
                        st.error(f"❌ {message}")
                        return False
    
    return False

def logout():
    """Log out current user"""
    if "auth_session" in st.session_state:
        del st.session_state["auth_session"]
    st.rerun()

def require_auth():
    """Decorator to require authentication"""
    session = check_session()
    if not session:
        login_form()
        st.stop()
    return session

def admin_only():
    """Decorator to require admin privileges"""
    if not is_admin():
        st.error("⛔ Admin access required")
        st.stop()
    return True