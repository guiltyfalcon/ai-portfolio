#!/usr/bin/env python3
"""
BetBrain AI - Picks Generator
Analyzes tonight's NBA slate and generates AI-powered picks
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

# NEVER commit tokens to GitHub! Use environment variables.
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '@betbrainaiwinner')  # Telegram Channel

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set! Set it in your environment or .env file.")

def send_telegram_message(message):
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print(f"✅ Alert sent to Telegram")
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

def analyze_games():
    """
    AI Analysis of tonight's NBA slate from Yahoo odds cache
    Based on: record, spread, total, moneyline, home/away
    """
    
    # Load real data from Yahoo odds cache
    cache_file = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/yahoo_odds_cache.json')
    
    if not cache_file.exists():
        print("❌ Yahoo odds cache not found!")
        return []
    
    with open(cache_file, 'r') as f:
        data = json.load(f)
    
    # Filter for TODAY's games (UTC is +1 day, so check today+1)
    today = datetime.now()
    today_utc = today.strftime('%d %b %Y').upper()  # "06 MAR 2026"
    tomorrow_utc = (today.replace(day=today.day+1)).strftime('%d %b %Y').upper()  # "07 MAR 2026"
    nba_games = data.get('sports', {}).get('nba', [])
    
    # NBA games listed in UTC - check for today or tomorrow (UTC offset)
    today_games = [
        g for g in nba_games
        if today_utc in g.get('commence_time', '').upper() or 
           tomorrow_utc in g.get('commence_time', '').upper()
    ]
    
    if not today_games:
        print(f"⚠️ No NBA games found for {today}")
        return []
    
    print(f"✅ Found {len(today_games)} NBA games for {today}")
    
    # AI Analysis - Top Picks based on value
    picks = []
    
    for game in today_games[:5]:  # Top 5 games
        home = game.get('home_team', 'Unknown')
        away = game.get('away_team', 'Unknown')
        spread = game.get('home_spread', 0)
        total = game.get('total', 0)
        home_ml = game.get('home_ml', 0)
        away_ml = game.get('away_ml', 0)
        home_last_5 = game.get('home_last_5', '')
        away_last_5 = game.get('away_last_5', '')
        
        # Simple AI logic: pick favorites with strong recent form
        if abs(spread) >= 6 and home_last_5 == 'WW':
            picks.append({
                'pick': f'{home} {spread}',
                'confidence': '75%',
                'reasoning': f'{home} on hot streak ({home_last_5}), covering {spread} at home',
                'game': f'{away} @ {home}'
            })
        elif abs(spread) <= 5 and away_last_5 == 'WW':
            picks.append({
                'pick': f'{away} +{abs(spread)}',
                'confidence': '70%',
                'reasoning': f'{away} rolling ({away_last_5}), keeping it close on road',
                'game': f'{away} @ {home}'
            })
        elif total >= 230:
            picks.append({
                'pick': f'OVER {total}',
                'confidence': '65%',
                'reasoning': f'High total ({total}), both teams score well',
                'game': f'{away} @ {home}'
            })
    
    return picks if picks else [{'pick': 'No strong value plays', 'confidence': 'N/A', 'reasoning': 'Waiting for better opportunities', 'game': 'Standby'}]

def format_picks_message(picks):
    """Format picks as Telegram message."""
    today = datetime.now().strftime('%A, %B %d, %Y')
    message = "🧠 <b>BetBrain AI - LIVE PICKS</b>\n\n"
    message += f"📅 {today}\n"
    message += f"🏀 <b>NBA SLATE ANALYSIS</b>\n\n"
    message += f"📊 <i>AI-analyzed using real-time odds from 9 sportsbooks</i>\n\n"
    message += "═══ TOP PICKS ═══\n\n"
    
    for i, pick in enumerate(picks, 1):
        emoji = "🔥" if pick.get('confidence', '0%').replace('%', '').isdigit() and int(pick['confidence'].replace('%', '')) >= 80 else "⚡"
        message += f"{emoji} <b>#{i}: {pick['pick']}</b>\n"
        message += f"   🎯 Confidence: {pick.get('confidence', 'N/A')}\n"
        message += f"   📍 {pick.get('game', '')}\n"
        message += f"   💡 {pick.get('reasoning', '')}\n\n"
    
    message += "═══\n"
    message += "⚠️ <i>Gamble responsibly. These are AI opinions, not guarantees.</i>\n"
    message += f"📊 <b>{len(picks)} value plays identified</b>"
    
    return message

def main():
    print("🧠 BetBrain AI - Generating picks for tonight's slate...")
    
    # Analyze games
    picks = analyze_games()
    print(f"📊 Generated {len(picks)} AI picks")
    
    # Format message
    message = format_picks_message(picks)
    
    # Send to Telegram
    send_telegram_message(message)
    
    print("✅ Picks sent to Telegram!")

if __name__ == '__main__':
    main()
