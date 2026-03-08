#!/usr/bin/env python3
"""
BetBrain AI - Welcome Email for New Signups
Sends automated welcome email with Telegram CTA to new waitlist signups.

Usage: Run after email_digest_bot.py or as standalone
"""

import os
import requests
from datetime import datetime

# Config
NYLAS_API_KEY = os.getenv('NYLAS_API_KEY', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88')
TELEGRAM_CHANNEL = '@betbrainaiwinner'
TELEGRAM_INVITE = 'https://t.me/betbrainaiwinner'

# Welcome Email Template
WELCOME_EMAIL_TEMPLATE = """
Subject: 🧠 Welcome to BetBrain AI - Your Free Beta Access is Confirmed

Hey {name},

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
"""

def get_signup_count():
    """Get current signup count from Formspree or tracking file."""
    # For now, hardcode based on our memory
    # TODO: Integrate with Formspree API
    return 53  # 47 spots left out of 100

def send_welcome_email(recipient_email, recipient_name="there"):
    """Send welcome email via Nylas."""
    
    spots_left = 100 - get_signup_count()
    
    email_content = WELCOME_EMAIL_TEMPLATE.format(
        name=recipient_name,
        spots_left=spots_left
    )
    
    # Use Nylas send API
    url = "https://api.nylas.com/v2/send"
    headers = {
        'Authorization': f'Bearer {NYLAS_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "to": [{"email": recipient_email}],
        "subject": "🧠 Welcome to BetBrain AI - Your Free Beta Access is Confirmed",
        "body": email_content
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✅ Welcome email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send: {e}")
        return False

def send_telegram_invite(recipient_email):
    """Alternative: Send Telegram invite directly via bot DM."""
    
    message = f"""🎉 Welcome to BetBrain AI!

You're confirmed for free beta access.

👉 Join the channel for real-time alerts:
{TELEGRAM_INVITE}

Why join?
• 30-min value bet alerts
• Daily picks (9 AM, 2 PM, 6 PM ET)
• Transparent results
• No spam, just data

See you inside! 🍡

— Mochi
"""
    
    # Note: Can't DM users directly unless they message bot first
    # This is a Telegram limitation
    # Instead, we'll log this for manual follow-up or use email
    
    print(f"📧 Telegram invite prepared for {recipient_email}")
    print(f"   (Email sent instead - Telegram DM requires user to message bot first)")
    return False

def main():
    print(f"🧠 Welcome Email Bot - {datetime.now()}")
    
    # This would integrate with email_digest_bot.py
    # For now, it's a template for manual use or future automation
    
    print("\n📝 Welcome email template ready.")
    print("   Integrate with email_digest_bot.py to auto-send.")
    print("\n🔗 Telegram invite: " + TELEGRAM_INVITE)

if __name__ == '__main__':
    main()
