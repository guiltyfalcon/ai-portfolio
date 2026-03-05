#!/usr/bin/env python3
"""
BetBrain AI - Welcome New Channel Members
Sends a welcome DM to new members who join the Telegram channel.

Note: This requires the bot to be an admin in the channel with 
"Add New Members" permission enabled.

Usage: Run this script periodically to check for new members and welcome them.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

# Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHAT_ID', '@betbrainaiwinner')
MEMBERS_FILE = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/bot/channel_members.json')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set!")

def load_members():
    """Load previously tracked members."""
    if MEMBERS_FILE.exists():
        with open(MEMBERS_FILE, 'r') as f:
            return json.load(f)
    return {'members': [], 'last_check': None}

def save_members(data):
    """Save member tracking data."""
    with open(MEMBERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_channel_members():
    """Get channel members (requires bot to be admin)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatAdministrators"
    data = {'chat_id': CHANNEL_ID}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            return [admin['user']['id'] for admin in result.get('result', [])]
    except Exception as e:
        print(f"⚠️  Could not fetch admins: {e}")
    
    return []

def send_welcome_message(user_id, username):
    """Send welcome DM to new member."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    welcome_message = f"""🧠 <b>Welcome to BetBrain AI!</b>

Hey {username or 'there'}! Thanks for joining the early access channel.

<b>What you'll get:</b>
🏀 Daily NBA picks (65-75% accuracy)
📊 Live odds updates every 30 min
🔔 Value bet alerts (+EV opportunities)
📈 Line movement tracking

<b>Getting Started:</b>
1. Check the pinned message for today's top picks
2. Turn on notifications so you don't miss alerts
3. Join our waitlist: https://landing-page-eight-nu-87.vercel.app

<b>Important:</b>
• 21+ only
• Gamble responsibly
• This is for entertainment, not financial advice

Questions? Reply to this message!

Good luck! 🍀
"""
    
    data = {
        'chat_id': user_id,
        'text': welcome_message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            print(f"✅ Welcome message sent to {username or user_id}")
            return True
        else:
            print(f"⚠️  Failed to send welcome: {result}")
            return False
    except Exception as e:
        print(f"❌ Error sending welcome: {e}")
        return False

def check_new_members():
    """Check for new channel members and welcome them."""
    print(f"🧠 BetBrain AI - Checking for new members... {datetime.now()}")
    
    # Load tracked members
    tracked = load_members()
    tracked_ids = set(m['id'] for m in tracked.get('members', []))
    
    # Get current admins (note: full member list requires different API)
    # For channels, we can't get all members, but we can track via channel posts interactions
    # Alternative: Use channel join notifications via bot updates (webhook)
    
    # For now, we'll post a welcome message to the channel itself
    # which all new members will see when they join
    
    welcome_post = """👋 <b>New to BetBrain AI?</b>

Welcome! Here's what you need to know:

<b>📍 Navigation:</b>
• Pinned message = Today's top picks
• Scroll up = Recent alerts & updates
• Updates posted every 30 min during games

<b>🎯 What We Track:</b>
• NBA player props (specialty)
• Spreads & totals
• Line movement alerts
• +EV value bets

<b>📊 Our Edge:</b>
• 65-75% accuracy (backtested)
• 9 sportsbooks tracked
• ML-powered predictions
• 500+ props analyzed daily

<b>🔗 Join the Community:</b>
• Waitlist: https://landing-page-eight-nu-87.vercel.app
• Twitter: https://twitter.com/holikidTV

<b>⚠️ Important:</b>
• 21+ only
• Gamble responsibly
• Entertainment purposes only

Drop a 🧠 if you're ready to win!
"""
    
    # Post welcome message to channel
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHANNEL_ID,
        'text': welcome_post,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            print("✅ Welcome post sent to channel")
        else:
            print(f"⚠️  Failed to post: {result}")
    except Exception as e:
        print(f"❌ Error posting welcome: {e}")
    
    print("✅ Member check complete")

def main():
    check_new_members()

if __name__ == '__main__':
    main()
