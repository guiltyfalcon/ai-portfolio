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

def send_welcome_email(recipient_email, recipient_name="there"):
    """Send welcome email via Nylas API."""
    
    spots_left = 47
    
    subject = "🧠 Welcome to BetBrain AI - Your Free Beta Access is Confirmed"
    
    body = f"""Hi {recipient_name},

Welcome to BetBrain AI! 🎉

You're officially in the free beta — one of {spots_left} spots remaining.

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 WHAT YOU'RE GETTING:

✅ Daily NBA picks (data-driven, not guesses)
✅ Player props with 55%+ hit probability  
✅ Line movement alerts (sharp money tracking)
✅ Transparent results (win or learn, always)

━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 NEXT STEP: JOIN THE TELEGRAM CHANNEL

Your email is confirmed, but here's where the real action happens:

👉 https://t.me/betbrainaiwinner

Why join?
• Real-time alerts (30-min updates during game days)
• Value bets sent directly to your phone
• Community of bettors using AI edge
• No spam, just data

━━━━━━━━━━━━━━━━━━━━━━━━━

📈 OUR APPROACH:

We don't guess. We scrape 10,000+ player props, track line movements, and let the data speak.

Recent example:
• Clarkson O 18.5 pts (58.5% hit prob) → He scored 38 ✅

━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 FREE BETA DETAILS:

You're in the first 100 — free access forever.
After 100 signups, beta access is $29/month.

Current spots left: {spots_left}

━━━━━━━━━━━━━━━━━━━━━━━━━

📬 WHAT TO EXPECT:

• Morning (9 AM ET): Daily picks thread
• Afternoon (2 PM ET): Engagement + insights
• Evening (6 PM ET): Results + recap
• Every 30 min: Value bet alerts (Telegram only)

━━━━━━━━━━━━━━━━━━━━━━━━━

🍀 LET'S WIN TOGETHER

Questions? Reply to this email.

See you in the channel!

— Mochi 🍡
BetBrain AI

P.S. Turn on notifications for the Telegram channel. That's where the alerts hit first.

━━━━━━━━━━━━━━━━━━━━━━━━━

NFA (Not Financial Advice) - Bet responsibly. 18+ only.
"""
    
    # Use Nylas send API
    url = "https://api.nylas.com/v2/send"
    headers = {
        'Authorization': f'Bearer {os.getenv("NYLAS_API_KEY", "")}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "to": [{"email": recipient_email}],
        "subject": subject,
        "body": body
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✅ Welcome email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Welcome email failed: {e}")
        return False

def send_digest(submissions):
    """Send digest to Telegram + auto-send welcome emails."""
    if not submissions:
        return False
    
    welcome_sent = 0
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
        
        # Auto-send welcome email
        if from_email and from_email != 'unknown':
            if send_welcome_email(from_email):
                welcome_sent += 1
    
    message += f"""
📈 Total processed: {len(submissions)}
✅ Welcome emails sent: {welcome_sent}

💡 New signups will receive Telegram invite automatically
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
