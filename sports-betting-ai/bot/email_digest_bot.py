#!/usr/bin/env python3
"""
BetBrain AI - Email Signup Digest Bot
Checks Formspree for new waitlist signups and posts hourly digest to Telegram.

Usage: Run hourly via cron
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88')
TELEGRAM_CHAT_ID = '@betbrainaiwinner'  # Channel
PERSONAL_CHAT_ID = '6471395025'  # Your personal chat for notifications

# Formspree API
FORMSPREE_FORM_ID = 'mnjgarek'
FORMSPREE_API_URL = f'https://api.formspree.io/v2/forms/{FORMSPREE_FORM_ID}/submissions'

# Tracking file
DIGEST_FILE = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/data/email_digest_state.json')

def load_state():
    """Load last check timestamp."""
    if DIGEST_FILE.exists():
        with open(DIGEST_FILE, 'r') as f:
            return json.load(f)
    return {'last_check': None, 'total_seen': 0}

def save_state(state):
    """Save state."""
    DIGEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DIGEST_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_new_submissions():
    """Fetch new submissions from Formspree."""
    state = load_state()
    
    # Formspree API requires authentication
    # For now, we'll check the local JSON file instead
    local_file = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/data/waitlist_emails.json')
    
    if not local_file.exists():
        return []
    
    with open(local_file, 'r') as f:
        data = json.load(f)
    
    emails = data.get('emails', [])
    total = data.get('total', 0)
    
    # Filter new ones since last check
    last_check = state.get('last_check')
    if last_check:
        new_emails = [
            e for e in emails 
            if e.get('timestamp', '') > last_check
        ]
    else:
        # First run - return last 5
        new_emails = emails[-5:] if len(emails) > 5 else emails
    
    # Update state
    state['last_check'] = datetime.now().isoformat()
    state['total_seen'] = total
    save_state(state)
    
    return new_emails

def send_digest(submissions):
    """Send digest to Telegram."""
    if not submissions:
        return False
    
    # Send to personal chat first
    message = f"""📧 <b>Email Signup Digest</b>

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 {len(submissions)} new signup(s) in last hour

"""
    
    for sub in submissions:
        email = sub.get('email', 'unknown')
        timestamp = sub.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%H:%M')
            except:
                time_str = ''
        else:
            time_str = ''
        
        message += f"• <code>{email}</code> {time_str}\n"
    
    message += f"""
📈 Total signups: {len(submissions)}
🔗 View all: https://formspree.io/f/{FORMSPREE_FORM_ID}

💡 Next: Auto-DM these users the Telegram invite
"""
    
    # Send to personal chat
    send_telegram_message(PERSONAL_CHAT_ID, message)
    
    # Also post to channel (optional - comment out if you only want personal)
    channel_message = f"""🎉 <b>{len(submissions)} New BetBrain Members!</b>

Welcome to everyone who joined this hour! 

Make sure to:
✅ Turn on notifications
✅ Check the pinned message for today's picks
✅ Invite your friends!

🧠 Let's win together!
"""
    send_telegram_message(TELEGRAM_CHAT_ID, channel_message)
    
    return True

def send_telegram_message(chat_id, message):
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print(f"✅ Sent to {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print(f"🧠 Email Digest Bot - {datetime.now()}")
    
    # Get new submissions
    submissions = get_new_submissions()
    print(f"📊 Found {len(submissions)} new submissions")
    
    if not submissions:
        print("✅ No new signups. Standing by.")
        return
    
    # Send digest
    send_digest(submissions)
    print("✅ Digest sent")

if __name__ == '__main__':
    main()
