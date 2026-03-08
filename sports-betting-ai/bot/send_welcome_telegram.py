#!/usr/bin/env python3
import requests

TELEGRAM_BOT_TOKEN = '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88'
CHANNEL = '@betbrainaiwinner'

message = """🎉 NEW MEMBER ALERT!

Welcome to BetBrain AI! 🧠

You just signed up for our free beta. Here's what you're getting:

✅ Daily NBA picks (data-driven)
✅ Player props with 55%+ hit probability
✅ Line movement alerts (sharp money)
✅ Transparent results (win or learn)

📬 What to Expect:
• 9 AM ET: Daily picks thread
• 2 PM ET: Engagement + insights
• 6 PM ET: Results + recap
• Every 30 min: Value bet alerts

🔥 You're one of the first 100 — free access forever!

📲 Turn on notifications so you never miss an alert.

Let's win together! 🍡

— Mochi

NFA - Bet responsibly. 18+ only.
"""

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
data = {'chat_id': CHANNEL, 'text': message}
response = requests.post(url, json=data, timeout=10)
print(response.json())
