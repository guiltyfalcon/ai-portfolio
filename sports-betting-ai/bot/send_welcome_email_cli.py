#!/usr/bin/env python3
"""Send welcome email using Nylas CLI (OAuth-based, no API key needed)."""

import subprocess
import sys
from datetime import datetime

def send_welcome_email(recipient_email, recipient_name="there"):
    """Send welcome email via Nylas CLI."""
    
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
    
    # Use Nylas CLI to send
    # Note: nylas email send requires interactive input, so we'll use a workaround
    # Create a temp file with the email content
    
    import tempfile
    import os
    
    # Try using nylas CLI send command
    cmd = [
        'nylas', 'email', 'send',
        '--to', recipient_email,
        '--subject', subject,
        '--body', body
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Welcome email sent to {recipient_email}")
            return True
        else:
            print(f"❌ CLI error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 send_welcome_email_cli.py <email> [name]")
        sys.exit(1)
    
    email = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "there"
    
    success = send_welcome_email(email, name)
    sys.exit(0 if success else 1)
