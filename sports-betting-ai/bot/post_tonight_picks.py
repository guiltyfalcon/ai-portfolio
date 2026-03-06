#!/usr/bin/env python3
import requests

TELEGRAM_BOT_TOKEN = '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88'
TELEGRAM_CHAT_ID = '@betbrainaiwinner'

message = """🧠 <b>BetBrain AI - Tonight's Picks</b>
📅 Thursday, March 5th | 9 NBA Games

🔥 <b>TOP PLAYER PROPS</b>

<b>1. Lauri Markkanen</b> (UTA @ WAS)
📊 Points: Over 25.0 (-110)
💯 Last 5: 27.2 PPG
🏀 Wizards = 28th in FGA defense

<b>2. Jordan Clarkson</b> (UTA @ WAS)
📊 Points: Over 18.5 (-110)
💯 Last 5: 20.1 PPG
🏀 High usage vs weak defense

<b>3. Nikola Jokic</b> (DEN vs LAL)
📊 Points: Over 29.5 (-115)
🏀 Lakers = Bottom 10 vs Centers

<b>4. LeBron James</b> (LAL @ DEN)
📊 Assists: Over 7.5 (-120)
🏀 8+ assists in 4 of last 6

<b>5. Jimmy Butler</b> (MIA vs BKN)
📊 Points: Over 22.5 (-110)
🏀 Nets allow 115 PPG to SFs

🎯 <b>PARLAY OF THE NIGHT</b>
Markkanen Over 25 + Jokic Over 29.5
💰 +260 payout

⚠️ <b>Disclaimer:</b>
• 21+ only • Gamble responsibly
• AI predictions, not guarantees
• Bet what you can afford to lose

🔗 Join Free: t.me/betbrainaiwinner
"""

url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
data = {
    'chat_id': TELEGRAM_CHAT_ID,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(url, json=data, timeout=10)
print(response.json())
