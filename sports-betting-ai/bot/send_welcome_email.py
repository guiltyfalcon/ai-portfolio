#!/usr/bin/env python3
"""
BetBrain AI - Send Welcome Email to New Signup
Quick script to send welcome email with Telegram CTA.

Usage: python3 send_welcome_email.py <email_address>
"""

import sys
import os
import requests
from datetime import datetime

# Config
NYLAS_API_KEY = os.getenv('NYLAS_API_KEY', '')
TELEGRAM_INVITE = 'https://t.me/betbrainaiwinner'
LANDING_PAGE = 'https://landing-page-eight-nu-87.vercel.app'

def send_welcome_email(recipient_email, recipient_name="there"):
    """Send welcome email via Nylas."""
    
    spots_left = 47  # Based on our landing page urgency
    
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

👉 {TELEGRAM_INVITE}

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
• That's a +19.5 smash

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
Unsubscribe: {LANDING_PAGE}
"""
    
    # Use Nylas send API
    url = "https://api.nylas.com/v2/send"
    headers = {
        'Authorization': f'Bearer {NYLAS_API_KEY}',
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
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print(f"🧠 BetBrain AI - Welcome Email Sender")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python3 send_welcome_email.py <email_address> [name]")
        print()
        print("Example:")
        print("  python3 send_welcome_email.py user@example.com")
        print("  python3 send_welcome_email.py user@example.com John")
        sys.exit(1)
    
    email = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "there"
    
    success = send_welcome_email(email, name)
    
    if success:
        print("\n🎉 Welcome email sent!")
        print(f"   Telegram invite: {TELEGRAM_INVITE}")
    else:
        print("\n❌ Failed to send. Check Nylas API key and try again.")
        sys.exit(1)

if __name__ == '__main__':
    main()
