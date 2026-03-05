# Telegram Bot Setup for BetBrain AI Alerts

## Quick Setup (5 minutes)

### 1. Create a New Bot

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Follow the prompts:
   - **Name:** `BetBrain AI Alerts`
   - **Username:** `BetBrainAIBot` (must end in "Bot")
4. BotFather will give you a **token** like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Get Your Chat ID

1. Search for **@userinfobot** in Telegram
2. Send it any message
3. It will reply with your **Id:** (this is your chat ID)

Or use your existing ID: `6471395025`

### 3. Start a Chat with Your Bot

1. Search for your new bot (`@BetBrainAIBot`)
2. Send `/start` to activate it

### 4. Update the Script

Edit `telegram_alerts.py`:

```python
TELEGRAM_BOT_TOKEN = 'YOUR_NEW_TOKEN_HERE'
TELEGRAM_CHAT_ID = '6471395025'  # Your Telegram ID
```

Or set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="6471395025"
```

### 5. Test It

```bash
python3 telegram_alerts.py
```

You should get a message in Telegram!

---

## Cron Schedule (Optional)

Add to crontab for automated alerts during game days:

```bash
# BetBrain AI alerts - every 30 mins during NBA games (4 PM - 11 PM ET)
*/30 16-23 * * * cd /Users/djryan/git/guiltyfalcon/ai-portfolio && python3 sports-betting-ai/bot/telegram_alerts.py
```

---

## Troubleshooting

**401 Unauthorized:**
- Token is wrong or revoked
- Create a new bot with @BotFather

**No message received:**
- Make sure you sent `/start` to your bot
- Check that chat ID is correct
- Bot can't message you first - you must initiate

**Permission errors:**
- Run: `chmod +x telegram_alerts.py`
