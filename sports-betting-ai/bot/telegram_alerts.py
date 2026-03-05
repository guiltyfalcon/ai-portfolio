#!/usr/bin/env python3
"""
BetBrain AI - Telegram Alert Bot
Monitors player props cache and sends high-value bet alerts to Telegram.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

# Config - BetBrain AI Alerts Bot Token
# NEVER commit tokens to GitHub! Use environment variables.
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '6471395025')  # User's Telegram ID

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set! Set it in your environment or .env file.")
CACHE_FILE = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/player_props_cache.json')
HIT_THRESHOLD = 60.0  # Only alert on props with 60%+ hit probability

def send_telegram_message(message):
    """Send message to Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  TELEGRAM_BOT_TOKEN not set. Printing message instead:")
        print(message)
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print(f"✅ Alert sent to Telegram: {message[:50]}...")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

def load_cache():
    """Load player props cache."""
    if not CACHE_FILE.exists():
        print(f"❌ Cache file not found: {CACHE_FILE}")
        return None
    
    with open(CACHE_FILE, 'r') as f:
        return json.load(f)

def find_value_bets(cache_data):
    """Find high-value bets from cache."""
    value_bets = []
    
    # Check if data is fresh (within last 2 hours)
    scrape_time = cache_data.get('scrape_time', '')
    if scrape_time:
        try:
            from datetime import datetime, timedelta
            scrape_dt = datetime.fromisoformat(scrape_time.replace('Z', '+00:00'))
            if datetime.now(scrape_dt.tzinfo) - scrape_dt > timedelta(hours=2):
                print("⚠️  WARNING: Data is stale (>2 hours old)")
                return []  # Don't send alerts on old data
        except:
            pass
    
    sports = cache_data.get('sports', {})
    nba_players = sports.get('nba', [])
    
    for game in nba_players:
        game_info = f"{game.get('away_team', 'Unknown')} @ {game.get('home_team', 'Unknown')}"
        
        for player in game.get('players', []):
            player_name = player.get('player', 'Unknown')
            team = player.get('team_abbr', '')
            
            for prop in player.get('props', []):
                hit_prob = prop.get('hit_probability', 0)
                weighted_prob = prop.get('weighted_probability', hit_prob)
                recommendation = prop.get('recommendation', 'EVEN')
                prop_type = prop.get('type', 'unknown').upper()
                line = prop.get('line', 0)
                odds_over = prop.get('odds_over', '-110')
                
                # Only alert on high-confidence picks
                if weighted_prob >= HIT_THRESHOLD or recommendation == 'LEAN':
                    value_bets.append({
                        'player': f"{player_name} ({team})",
                        'game': game_info,
                        'prop': f"{prop_type} {line}",
                        'hit_prob': weighted_prob,
                        'recommendation': recommendation,
                        'odds': odds_over
                    })
    
    return value_bets

def format_alert(value_bets):
    """Format value bets as Telegram message."""
    if not value_bets:
        return None
    
    message = "🧠 <b>BetBrain AI - Value Alerts</b>\n\n"
    message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    message += f"🔍 Found {len(value_bets)} high-value bets\n\n"
    
    for i, bet in enumerate(value_bets[:5], 1):  # Top 5 only
        emoji = "🔥" if bet['hit_prob'] >= 65 else "⚡"
        message += f"{emoji} <b>#{i}: {bet['player']}</b>\n"
        message += f"   Prop: {bet['prop']}\n"
        message += f"   Hit Rate: {bet['hit_prob']:.1f}%\n"
        message += f"   Odds: {bet['odds']}\n"
        message += f"   Game: {bet['game']}\n\n"
    
    if len(value_bets) > 5:
        message += f"...and {len(value_bets) - 5} more\n"
    
    message += "\n💡 <i>Always bet responsibly. This is for entertainment only.</i>"
    
    return message

def main():
    print(f"🧠 BetBrain AI Alert Bot - {datetime.now()}")
    print(f"   Cache: {CACHE_FILE}")
    print(f"   Threshold: {HIT_THRESHOLD}%\n")
    
    # Load cache
    cache_data = load_cache()
    if not cache_data:
        return
    
    # Find value bets
    value_bets = find_value_bets(cache_data)
    print(f"📊 Found {len(value_bets)} value bets")
    
    if not value_bets:
        print("✅ No high-value bets found. Standing by.")
        return
    
    # Format and send alert
    message = format_alert(value_bets)
    if message:
        send_telegram_message(message)
    
    print("✅ Alert check complete")

if __name__ == '__main__':
    main()
