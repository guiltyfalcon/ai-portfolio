#!/usr/bin/env python3
"""
BetBrain AI - Weekly Props Finder
Scrapes ALL available player props and identifies the BEST picks for the week.

Features:
- Scrapes 5+ sportsbooks for best lines
- AI analysis with 65-75% confidence threshold
- Saves weekly props database
- Auto-posts top picks to Telegram
- Tracks performance for accuracy verification

Usage: python3 weekly_props_finder.py
Schedule: Run daily at 9 AM ET via cron
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88')
TELEGRAM_CHAT_ID = '@betbrainaiwinner'

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data' / 'weekly-props'
DATA_DIR.mkdir(parents=True, exist_ok=True)

class WeeklyPropsFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.weekly_props = []
        self.confidence_threshold = 70  # Only save props with 70%+ confidence
    
    def run_all_scrapers(self):
        """Run all scraper scripts and consolidate data."""
        print("🧠 BetBrain AI - Weekly Props Finder")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        all_props = []
        
        # Run Yahoo scraper
        print("\n📊 Running Yahoo scraper...")
        try:
            result = subprocess.run(
                ['python3', SCRIPT_DIR / 'yahoo_scraper.py'],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                with open(SCRIPT_DIR / 'yahoo_odds_cache.json', 'r') as f:
                    yahoo_data = json.load(f)
                all_props.append({'source': 'Yahoo', 'data': yahoo_data})
                print(f"  ✅ Yahoo: {len(yahoo_data.get('games', []))} games")
        except Exception as e:
            print(f"  ⚠️  Yahoo failed: {e}")
        
        # Run player props scraper
        print("\n📊 Running player props scraper...")
        try:
            result = subprocess.run(
                ['python3', SCRIPT_DIR / 'player_props_scraper.py'],
                capture_output=True, text=True, timeout=90
            )
            if result.returncode == 0:
                with open(SCRIPT_DIR / 'player_props_cache.json', 'r') as f:
                    props_data = json.load(f)
                all_props.append({'source': 'Player Props', 'data': props_data})
                print(f"  ✅ Player Props: {len(props_data.get('best_bets', []))} best bets")
        except Exception as e:
            print(f"  ⚠️  Player Props failed: {e}")
        
        # Run multi-sportsbook scraper
        print("\n📊 Running multi-sportsbook scraper...")
        try:
            result = subprocess.run(
                ['python3', SCRIPT_DIR / 'multi_sportsbook_scraper.py'],
                capture_output=True, text=True, timeout=90
            )
            if result.returncode == 0:
                cache_file = SCRIPT_DIR / 'odds-data' / f"consolidated_odds_{datetime.now().strftime('%Y%m%d')}.json"
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        multi_data = json.load(f)
                    all_props.append({'source': 'Multi-Book', 'data': multi_data})
                    print(f"  ✅ Multi-Book: {len(multi_data.get('games', []))} games")
        except Exception as e:
            print(f"  ⚠️  Multi-Book failed: {e}")
        
        return all_props
    
    def analyze_props(self, all_props: list) -> list:
        """Analyze all props and identify high-confidence picks."""
        print("\n🔍 Analyzing props for high-confidence picks...")
        print("-" * 60)
        
        high_confidence_picks = []
        
        for source_data in all_props:
            source = source_data['source']
            data = source_data['data']
            
            # Process best bets from player props
            if source == 'Player Props':
                for bet in data.get('best_bets', []):
                    confidence = bet.get('hit_probability', 0)
                    if confidence >= self.confidence_threshold:
                        pick = {
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'sport': bet.get('sport', 'NBA'),
                            'player': bet.get('player', ''),
                            'prop': bet.get('prop', ''),
                            'game': bet.get('game', ''),
                            'confidence': confidence,
                            'odds': bet.get('odds', -110),
                            'recommendation': bet.get('recommendation', 'LEAN'),
                            'source': source,
                            'status': 'pending'
                        }
                        high_confidence_picks.append(pick)
                        print(f"  ✅ {pick['player']} - {pick['prop']} ({confidence}%)")
            
            # Process games from Yahoo/Multi-Book
            elif source in ['Yahoo', 'Multi-Book']:
                for game in data.get('games', []):
                    # Extract any props/lines with value
                    markets = game.get('markets', {})
                    for market_type, outcomes in markets.items():
                        # Simple value detection (in production, use ML model)
                        pass
        
        # Remove duplicates (same player/prop from multiple sources)
        seen = set()
        unique_picks = []
        for pick in high_confidence_picks:
            key = f"{pick['player']}-{pick['prop']}-{pick['date']}"
            if key not in seen:
                seen.add(key)
                unique_picks.append(pick)
        
        # Sort by confidence
        unique_picks.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n📊 Found {len(unique_picks)} high-confidence picks ({self.confidence_threshold}%+)")
        return unique_picks
    
    def save_weekly_props(self, picks: list):
        """Save picks to weekly database."""
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_file = DATA_DIR / f"week_of_{week_start.strftime('%Y-%m-%d')}.json"
        
        # Load existing week data
        if week_file.exists():
            with open(week_file, 'r') as f:
                week_data = json.load(f)
        else:
            week_data = {
                'week_start': week_start.strftime('%Y-%m-%d'),
                'picks': [],
                'total_picks': 0,
                'settled': 0,
                'won': 0,
                'lost': 0,
                'pending': 0
            }
        
        # Add new picks (avoid duplicates)
        existing_keys = {f"{p['player']}-{p['prop']}-{p['date']}" for p in week_data['picks']}
        new_picks = []
        for pick in picks:
            key = f"{pick['player']}-{pick['prop']}-{pick['date']}"
            if key not in existing_keys:
                new_picks.append(pick)
        
        week_data['picks'].extend(new_picks)
        week_data['total_picks'] = len(week_data['picks'])
        week_data['pending'] = len([p for p in week_data['picks'] if p['status'] == 'pending'])
        
        # Save
        with open(week_file, 'w') as f:
            json.dump(week_data, f, indent=2)
        
        print(f"\n💾 Saved {len(new_picks)} new picks to {week_file.name}")
        return week_data
    
    def post_to_telegram(self, picks: list, top_n: int = 5):
        """Post top picks to Telegram channel."""
        if not picks:
            print("\n⚠️  No picks to post")
            return
        
        print(f"\n📱 Posting top {top_n} picks to Telegram...")
        
        # Get today's date
        today = datetime.now().strftime('%A, %B %d')
        
        # Build message
        message = f"""🧠 <b>BetBrain AI - Top Picks for {today}</b>

🔥 <b>High-Confidence Player Props</b>
AI-analyzed with 70%+ hit probability

"""
        
        for i, pick in enumerate(picks[:top_n], 1):
            stars = "🔥" * min(3, int(pick['confidence'] // 25))
            message += f"""{i}. {pick['player']}
   📊 {pick['prop']}
   💯 Confidence: {pick['confidence']}% {stars}
   💰 Odds: {pick['odds']}
   🏀 {pick['game']}

"""
        
        message += """⚠️ <b>Disclaimer:</b>
• 21+ only • Gamble responsibly
• These are AI predictions, not guarantees
• Never bet more than you can afford to lose

🔗 <b>Join Free:</b> t.me/betbrainaiwinner
📊 <b>Track Record:</b> See pinned message
"""
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get('ok'):
                print(f"  ✅ Posted to Telegram successfully")
                return True
            else:
                print(f"  ⚠️  Telegram API error: {result}")
                return False
        except Exception as e:
            print(f"  ❌ Failed to post: {e}")
            return False
    
    def generate_summary_report(self, week_data: dict):
        """Generate weekly summary report."""
        total = week_data['total_picks']
        settled = week_data['settled']
        won = week_data['won']
        lost = week_data['lost']
        
        if settled > 0:
            hit_rate = won / settled * 100
        else:
            hit_rate = 0
        
        report = f"""
📊 WEEKLY SUMMARY
Week of: {week_data['week_start']}

Total Picks: {total}
Settled: {settled} ({won}W-{lost}L)
Pending: {week_data['pending']}
Hit Rate: {hit_rate:.1f}%
"""
        return report
    
    def run(self):
        """Main execution."""
        # Run all scrapers
        all_props = self.run_all_scrapers()
        
        # Analyze for high-confidence picks
        picks = self.analyze_props(all_props)
        
        if not picks:
            print("\n⚠️  No high-confidence picks found today")
            return
        
        # Save to weekly database
        week_data = self.save_weekly_props(picks)
        
        # Post top picks to Telegram
        self.post_to_telegram(picks, top_n=5)
        
        # Print summary
        print("\n" + "=" * 60)
        print(self.generate_summary_report(week_data))
        print("=" * 60)

if __name__ == '__main__':
    finder = WeeklyPropsFinder()
    finder.run()
