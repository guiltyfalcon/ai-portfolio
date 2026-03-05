# BetBrain AI - Telegram Bot Automation

## Overview
Automated Telegram bot for the BetBrain AI channel (@betbrainaiwinner).

## Features

| Feature | Script | Schedule |
|---------|--------|----------|
| **Morning Picks** | `ai_picks_generator.py` | 9:00 AM ET daily |
| **Odds Updates** | `telegram_alerts.py` | Every 30 min (9 AM - 11 PM) |
| **Welcome Messages** | `welcome_new_members.py` | Hourly |
| **Value Alerts** | `telegram_alerts.py` | When 60%+ hit prob found |

## Installation

### 1. Install Cron Jobs

```bash
crontab /Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/bot/bot.cron
```

### 2. Verify Installation

```bash
crontab -l
```

You should see:
- Morning picks at 9 AM
- 30-min updates during game hours
- Evening recap at 6 PM
- Welcome check hourly

### 3. Test Scripts Manually

```bash
cd /Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/bot
source .env
export TELEGRAM_BOT_TOKEN
export TELEGRAM_CHAT_ID

# Test picks generator
python3 ai_picks_generator.py

# Test alerts
python3 telegram_alerts.py

# Test welcome
python3 welcome_new_members.py
```

## Configuration

### Environment Variables (.env)

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=@betbrainaiwinner
```

**⚠️ NEVER commit .env to Git!**

### Bot Requirements

1. Bot must be added to channel as **admin**
2. Bot needs permission to **post messages**
3. Channel must be **public** or bot must be admin for private channels

## File Structure

```
bot/
├── .env                    # Environment variables (gitignored)
├── .env.example            # Example env file
├── ai_picks_generator.py   # Morning picks thread
├── telegram_alerts.py      # Value bet alerts
├── welcome_new_members.py  # Welcome new channel members
├── bot.cron                # Cron job definitions
└── TELEGRAM_SETUP.md       # Setup instructions
```

## Message Types

### 1. Morning Picks (9 AM)
- Today's NBA slate analysis
- 5 AI-powered picks with confidence %
- Reasoning for each pick

### 2. Value Alerts (30-min)
- High-confidence props (60%+ hit prob)
- Line movement notifications
- +EV opportunities

### 3. Welcome Message (Hourly)
- Posted to channel for new joiners
- Explains what the channel offers
- Links to waitlist & Twitter

## Monitoring

Check logs:
```bash
tail -f /tmp/betbrain-morning.log
tail -f /tmp/betbrain-updates.log
tail -f /tmp/betbrain-evening.log
tail -f /tmp/betbrain-welcome.log
```

## Troubleshooting

### Bot not posting?
1. Check if bot is admin in channel
2. Verify TELEGRAM_BOT_TOKEN is correct
3. Check cron logs: `grep CRON /var/log/system.log`

### Welcome not sending?
- Telegram doesn't allow DMing channel members directly
- Welcome is posted to channel instead (visible to all)

### Alerts not triggering?
- Check if cache file exists and is fresh
- Adjust HIT_THRESHOLD in telegram_alerts.py (default: 60%)

## Future Enhancements

- [ ] Connect to live odds API for real-time alerts
- [ ] Add user commands (/picks, /odds, /help)
- [ ] Integrate email capture from landing page
- [ ] Add betting record tracking
- [ ] Multi-sport support (NFL, MLB, NHL)
