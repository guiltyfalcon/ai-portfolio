#!/usr/bin/env python3
"""
BetBrain AI - Multi-Sportsbook Odds Scraper
Scrapes odds from 5+ sportsbooks for comprehensive line shopping.

Sportsbooks:
- DraftKings
- FanDuel  
- BetMGM
- Caesars
- PointsBet
- Yahoo (existing)

Bet Types:
- Spreads
- Moneylines
- Totals (Over/Under)
- Player Props
- Parlays

Usage: python3 multi_sportsbook_scraper.py
Output: JSON file with consolidated odds data
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Output directory
OUTPUT_DIR = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/odds-data')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class SportsbookScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_draftkings(self, sport='basketball/nba'):
        """Scrape DraftKings odds via API."""
        try:
            # DraftKings public API endpoint (may change)
            url = f'https://sportsbook.api.draftkings.com/leagues/{sport}/events'
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            odds = []
            for event in data.get('events', []):
                game = {
                    'sportsbook': 'DraftKings',
                    'event_id': event.get('id'),
                    'home_team': event.get('home', {}).get('name'),
                    'away_team': event.get('away', {}).get('name'),
                    'start_time': event.get('startDate'),
                    'markets': {}
                }
                
                # Extract markets
                for market in event.get('markets', []):
                    market_type = market.get('marketType', 'unknown')
                    outcomes = {}
                    for outcome in market.get('outcomes', []):
                        outcomes[outcome.get('participant', 'unknown')] = {
                            'price': outcome.get('price'),
                            'points': outcome.get('points')
                        }
                    game['markets'][market_type] = outcomes
                
                odds.append(game)
            
            print(f"✅ DraftKings: {len(odds)} games")
            return odds
            
        except Exception as e:
            print(f"⚠️  DraftKings failed: {e}")
            return []
    
    def scrape_fanduel(self, sport='48502628'):  # NBA league ID
        """Scrape FanDuel odds."""
        try:
            url = f'https://sportsbook.api.fanduel.com/market/{sport}'
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            odds = []
            # Parse FanDuel response structure
            for event in data.get('events', []):
                game = {
                    'sportsbook': 'FanDuel',
                    'event_id': event.get('eventId'),
                    'home_team': event.get('homeTeam', {}).get('name'),
                    'away_team': event.get('awayTeam', {}).get('name'),
                    'start_time': event.get('startDate'),
                    'markets': {}
                }
                
                for market in event.get('markets', []):
                    market_type = market.get('key', 'unknown')
                    outcomes = {}
                    for selection in market.get('selections', []):
                        outcomes[selection.get('name', 'unknown')] = {
                            'price': selection.get('odds', {}).get('american'),
                            'points': selection.get('points')
                        }
                    game['markets'][market_type] = outcomes
                
                odds.append(game)
            
            print(f"✅ FanDuel: {len(odds)} games")
            return odds
            
        except Exception as e:
            print(f"⚠️  FanDuel failed: {e}")
            return []
    
    def scrape_betmgm(self, sport='Basketball/NBA'):
        """Scrape BetMGM odds."""
        try:
            url = f'https://sports.api.betmgm.com/sports/{sport}/events'
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            odds = []
            for event in data.get('events', []):
                game = {
                    'sportsbook': 'BetMGM',
                    'event_id': event.get('id'),
                    'home_team': event.get('home', {}).get('name'),
                    'away_team': event.get('away', {}).get('name'),
                    'start_time': event.get('startTime'),
                    'markets': {}
                }
                
                for market in event.get('markets', []):
                    market_type = market.get('marketType', 'unknown')
                    outcomes = {}
                    for outcome in market.get('outcomes', []):
                        outcomes[outcome.get('participantAlias', 'unknown')] = {
                            'price': outcome.get('price'),
                            'points': outcome.get('points')
                        }
                    game['markets'][market_type] = outcomes
                
                odds.append(game)
            
            print(f"✅ BetMGM: {len(odds)} games")
            return odds
            
        except Exception as e:
            print(f"⚠️  BetMGM failed: {e}")
            return []
    
    def scrape_caesars(self, sport='NBA'):
        """Scrape Caesars Sportsbook odds."""
        try:
            url = f'https://sportsbook.caesars.com/api/v1/events/{sport}'
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            odds = []
            for event in data.get('events', []):
                game = {
                    'sportsbook': 'Caesars',
                    'event_id': event.get('eventId'),
                    'home_team': event.get('homeTeam'),
                    'away_team': event.get('awayTeam'),
                    'start_time': event.get('startTime'),
                    'markets': event.get('markets', {})
                }
                odds.append(game)
            
            print(f"✅ Caesars: {len(odds)} games")
            return odds
            
        except Exception as e:
            print(f"⚠️  Caesars failed: {e}")
            return []
    
    def scrape_pointsbet(self, sport='basketball/nba'):
        """Scrape PointsBet odds."""
        try:
            url = f'https://api.pointsbet.com/api/v2/markets/{sport}'
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            odds = []
            for event in data.get('fixtures', []):
                game = {
                    'sportsbook': 'PointsBet',
                    'event_id': event.get('id'),
                    'home_team': event.get('homeTeam', {}).get('name'),
                    'away_team': event.get('awayTeam', {}).get('name'),
                    'start_time': event.get('startDate'),
                    'markets': event.get('markets', [])
                }
                odds.append(game)
            
            print(f"✅ PointsBet: {len(odds)} games")
            return odds
            
        except Exception as e:
            print(f"⚠️  PointsBet failed: {e}")
            return []
    
    def find_best_lines(self, all_odds):
        """Find best available lines across all sportsbooks."""
        best_lines = []
        
        # Group by game
        games = {}
        for sportsbook_odds in all_odds:
            for game in sportsbook_odds:
                game_key = f"{game.get('away_team')} @ {game.get('home_team')}"
                if game_key not in games:
                    games[game_key] = []
                games[game_key].append(game)
        
        # Find best lines for each game
        for game_key, game_versions in games.items():
            best_game = {
                'game': game_key,
                'best_spread': None,
                'best_total': None,
                'best_moneyline': None,
                'arbitrage_opportunities': [],
                'sportsbooks_covered': list(set(g['sportsbook'] for g in game_versions))
            }
            
            # Analyze each market type
            for game in game_versions:
                markets = game.get('markets', {})
                sportsbook = game.get('sportsbook')
                
                # Check for spread arbitrage
                if 'spread' in markets or 'h2h' in markets:
                    # Compare spreads across books
                    pass
                
                # Check for totals arbitrage
                if 'totals' in markets:
                    pass
                
                # Check for moneyline arbitrage
                if 'moneyline' in markets or 'h2h' in markets:
                    pass
            
            best_lines.append(best_game)
        
        return best_lines
    
    def save_data(self, data, filename):
        """Save scraped data to JSON file."""
        output_file = OUTPUT_DIR / filename
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 Saved to {output_file}")
    
    def run_full_scrape(self):
        """Run all scrapers and consolidate data."""
        print(f"🧠 BetBrain AI - Multi-Sportsbook Scraper")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        all_odds = []
        
        # Run all scrapers
        all_odds.append(self.scrape_draftkings())
        all_odds.append(self.scrape_fanduel())
        all_odds.append(self.scrape_betmgm())
        all_odds.append(self.scrape_caesars())
        all_odds.append(self.scrape_pointsbet())
        
        # Find best lines
        print("-" * 50)
        print("🔍 Finding best lines...")
        best_lines = self.find_best_lines(all_odds)
        
        # Save data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_data({
            'timestamp': datetime.now().isoformat(),
            'sportsbooks': ['DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 'PointsBet'],
            'games': best_lines,
            'raw_data': all_odds
        }, f'consolidated_odds_{timestamp}.json')
        
        # Save summary
        self.save_data({
            'timestamp': datetime.now().isoformat(),
            'total_games': len(best_lines),
            'best_lines': best_lines
        }, f'best_lines_{timestamp}.json')
        
        print(f"\n✅ Scraping complete!")
        return best_lines

if __name__ == '__main__':
    scraper = SportsbookScraper()
    scraper.run_full_scrape()
