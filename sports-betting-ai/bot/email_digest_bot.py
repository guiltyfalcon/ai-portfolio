#!/usr/bin/env python3
"""
BetBrain AI - Email Signup Digest Bot
Checks Nylas for new waitlist signups and posts hourly digest to Telegram.

Usage: Run hourly via cron
"""

import json
import os
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88')
TELEGRAM_CHAT_ID = '@betbrainaiwinner'  # Channel
PERSONAL_CHAT_ID = '6471395025'  # Your personal chat for notifications

# Tracking file
DIGEST_FILE = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/data/email_digest_state.json')

def load_state():
    """Load last check timestamp and processed message IDs."""
    if DIGEST_FILE.exists():
        with open(DIGEST_FILE, 'r') as f:
            return json.load(f)
    return {'last_check': None, 'processed_ids': [], 'total_seen': 0}

def save_state(state):
    """Save state."""
    DIGEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DIGEST_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_new_submissions():
    """Fetch new waitlist emails from Nylas."""
    state = load_state()
    processed_ids = set(state.get('processed_ids', []))
    
    # Use Nylas CLI to fetch unread emails
    try:
        result = subprocess.run(
            ['nylas', 'email', 'list', '--unread', '--limit', '100', '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Nylas error: {result.stderr}")
            return []
        
        # Parse Nylas output (JSON format)
        emails = json.loads(result.stdout) if result.stdout.strip() else []
        
        # Filter for waitlist-related emails (subject or sender)
        waitlist_keywords = ['waitlist', 'betbrain', 'signup', 'join']
        new_emails = [
            e for e in emails 
            if e.get('id') not in processed_ids
            and e.get('unread', False)
            and any(kw.lower() in e.get('subject', '').lower() for kw in waitlist_keywords)
        ]
        
        # Mark as read
        for email in new_emails:
            email_id = email.get('id')
            if email_id:
                subprocess.run(
                    ['nylas', 'email', 'mark-read', email_id],
                    capture_output=True,
                    timeout=10
                )
                processed_ids.add(email_id)
        
        # Update state
        state['last_check'] = datetime.now().isoformat()
        state['processed_ids'] = list(processed_ids)[-1000:]  # Keep last 1000 IDs
        state['total_seen'] = len(processed_ids)
        save_state(state)
        
        return new_emails
        
    except subprocess.TimeoutExpired:
        print("❌ Nylas timeout")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

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
        # Extract from Nylas email format
        from_email = sub.get('from', [{}])[0].get('email', 'unknown')
        subject = sub.get('subject', '')
        date = sub.get('date', '')
        
        if date:
            try:
                dt = datetime.fromtimestamp(int(date))
                time_str = dt.strftime('%H:%M')
            except:
                time_str = ''
        else:
            time_str = ''
        
        message += f"• <code>{from_email}</code> {time_str}\n"
    
    message += f"""
📈 Total processed: {len(submissions)}

💡 Next: Auto-DM these users the Telegram invite
"""
    
    # Send to personal chat
    send_telegram_message(PERSONAL_CHAT_ID, message)
    
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
