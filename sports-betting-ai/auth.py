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

def login_form():
    """Display login form"""
    st.markdown("""
    <div style="text-align: center; padding: 40px;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">🎯 Sports Betting AI Pro</h1>
        <p style="color: #a0a0c0; font-size: 1.2rem;">Please log in to access the platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submit = st.form_submit_button("Log In", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return False
                
                # Check credentials (email or username)
                is_admin_login = (email == ADMIN_EMAIL or email == ADMIN_USERNAME) and hash_password(password) == ADMIN_PASSWORD_HASH
                
                if is_admin_login:
                    # Admin login
                    session = create_session(ADMIN_USERNAME, is_admin=True)
                    st.success(f"✅ Welcome back, Admin!")
                    st.rerun()
                    return True
                else:
                    # Regular user login (could add more users here)
                    st.error("Invalid email or password")
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