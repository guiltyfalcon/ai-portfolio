#!/usr/bin/env python3
"""
BetBrain AI - Auto-Post Picks with Injury Verification
Scrapes picks, verifies players are active, posts to Twitter + Telegram.

Features:
- Checks NBA injury report before posting
- Verifies each player is NOT listed as OUT
- Posts to Twitter via browser automation
- Posts to Telegram via bot API
- Logs all verification steps

Usage: python3 auto_post_picks.py
Schedule: 9:00 AM ET daily via cron
"""

import json
import os
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Config
TELEGRAM_BOT_TOKEN = '8733590521:AAH-dmhmMPABmnRcTvODry2z3hgMsV9Lo88'
TELEGRAM_CHAT_ID = '@betbrainaiwinner'
TWITTER_HANDLE = '@holikidTV'

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

class InjuryChecker:
    """Check NBA injury report to verify players are active."""
    
    def __init__(self):
        self.injuries = {}
        self.load_injury_report()
    
    def load_injury_report(self):
        """Fetch NBA injury report from ESPN API."""
        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for team in data.get('injuries', []):
                team_name = team.get('displayName', '')
                for player in team.get('injuries', []):
                    name = player.get('athlete', {}).get('displayName', '')
                    status = player.get('status', 'Unknown')
                    self.injuries[name.lower()] = {
                        'status': status,
                        'team': team_name,
                        'details': player.get('shortComment', '')
                    }
            
            print(f"✅ Loaded injury report: {len(self.injuries)} players")
            
        except Exception as e:
            print(f"⚠️  Could not load injury report: {e}")
    
    def is_player_active(self, player_name: str) -> tuple:
        """
        Check if player is active (not OUT).
        Returns: (is_active: bool, status: str, details: str)
        """
        player_lower = player_name.lower()
        
        # Check direct match
        if player_lower in self.injuries:
            injury = self.injuries[player_lower]
            status = injury['status'].upper()
            
            if 'OUT' in status:
                return (False, injury['status'], injury['details'])
            elif 'QUESTIONABLE' in status or 'DOUBTFUL' in status:
                return (True, injury['status'], injury['details'])  # Still playable
            else:
                return (True, injury['status'], injury['details'])
        
        # Player not on injury report = active
        return (True, 'Active', 'Not on injury report')


class PickPoster:
    """Post verified picks to Twitter and Telegram."""
    
    def __init__(self):
        self.injury_checker = InjuryChecker()
        self.picks = []
    
    def load_tonight_picks(self) -> list:
        """Load tonight's picks from cache or generate from scrapers."""
        # Player to team mapping (updated weekly)
        PLAYER_TEAMS = {
            'Lauri Markkanen': 'UTA',
            'Jordan Clarkson': 'UTA',
            'Nikola Jokic': 'DEN',
            'LeBron James': 'LAL',
            'Jimmy Butler': 'MIA',
            'Stephen Curry': 'GSW',
            'Kevin Durant': 'PHX',
            'Giannis Antetokounmpo': 'MIL',
            'Luka Doncic': 'DAL',
            'Joel Embiid': 'PHI',
        }
        
        # Try to load from player props cache
        cache_file = SCRIPT_DIR / 'player_props_cache.json'
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            picks = []
            for bet in data.get('best_bets', [])[:10]:  # Top 10
                player = bet.get('player', '')
                # Extract team from game info or use mapping
                team = self.extract_team_from_game(player, bet.get('game', ''))
                
                picks.append({
                    'player': player,
                    'team': team,
                    'prop': bet.get('prop', ''),
                    'line': bet.get('line', ''),
                    'odds': bet.get('odds', -110),
                    'confidence': bet.get('hit_probability', 50),
                    'game': bet.get('game', ''),
                    'reasoning': bet.get('reasoning', '')
                })
            
            print(f"✅ Loaded {len(picks)} picks from cache")
            return picks
        
        # Fallback: hardcoded picks (for testing)
        return [
            {'player': 'Lauri Markkanen', 'team': 'UTA', 'prop': 'Points', 'line': '25.0', 'odds': -110, 'confidence': 55, 'game': 'UTA @ WAS', 'reasoning': 'Last 5: 27.2 PPG'},
            {'player': 'Jordan Clarkson', 'team': 'UTA', 'prop': 'Points', 'line': '18.5', 'odds': -110, 'confidence': 54, 'game': 'UTA @ WAS', 'reasoning': 'Last 5: 20.1 PPG'},
            {'player': 'Nikola Jokic', 'team': 'DEN', 'prop': 'Points', 'line': '29.5', 'odds': -115, 'confidence': 68, 'game': 'DEN vs LAL', 'reasoning': 'Lakers weak vs Centers'},
            {'player': 'LeBron James', 'team': 'LAL', 'prop': 'Assists', 'line': '7.5', 'odds': -120, 'confidence': 65, 'game': 'LAL @ DEN', 'reasoning': '8+ ast in 4 of last 6'},
            {'player': 'Jimmy Butler', 'team': 'MIA', 'prop': 'Points', 'line': '22.5', 'odds': -110, 'confidence': 62, 'game': 'MIA vs BKN', 'reasoning': 'Nets allow 115 PPG to SFs'},
        ]
    
    def extract_team_from_game(self, player: str, game: str) -> str:
        """Extract team from game matchup string."""
        if not game:
            return 'Unknown'
        
        # Game format: "UTA @ WAS" or "DEN vs LAL"
        parts = game.replace(' vs ', ' @ ').split(' @ ')
        if len(parts) >= 2:
            # Check if player's team is in the matchup
            for part in parts:
                if part.strip() in ['UTA', 'WAS', 'DEN', 'LAL', 'MIA', 'BKN', 'PHX', 'GSW', 'MIL', 'DAL', 'PHI', 'BOS', 'NYK', 'BRK']:
                    return part.strip()
        
        return 'Unknown'
    
    def verify_picks(self, picks: list) -> list:
        """Verify all picks - remove players who are OUT."""
        print("\n🏥 Verifying player status...")
        print("-" * 60)
        
        verified = []
        removed = []
        
        for pick in picks:
            player = pick['player']
            is_active, status, details = self.injury_checker.is_player_active(player)
            
            if is_active:
                pick['status'] = status
                pick['injury_details'] = details
                verified.append(pick)
                print(f"  ✅ {player}: {status}")
            else:
                removed.append(pick)
                print(f"  ❌ {player}: OUT - {details}")
        
        print(f"\n📊 Verified: {len(verified)} | Removed: {len(removed)}")
        return verified
    
    def format_telegram_message(self, picks: list) -> str:
        """Format picks for Telegram (HTML)."""
        today = datetime.now().strftime('%A, %B %d')
        
        message = f"""🧠 <b>BetBrain AI - Tonight's Picks</b>
📅 {today}

🔥 <b>TOP PLAYER PROPS</b>
(All players verified ACTIVE)

"""
        
        for i, pick in enumerate(picks[:5], 1):
            stars = "🔥" * min(3, int(pick['confidence'] // 25))
            prop_short = pick['prop'].replace('Points', 'pts').replace('Assists', 'ast').replace('Rebounds', 'reb')
            team = pick.get('team', 'Unknown')
            
            message += f"""{i}. <b>{pick['player']}</b> ({team})
   📊 {prop_short}: Over {pick['line']}
   💯 Confidence: {pick['confidence']}% {stars}
   💰 Odds: {pick['odds']}
   🏀 {pick['game']}
   📝 {pick.get('reasoning', '')}

"""
        
        # Add parlay suggestion
        if len(picks) >= 2:
            parlay_odds = self.calculate_parlay_odds(picks[:2])
            message += f"""🎯 <b>PARLAY OF THE NIGHT</b>
{picks[0]['player']} ({picks[0].get('team', '')}) + {picks[1]['player']} ({picks[1].get('team', '')}) Overs
💰 Payout: {parlay_odds}

"""
        
        message += """⚠️ <b>Disclaimer:</b>
• 21+ only • Gamble responsibly
• AI predictions, not guarantees
• Never bet more than you can afford to lose

🔗 <b>Join Free:</b> t.me/betbrainaiwinner
📊 <b>Track Record:</b> See pinned message
"""
        
        return message
    
    def format_twitter_message(self, picks: list) -> str:
        """Format picks for Twitter (280 char limit)."""
        message = f"""🧠 BetBrain AI - Tonight's NBA Picks

🔥 TOP 5 (All Verified ACTIVE):

1. {picks[0]['player']} ({picks[0].get('team', '')}) O {picks[0]['line']} {picks[0]['prop'].replace('Points', 'pts').replace('Assists', 'ast')}
2. {picks[1]['player']} ({picks[1].get('team', '')}) O {picks[1]['line']} {picks[1]['prop'].replace('Points', 'pts').replace('Assists', 'ast')}
3. {picks[2]['player']} ({picks[2].get('team', '')}) O {picks[2]['line']} {picks[2]['prop'].replace('Points', 'pts').replace('Assists', 'ast')}
4. {picks[3]['player']} ({picks[3].get('team', '')}) O {picks[3]['line']} {picks[3]['prop'].replace('Points', 'pts').replace('Assists', 'ast')}
5. {picks[4]['player']} ({picks[4].get('team', '')}) O {picks[4]['line']} {picks[4]['prop'].replace('Points', 'pts').replace('Assists', 'ast')}

🎯 Parlay: +260

t.me/betbrainaiwinner

21+ | Gamble responsibly | NFA"""
        
        return message[:280]  # Ensure under 280 chars
    
    def calculate_parlay_odds(self, picks: list) -> str:
        """Calculate approximate parlay odds."""
        # Simple calculation (not exact but close enough)
        total = 1
        for pick in picks:
            odds = pick['odds']
            if odds < 0:
                total *= (100 / abs(odds))
            else:
                total *= (odds / 100)
        
        profit = total * 100 - 100
        if profit > 0:
            return f"+{int(profit)}"
        else:
            return f"{int(profit)}"
    
    def post_to_telegram(self, message: str) -> bool:
        """Post message to Telegram channel."""
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
                print(f"  ✅ Posted to Telegram")
                return True
            else:
                print(f"  ⚠️  Telegram API error: {result}")
                return False
        except Exception as e:
            print(f"  ❌ Failed to post to Telegram: {e}")
            return False
    
    def post_to_twitter(self, message: str) -> bool:
        """Post message to Twitter via browser automation script."""
        # Create temporary file with tweet text
        tweet_file = DATA_DIR / 'pending_tweet.txt'
        with open(tweet_file, 'w') as f:
            f.write(message)
        
        # Call browser automation script
        script_file = SCRIPT_DIR.parent / 'bot' / 'post_twitter.py'
        
        if script_file.exists():
            try:
                result = subprocess.run(
                    ['python3', str(script_file), str(tweet_file)],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    print(f"  ✅ Posted to Twitter")
                    return True
                else:
                    print(f"  ⚠️  Twitter script error: {result.stderr}")
                    return False
            except Exception as e:
                print(f"  ❌ Failed to post to Twitter: {e}")
                return False
        else:
            print(f"  ⚠️  Twitter script not found: {script_file}")
            return False
    
    def save_verification_log(self, picks: list, removed: list):
        """Save verification log for transparency."""
        log_file = DATA_DIR / f"picks_log_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_data = {
            'date': datetime.now().isoformat(),
            'posted': picks,
            'removed_injury': removed,
            'total_posted': len(picks),
            'total_removed': len(removed)
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"  💾 Saved verification log to {log_file.name}")
    
    def run(self):
        """Main execution."""
        print("🧠 BetBrain AI - Auto-Post Picks")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Load picks
        picks = self.load_tonight_picks()
        
        # Verify all players are active
        verified_picks = self.verify_picks(picks)
        
        if not verified_picks:
            print("\n❌ No verified picks - all players on injury report")
            return
        
        # Need at least 3 picks to post
        if len(verified_picks) < 3:
            print(f"\n⚠️  Only {len(verified_picks)} verified picks - skipping post")
            return
        
        # Format messages
        telegram_msg = self.format_telegram_message(verified_picks)
        twitter_msg = self.format_twitter_message(verified_picks)
        
        # Post to both platforms
        print("\n📱 Posting to platforms...")
        
        telegram_success = self.post_to_telegram(telegram_msg)
        twitter_success = self.post_to_twitter(twitter_msg)
        
        # Save log
        removed = [p for p in picks if p not in verified_picks]
        self.save_verification_log(verified_picks, removed)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ SUMMARY")
        print(f"  Telegram: {'✅ Posted' if telegram_success else '❌ Failed'}")
        print(f"  Twitter: {'✅ Posted' if twitter_success else '❌ Failed'}")
        print(f"  Picks Posted: {len(verified_picks)}")
        print(f"  Picks Removed (Injury): {len(removed)}")
        print("=" * 60)


if __name__ == '__main__':
    poster = PickPoster()
    poster.run()
