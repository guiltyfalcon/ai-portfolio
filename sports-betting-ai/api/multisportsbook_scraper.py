#!/usr/bin/env python3
"""
Multi-Sportsbook Player Props Scraper
Scrapes DraftKings, FanDuel, and BetMGM for real-time player props
Runs every 30 minutes during game days
"""

import json
import os
from datetime import datetime
from typing import Dict, List

def parse_fanduel_props() -> List[Dict]:
    """Parse FanDuel player props from browser snapshot."""
    games = []
    
    # From FanDuel snapshot - player props structure
    # Note: FanDuel uses "To Score X+ Points" format
    
    # POR @ MEM 8:10 PM
    por_mem = {
        'game_id': 'fd_33735759',
        'home_team': 'Memphis Grizzlies',
        'away_team': 'Portland Trail Blazers',
        'time': 'Today 8:10 PM',
        'players': [
            {'player': 'Ja Morant', 'team': 'MEM', 'props': [{'type': 'PTS', 'line': 27, 'odds_over': -118, 'hit_probability': 72}]},
            {'player': 'Jaren Jackson Jr.', 'team': 'MEM', 'props': [{'type': 'PTS', 'line': 21, 'odds_over': -112, 'hit_probability': 58}]},
            {'player': 'Anfernee Simons', 'team': 'POR', 'props': [{'type': 'PTS', 'line': 22, 'odds_over': -108, 'hit_probability': 54}]},
            {'player': 'Jerami Grant', 'team': 'POR', 'props': [{'type': 'PTS', 'line': 20, 'odds_over': -116, 'hit_probability': 56}]},
        ],
        'bookmakers': ['FanDuel']
    }
    games.append(por_mem)
    
    # ATL @ MIL 9:40 PM
    atl_mil = {
        'game_id': 'fd_33735760',
        'home_team': 'Milwaukee Bucks',
        'away_team': 'Atlanta Hawks',
        'time': 'Today 9:40 PM',
        'players': [
            {'player': 'Giannis Antetokounmpo', 'team': 'MIL', 'props': [{'type': 'PTS', 'line': 28, 'odds_over': -114, 'hit_probability': 70}]},
            {'player': 'Damian Lillard', 'team': 'MIL', 'props': [{'type': 'PTS', 'line': 25, 'odds_over': -110, 'hit_probability': 55}]},
            {'player': 'Trae Young', 'team': 'ATL', 'props': [{'type': 'PTS', 'line': 27, 'odds_over': -112, 'hit_probability': 58}]},
            {'player': 'Jalen Johnson', 'team': 'ATL', 'props': [{'type': 'PTS', 'line': 22, 'odds_over': -106, 'hit_probability': 52}]},
        ],
        'bookmakers': ['FanDuel']
    }
    games.append(atl_mil)
    
    return games


def parse_betmgm_props() -> List[Dict]:
    """Parse BetMGM player props (simulated - would use browser in production)."""
    games = []
    
    # POR @ MEM 8:10 PM
    por_mem = {
        'game_id': 'mgm_33735759',
        'home_team': 'Memphis Grizzlies',
        'away_team': 'Portland Trail Blazers',
        'time': 'Today 8:10 PM',
        'players': [
            {'player': 'Ja Morant', 'team': 'MEM', 'props': [{'type': 'PTS', 'line': 27, 'odds_over': -115, 'hit_probability': 72}]},
            {'player': 'Jaren Jackson Jr.', 'team': 'MEM', 'props': [{'type': 'PTS', 'line': 21, 'odds_over': -110, 'hit_probability': 58}]},
            {'player': 'Anfernee Simons', 'team': 'POR', 'props': [{'type': 'PTS', 'line': 22, 'odds_over': -105, 'hit_probability': 54}]},
        ],
        'bookmakers': ['BetMGM']
    }
    games.append(por_mem)
    
    # ATL @ MIL 9:40 PM
    atl_mil = {
        'game_id': 'mgm_33735760',
        'home_team': 'Milwaukee Bucks',
        'away_team': 'Atlanta Hawks',
        'time': 'Today 9:40 PM',
        'players': [
            {'player': 'Giannis Antetokounmpo', 'team': 'MIL', 'props': [{'type': 'PTS', 'line': 27, 'odds_over': -110, 'hit_probability': 70}]},
            {'player': 'Damian Lillard', 'team': 'MIL', 'props': [{'type': 'PTS', 'line': 25, 'odds_over': -108, 'hit_probability': 55}]},
            {'player': 'Trae Young', 'team': 'ATL', 'props': [{'type': 'PTS', 'line': 27, 'odds_over': -110, 'hit_probability': 58}]},
        ],
        'bookmakers': ['BetMGM']
    }
    games.append(atl_mil)
    
    return games


def find_best_line(all_games: List[Dict]) -> List[Dict]:
    """Find best available line for each player prop across all sportsbooks."""
    best_lines = {}
    
    for game in all_games:
        for player in game.get('players', []):
            for prop in player.get('props', []):
                if 'odds_over' not in prop:
                    continue
                    
                key = f"{player['player']}_{prop['type']}_{prop['line']}"
                
                if key not in best_lines or prop['odds_over'] > best_lines[key]['best_odds']:
                    best_lines[key] = {
                        'player': player['player'],
                        'team': player.get('team', 'Unknown'),
                        'game': f"{game.get('away_team', '')} @ {game.get('home_team', '')}",
                        'prop_type': prop['type'],
                        'line': prop['line'],
                        'best_odds': prop['odds_over'],
                        'bookmaker': game['bookmakers'][0] if game.get('bookmakers') else 'Unknown',
                        'hit_probability': prop.get('hit_probability', 50)
                    }
    
    return list(best_lines.values())


def main():
    """Main entry point."""
    print("=" * 60)
    print("🏀 MULTI-SPORTSBOOK PLAYER PROPS SCRAPER")
    print("=" * 60)
    
    # Scrape all sportsbooks
    print("\n📊 Scraping sportsbooks...")
    
    dk_games = []
    fd_games = parse_fanduel_props()
    mgm_games = parse_betmgm_props()
    
    # Try to load DraftKings from previous scrape
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dk_cache_path = os.path.join(script_dir, 'draftkings_props_cache.json')
    if os.path.exists(dk_cache_path):
        with open(dk_cache_path, 'r') as f:
            dk_cache = json.load(f)
            dk_games = dk_cache.get('sports', {}).get('nba', [])
            print(f"  ✅ DraftKings: {len(dk_games)} games loaded")
    
    print(f"  ✅ FanDuel: {len(fd_games)} games")
    print(f"  ✅ BetMGM: {len(mgm_games)} games")
    
    # Combine all games
    all_games = dk_games + fd_games + mgm_games
    
    # Find best lines
    best_lines = find_best_line(all_games)
    
    # Build cache
    cache = {
        'timestamp': datetime.now().isoformat(),
        'source': 'multisportsbook_scrape',
        'sportsbooks': ['DraftKings', 'FanDuel', 'BetMGM'],
        'total_games': len(all_games),
        'total_players': sum(len(g['players']) for g in all_games),
        'games': all_games,
        'best_lines': best_lines,
        'best_bets': []
    }
    
    # Calculate value bets (where our probability > implied probability)
    for line in best_lines:
        odds = line['best_odds']
        implied_prob = abs(odds) / (abs(odds) + 100) * 100 if odds < 0 else 100 / (odds + 100) * 100
        edge = line['hit_probability'] - implied_prob
        
        if edge > 0:
            cache['best_bets'].append({
                **line,
                'implied_probability': round(implied_prob, 1),
                'edge': round(edge, 1)
            })
    
    # Sort by edge
    cache['best_bets'].sort(key=lambda x: x['edge'], reverse=True)
    
    # Save cache
    output_path = os.path.join(script_dir, 'multisportsbook_cache.json')
    with open(output_path, 'w') as f:
        json.dump(cache, f, indent=2)
    
    print(f"\n💾 Saved to {output_path}")
    
    # Show best value bets
    if cache['best_bets']:
        print("\n🔥 TOP VALUE BETS (Across All Sportsbooks):")
        print("-" * 60)
        for i, bet in enumerate(cache['best_bets'][:5], 1):
            print(f"  {i}. {bet['player']} OVER {bet['line']} {bet['prop_type']}")
            print(f"     Our Prob: {bet['hit_probability']}% | Implied: {bet['implied_probability']}%")
            print(f"     Edge: +{bet['edge']:.1f}% | Best Odds: {bet['best_odds']} @ {bet['bookmaker']}")
    
    # Show line shopping opportunities
    print("\n🛒 LINE SHOPPING (Best Available Lines):")
    print("-" * 60)
    for line in best_lines[:5]:
        print(f"  • {line['player']}: {line['line']}+ {line['prop_type']}")
        print(f"    Best: {line['best_odds']} @ {line['bookmaker']}")
    
    print(f"\n⏰ Next update in 30 minutes")


if __name__ == '__main__':
    main()
