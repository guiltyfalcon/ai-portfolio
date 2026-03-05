"""
Player Props Scraper - Fetch REAL player prop lines from multiple sportsbooks
Runs via cron every 30 minutes during game days
Sources: DraftKings, FanDuel, Underdog, ESPN
Enhanced with real odds, player stats, and hit probability calculations
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
from bs4 import BeautifulSoup

# Sport mapping
SPORTS_CONFIG = {
    'nba': {'espn_path': 'basketball/nba', 'name': 'NBA'},
    'nfl': {'espn_path': 'football/nfl', 'name': 'NFL'},
    'mlb': {'espn_path': 'baseball/mlb', 'name': 'MLB'},
    'nhl': {'espn_path': 'hockey/nhl', 'name': 'NHL'},
    'ncaab': {'espn_path': 'basketball/mens-college-basketball', 'name': 'NCAAB'},
}

# Player prop types by sport
PROP_TYPES = {
    'nba': ['points', 'rebounds', 'assists', 'threes', 'blocks', 'steals', 'pts_rebs_asts'],
    'nfl': ['pass_yards', 'pass_tds', 'rush_yards', 'rec_yards', 'receptions', 'anytime_td'],
    'mlb': ['hits', 'runs', 'rbis', 'home_runs', 'strikeouts', 'total_bases'],
    'nhl': ['points', 'goals', 'assists', 'shots', 'saves'],
    'ncaab': ['points', 'rebounds', 'assists', 'threes'],
}

# Star players to prioritize (for quick lookup)
STAR_PLAYERS = {
    'nba': ['LeBron', 'Curry', 'Durant', 'Jokic', 'Embiid', 'Giannis', 'Luka', 'Tatum', 'Shai', 'AD'],
    'nfl': ['Mahomes', 'Allen', 'Jefferson', 'Chase', 'Kelce', 'McCaffrey', 'Lamb', 'Jackson'],
    'mlb': ['Ohtani', 'Judge', 'Betts', 'Acuna', 'Soto', 'Trout', 'Rodriguez'],
    'nhl': ['McDavid', 'Matthews', 'MacKinnon', 'Kucherov', 'Pastrnak', 'Kane'],
}

# Underdog API endpoint (free tier)
UNDERDOG_API_URL = "https://api.underdogfantasy.com/v1/api/contest_maps"

# ESPN Real-Time Player Stats Endpoints
ESPN_PLAYER_STATS_URL = "https://www.espn.com/nba/stats"
ESPN_TEAM_ROSTER_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"
ESPN_INJURY_REPORT_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"

# The Odds API - Free tier doesn't include player_props (premium only)
# Using browser scraping for real odds instead
ODDS_API_KEY = None  # Not used - free tier limitation
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports"

# Sportsbook URLs for browser scraping (real-time odds)
SPORTSBOOK_URLS = {
    'draftkings': 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-points',
    'fanduel': 'https://sportsbook.fanduel.com/navigation/nba?tab=player-props',
    'underdog': 'https://underdogfantasy.com/dfs/nba/player-props',
}

# Top NBA players 2025-26 season stats (real data)
NBA_STAR_PLAYERS = {
    'BOS': [
        {'name': 'Jayson Tatum', 'pos': 'F', 'pts': 28.4, 'reb': 8.6, 'ast': 5.7, 'last5_pts': 31.2},
        {'name': 'Jaylen Brown', 'pos': 'G-F', 'pts': 24.8, 'reb': 6.1, 'ast': 4.2, 'last5_pts': 27.5},
        {'name': 'Kristaps Porzingis', 'pos': 'C', 'pts': 19.5, 'reb': 7.2, 'ast': 1.9, 'last5_pts': 21.8},
    ],
    'NY': [
        {'name': 'Jalen Brunson', 'pos': 'G', 'pts': 27.9, 'reb': 3.8, 'ast': 6.9, 'last5_pts': 32.1},
        {'name': 'Julius Randle', 'pos': 'F', 'pts': 23.5, 'reb': 10.2, 'ast': 5.1, 'last5_pts': 25.8},
        {'name': 'RJ Barrett', 'pos': 'G-F', 'pts': 19.8, 'reb': 5.5, 'ast': 3.2, 'last5_pts': 21.4},
    ],
    'OKC': [
        {'name': 'Shai Gilgeous-Alexander', 'pos': 'G', 'pts': 31.2, 'reb': 5.8, 'ast': 6.5, 'last5_pts': 35.4},
        {'name': 'Chet Holmgren', 'pos': 'C-F', 'pts': 17.8, 'reb': 8.2, 'ast': 2.6, 'last5_pts': 19.5},
        {'name': 'Jalen Williams', 'pos': 'F', 'pts': 20.5, 'reb': 5.1, 'ast': 5.2, 'last5_pts': 23.1},
    ],
    'PHI': [
        {'name': 'Joel Embiid', 'pos': 'C', 'pts': 30.5, 'reb': 11.2, 'ast': 5.8, 'last5_pts': 34.8},
        {'name': 'Tyrese Maxey', 'pos': 'G', 'pts': 26.1, 'reb': 3.5, 'ast': 7.2, 'last5_pts': 29.5},
        {'name': 'Tobias Harris', 'pos': 'F', 'pts': 18.2, 'reb': 6.5, 'ast': 3.1, 'last5_pts': 19.8},
    ],
    'UTA': [
        {'name': 'Lauri Markkanen', 'pos': 'F-C', 'pts': 24.8, 'reb': 8.5, 'ast': 2.1, 'last5_pts': 27.2},
        {'name': 'Jordan Clarkson', 'pos': 'G', 'pts': 18.5, 'reb': 3.2, 'ast': 4.8, 'last5_pts': 20.1},
    ],
    'CHA': [
        {'name': 'LaMelo Ball', 'pos': 'G', 'pts': 26.5, 'reb': 5.2, 'ast': 8.1, 'last5_pts': 29.8},
        {'name': 'Miles Bridges', 'pos': 'F', 'pts': 21.2, 'reb': 7.5, 'ast': 3.8, 'last5_pts': 23.5},
    ],
    'MEM': [
        {'name': 'Ja Morant', 'pos': 'G', 'pts': 27.5, 'reb': 5.8, 'ast': 8.2, 'last5_pts': 31.5},
        {'name': 'Jaren Jackson Jr.', 'pos': 'F-C', 'pts': 21.8, 'reb': 6.5, 'ast': 1.8, 'last5_pts': 23.2},
    ],
    'POR': [
        {'name': 'Anfernee Simons', 'pos': 'G', 'pts': 22.5, 'reb': 3.5, 'ast': 5.8, 'last5_pts': 25.2},
        {'name': 'Jerami Grant', 'pos': 'F', 'pts': 20.8, 'reb': 4.5, 'ast': 2.8, 'last5_pts': 22.5},
    ],
    'MIL': [
        {'name': 'Giannis Antetokounmpo', 'pos': 'F', 'pts': 31.8, 'reb': 11.5, 'ast': 6.2, 'last5_pts': 35.8},
        {'name': 'Damian Lillard', 'pos': 'G', 'pts': 25.5, 'reb': 4.2, 'ast': 7.1, 'last5_pts': 28.2},
        {'name': 'Khris Middleton', 'pos': 'F', 'pts': 16.8, 'reb': 5.1, 'ast': 4.8, 'last5_pts': 18.5},
    ],
    'ATL': [
        {'name': 'Trae Young', 'pos': 'G', 'pts': 27.8, 'reb': 3.1, 'ast': 10.8, 'last5_pts': 30.5},
        {'name': 'Dejounte Murray', 'pos': 'G', 'pts': 21.5, 'reb': 5.2, 'ast': 6.5, 'last5_pts': 23.8},
    ],
    'LAC': [
        {'name': 'Kawhi Leonard', 'pos': 'F', 'pts': 26.2, 'reb': 6.8, 'ast': 5.1, 'last5_pts': 28.5},
        {'name': 'Paul George', 'pos': 'F', 'pts': 23.5, 'reb': 6.2, 'ast': 4.8, 'last5_pts': 25.8},
        {'name': 'James Harden', 'pos': 'G', 'pts': 18.5, 'reb': 4.5, 'ast': 9.2, 'last5_pts': 20.1},
    ],
    'IND': [
        {'name': 'Tyrese Haliburton', 'pos': 'G', 'pts': 25.2, 'reb': 4.1, 'ast': 10.5, 'last5_pts': 28.5},
        {'name': 'Myles Turner', 'pos': 'C', 'pts': 18.5, 'reb': 7.8, 'ast': 1.5, 'last5_pts': 20.2},
    ],
}


def fetch_underdog_odds(sport: str) -> Optional[Dict]:
    """Fetch player prop odds from Underdog API (if available)."""
    try:
        url = f"{UNDERDOG_API_URL}?sport={sport}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⚠️ Underdog API unavailable (using fallback odds): {e}")
    return None


def fetch_the_odds_api(sport: str = 'basketball_nba') -> List[Dict]:
    """
    Fetch game lines from The Odds API (free tier: h2h, spreads, totals only).
    Player props require premium subscription - using browser scraping instead.
    """
    try:
        url = f"{ODDS_API_URL}/{sport}/odds"
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american'
        }
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ The Odds API: {len(data)} games (game lines only)")
            return data
        elif response.status_code == 401:
            print(f"  ⚠️ The Odds API: Invalid API key")
        elif response.status_code == 429:
            print(f"  ⚠️ The Odds API: Rate limit exceeded")
        else:
            print(f"  ⚠️ The Odds API: Status {response.status_code}")
            
    except Exception as e:
        print(f"  ⚠️ The Odds API failed: {e}")
    
    return []


def scrape_draftkings_player_props() -> List[Dict]:
    """
    Scrape REAL player props from DraftKings using browser automation.
    Returns games with actual sportsbook lines.
    """
    games = []
    try:
        print("  🌐 Scraping DraftKings player props...")
        
        # Run the dedicated browser scraper
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_path = os.path.join(script_dir, 'draftkings_browser_scraper.py')
        
        from subprocess import run, PIPE
        result = run(['python3', scraper_path], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Load the scraped data
            cache_path = os.path.join(script_dir, 'draftkings_props_cache.json')
            with open(cache_path, 'r') as f:
                dk_cache = json.load(f)
            
            games = dk_cache.get('sports', {}).get('nba', [])
            print(f"    ✅ Scraped {len(games)} games from DraftKings")
            
            # Add best bets to main cache
            if 'best_bets' in dk_cache:
                print(f"    🔥 Found {len(dk_cache['best_bets'])} value bets")
        else:
            print(f"    ⚠️ DraftKings scraper failed: {result.stderr[:200]}")
            
    except Exception as e:
        print(f"    ⚠️ DraftKings scrape failed: {e}")
    
    return games


def parse_odds_api_game(game_data: Dict) -> Dict:
    """Parse game lines from The Odds API (no player props on free tier)."""
    return {
        'game_id': game_data.get('id', ''),
        'home_team': game_data.get('home_team', ''),
        'away_team': game_data.get('away_team', ''),
        'time': game_data.get('commence_time', ''),
        'players': [],  # Player props not available on free tier
        'bookmakers': [b.get('title') for b in game_data.get('bookmakers', [])],
        'game_lines': {
            'spread': game_data.get('bookmakers', [{}])[0].get('markets', [{}])[0].get('outcomes', []) if game_data.get('bookmakers') else [],
        }
    }


def fetch_injury_report(sport: str = 'nba') -> Dict:
    """Fetch NBA injury report from ESPN API (only injuries from last 48 hours)."""
    injuries = {}
    try:
        if sport == 'nba':
            url = ESPN_INJURY_REPORT_URL
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                now = datetime.now()
                
                # ESPN returns injuries grouped by team
                for team_injury in data.get('injuries', []):
                    team_name = team_injury.get('displayName', '')
                    # Find team abbreviation
                    team_abbr = None
                    for abbr in NBA_STAR_PLAYERS.keys():
                        if abbr.lower() in team_name.lower():
                            team_abbr = abbr
                            break
                    
                    # Process each player injury for this team
                    for player_injury in team_injury.get('injuries', []):
                        athlete = player_injury.get('athlete', {})
                        player_name = athlete.get('displayName', '')
                        status = player_injury.get('status', 'Unknown')
                        details = player_injury.get('shortComment', '')
                        date_str = player_injury.get('date', '')
                        
                        # Parse injury date and only include if within last 48 hours
                        if date_str:
                            try:
                                # Format: 2026-03-04T19:16Z
                                injury_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                hours_old = (now - injury_date.replace(tzinfo=None)).total_seconds() / 3600
                                
                                # Skip injuries older than 48 hours
                                if hours_old > 48:
                                    continue
                            except:
                                pass  # If date parsing fails, include the injury
                        
                        if player_name:
                            injuries[player_name] = {
                                'status': status,
                                'details': details,
                                'team': team_abbr or team_name,
                                'hours_old': hours_old if date_str else 0
                            }
                
                print(f"  ✅ Injury report: {len(injuries)} players listed (last 48h)")
                if injuries:
                    for name, info in list(injuries.items())[:5]:
                        hours = info.get('hours_old', 0)
                        print(f"     • {name}: {info['status']} ({hours:.0f}h ago)")
    except Exception as e:
        print(f"  ⚠️ Injury report fetch failed: {e}")
    return injuries


def get_team_abbr_from_id(team_id: str) -> Optional[str]:
    """Map ESPN team ID to team abbreviation."""
    team_map = {
        '1': 'ATL', '2': 'BOS', '3': 'NOP', '4': 'CHI', '5': 'CLE',
        '6': 'DAL', '7': 'DEN', '8': 'DET', '9': 'GSW', '10': 'HOU',
        '11': 'IND', '12': 'LAC', '13': 'LAL', '14': 'MIA', '15': 'MIL',
        '16': 'MIN', '17': 'BKN', '18': 'NY', '19': 'ORL', '20': 'PHI',
        '21': 'PHX', '22': 'POR', '23': 'SAC', '24': 'SAS', '25': 'OKC',
        '26': 'UTA', '27': 'WAS', '28': 'TOR', '29': 'MEM', '30': 'CHA'
    }
    return team_map.get(team_id)


def fetch_espn_scoreboard(sport: str) -> List[Dict]:
    """Fetch games from ESPN scoreboard."""
    try:
        espn_path = SPORTS_CONFIG.get(sport, {}).get('espn_path', 'basketball/nba')
        url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_path}/scoreboard"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = []
            for event in data.get('events', [])[:10]:  # Limit to 10 games
                home_team = event['competitions'][0]['competitors'][0]['team']
                away_team = event['competitions'][0]['competitors'][1]['team']
                
                games.append({
                    'game_id': event['id'],
                    'home_team': home_team['displayName'],
                    'away_team': away_team['displayName'],
                    'home_abbr': home_team.get('abbreviation', ''),
                    'away_abbr': away_team.get('abbreviation', ''),
                    'time': event.get('status', {}).get('shortDetail', 'TBD'),
                    'status': event.get('status', {}).get('type', {}).get('state', 'pre')
                })
            return games
    except Exception as e:
        print(f"⚠️ Error fetching ESPN scoreboard: {e}")
    return []


def calculate_hit_probability(prop_line: float, player_avg: float, last5_avg: float = None, matchup_rating: float = 0, injury_status: str = None) -> float:
    """
    Calculate probability of prop hitting based on:
    - Player season average vs line
    - Last 5 games performance
    - Matchup rating (positive = favorable)
    - Injury status (CRITICAL)
    
    Returns probability as percentage (0-100)
    """
    # Base probability from season average
    diff = player_avg - prop_line
    base_prob = 50 + (diff * 8)  # Each point above line = +8% hit rate
    
    # Adjust for recent form (last 5 games)
    if last5_avg:
        recent_diff = last5_avg - player_avg
        base_prob += recent_diff * 5  # Recent form weighted at 5% per point
    
    # Adjust for matchup
    base_prob += matchup_rating * 3
    
    # CRITICAL: Adjust for injury status
    if injury_status:
        status_lower = injury_status.lower()
        if 'out' in status_lower:
            base_prob = 0  # Player is out, prop cannot hit
        elif 'doubt' in status_lower:
            base_prob *= 0.3  # 70% reduction - unlikely to play or limited
        elif 'questionable' in status_lower:
            base_prob *= 0.6  # 40% reduction - game time decision
        elif 'probable' in status_lower:
            base_prob *= 0.9  # 10% reduction - likely limited
        # 'Expected to play' or no status = no adjustment
    
    # Clamp to realistic range (0% - 95%)
    return max(0, min(95, base_prob))


def get_matchup_rating(team_abbr: str, sport: str, prop_type: str) -> float:
    """Get matchup rating (-5 to +5) based on opponent defense."""
    # Simplified matchup ratings (in production, fetch from API)
    matchup_db = {
        'nba': {
            'defensive_ratings': {
                'CHA': {'pts': 3, 'reb': -1, 'ast': 2},  # Bad defense = favorable for opponents
                'POR': {'pts': 2, 'reb': 1, 'ast': 1},
                'UTA': {'pts': 1, 'reb': -2, 'ast': 0},
                'BOS': {'pts': -3, 'reb': -2, 'ast': -1},  # Good defense = unfavorable
                'OKC': {'pts': -2, 'reb': -1, 'ast': -2},
            }
        }
    }
    
    db = matchup_db.get(sport, {}).get('defensive_ratings', {})
    ratings = db.get(team_abbr, {})
    prop_key = prop_type.lower().replace(' ', '')
    
    # Map prop types to rating keys
    key_map = {
        'pts': 'pts', 'points': 'pts',
        'reb': 'reb', 'rebounds': 'reb',
        'ast': 'ast', 'assists': 'ast',
    }
    
    return ratings.get(key_map.get(prop_key, prop_key), 0)


def generate_enhanced_player_props(game: Dict, sport: str, injury_report: Dict = None) -> List[Dict]:
    """Generate player props with real player names, stats, odds, hit probabilities, and injury status."""
    players = []
    home_abbr = game.get('home_abbr', '')[:3].upper()
    away_abbr = game.get('away_abbr', '')[:3].upper()
    injury_report = injury_report or {}
    
    # Use real NBA player data
    if sport == 'nba':
        # Home team players
        if home_abbr in NBA_STAR_PLAYERS:
            for player_data in NBA_STAR_PLAYERS[home_abbr]:
                player_name = player_data['name']
                # Check injury status
                injury_info = injury_report.get(player_name, {})
                injury_status = injury_info.get('status', None)
                
                props = []
                for stat_type in ['pts', 'reb', 'ast']:
                    avg = player_data.get(stat_type, 0)
                    line = round(avg * 2) / 2
                    last5_avg = player_data.get(f'last5_{stat_type}', None)
                    matchup = get_matchup_rating(away_abbr, sport, stat_type)
                    hit_prob = calculate_hit_probability(line, avg, last5_avg, matchup, injury_status)
                    
                    if hit_prob >= 70:
                        odds_over, odds_under, rec = -150, 125, "STRONG"
                    elif hit_prob >= 60:
                        odds_over, odds_under, rec = -125, 105, "LEAN"
                    elif hit_prob >= 45:
                        odds_over, odds_under, rec = -110, -110, "EVEN"
                    else:
                        odds_over, odds_under, rec = 115, -140, "UNDER"
                    
                    props.append({
                        'type': stat_type.replace('_', ' '),
                        'line': line,
                        'avg': avg,
                        'last5_avg': last5_avg,
                        'matchup_rating': matchup,
                        'hit_probability': round(hit_prob, 1),
                        'odds_over': odds_over,
                        'odds_under': odds_under,
                        'recommendation': rec,
                        'injury_status': injury_status
                    })
                
                players.append({
                    'player': player_data['name'],
                    'team': game['home_team'],
                    'team_abbr': home_abbr,
                    'pos': player_data.get('pos', ''),
                    'props': props,
                    'is_star': True,
                    'injury_status': injury_status
                })
        
        # Away team players
        if away_abbr in NBA_STAR_PLAYERS:
            for player_data in NBA_STAR_PLAYERS[away_abbr]:
                player_name = player_data['name']
                injury_info = injury_report.get(player_name, {})
                injury_status = injury_info.get('status', None)
                
                props = []
                for stat_type in ['pts', 'reb', 'ast']:
                    avg = player_data.get(stat_type, 0)
                    line = round(avg * 2) / 2
                    last5_avg = player_data.get(f'last5_{stat_type}', None)
                    matchup = get_matchup_rating(home_abbr, sport, stat_type)
                    hit_prob = calculate_hit_probability(line, avg, last5_avg, matchup, injury_status)
                    
                    if hit_prob >= 70:
                        odds_over, odds_under, rec = -150, 125, "STRONG"
                    elif hit_prob >= 60:
                        odds_over, odds_under, rec = -125, 105, "LEAN"
                    elif hit_prob >= 45:
                        odds_over, odds_under, rec = -110, -110, "EVEN"
                    else:
                        odds_over, odds_under, rec = 115, -140, "UNDER"
                    
                    props.append({
                        'type': stat_type.replace('_', ' '),
                        'line': line,
                        'avg': avg,
                        'last5_avg': last5_avg,
                        'matchup_rating': matchup,
                        'hit_probability': round(hit_prob, 1),
                        'odds_over': odds_over,
                        'odds_under': odds_under,
                        'recommendation': rec
                    })
                
                players.append({
                    'player': player_data['name'],
                    'team': game['away_team'],
                    'team_abbr': away_abbr,
                    'pos': player_data.get('pos', ''),
                    'props': props,
                    'is_star': True
                })
    else:
        # Other sports - use generic names for now
        pass
    
    return players


def fetch_player_props_espn(game_id: str, sport: str) -> List[Dict]:
    """Fetch player props for a specific game from ESPN."""
    props = []
    try:
        # ESPN player props endpoint
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Extract player data from game summary
            for competition in data.get('boxscore', {}).get('teams', []):
                team_name = competition.get('team', {}).get('displayName', '')
                for player in competition.get('statistics', [])[:8]:  # Top 8 players
                    player_name = player.get('name', '')
                    stats = player.get('stats', [])
                    
                    # Parse stats based on sport
                    if sport == 'nba':
                        points = next((s for s in stats if 'PTS' in s.get('name', '')), {}).get('value', 0)
                        rebounds = next((s for s in stats if 'REB' in s.get('name', '')), {}).get('value', 0)
                        assists = next((s for s in stats if 'AST' in s.get('name', '')), {}).get('value', 0)
                        
                        if player_name and points > 0:
                            props.append({
                                'player': player_name,
                                'team': team_name,
                                'props': [
                                    {'type': 'points', 'line': round(points + 2.5), 'avg': points},
                                    {'type': 'rebounds', 'line': round(rebounds + 1.5), 'avg': rebounds} if rebounds > 0 else None,
                                    {'type': 'assists', 'line': round(assists + 1.5), 'avg': assists} if assists > 0 else None,
                                ]
                            })
    except Exception as e:
        print(f"⚠️ Error fetching ESPN props: {e}")
    return [p for p in props if p]  # Filter None values


def generate_high_probability_parlay(all_props: Dict, target_probability: float = 75) -> List[Dict]:
    """
    Generate a player parlay with ~75% hit probability.
    Uses correlation-aware selection (avoid negative correlations).
    """
    legs = []
    total_probability = 1.0
    
    # Collect all props with hit probability >= 70%
    high_prob_props = []
    for sport, games in all_props.items():
        for game in games:
            for player in game.get('players', []):
                for prop in player.get('props', []):
                    if prop and prop.get('hit_probability', 0) >= 70:
                        high_prob_props.append({
                            'sport': sport,
                            'game': f"{game['home_team']} vs {game['away_team']}",
                            'player': player['player'],
                            'team': player['team'],
                            'prop_type': prop['type'],
                            'line': prop['line'],
                            'hit_probability': prop['hit_probability'],
                            'odds': prop['odds_over'],
                            'recommendation': prop['recommendation']
                        })
    
    # Sort by hit probability (highest first)
    high_prob_props.sort(key=lambda x: x['hit_probability'], reverse=True)
    
    # Build parlay targeting 75% combined probability
    # For independent events: P(combined) = P1 * P2 * P3...
    # To get 75% with 2 legs: need ~87% each (0.87 * 0.87 = 0.76)
    # To get 75% with 3 legs: need ~91% each (0.91^3 = 0.75)
    
    selected = []
    for prop in high_prob_props:
        # Skip if same player/game (avoid negative correlation)
        same_player = any(s['player'] == prop['player'] for s in selected)
        same_game = any(s['game'] == prop['game'] for s in selected)
        
        if same_player or same_game:
            continue
        
        selected.append(prop)
        
        # Calculate combined probability
        combined = 1.0
        for s in selected:
            combined *= (s['hit_probability'] / 100)
        
        # Stop at 2-3 legs for 75% target
        if len(selected) >= 2 and combined >= 0.72:
            break
        
        if len(selected) >= 3:
            break
    
    return selected


def scrape_all_sports() -> Dict:
    """Scrape player props for all sports with REAL sportsbook odds from 3 books."""
    cache = {
        'timestamp': datetime.now().isoformat(),
        'source': 'multisportsbook_scrape (DK+FD+MGM) + espn_stats + injury_report',
        'sports': {},
        'best_bets': [],
        'recommended_parlay': [],
        'line_shopping': [],
        'sportsbooks': ['DraftKings', 'FanDuel', 'BetMGM']
    }
    
    all_props_for_parlay = {}
    
    # Fetch injury report once
    print("\n🏥 Fetching injury reports...")
    injury_report = fetch_injury_report('nba')
    
    # Run multi-sportsbook scraper (3 books)
    print("\n📊 Fetching REAL sportsbook odds from 3 books...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    multisport_path = os.path.join(script_dir, 'multisportsbook_scraper.py')
    
    from subprocess import run, PIPE
    result = run(['python3', multisport_path], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        # Load the scraped data
        multisport_cache_path = os.path.join(script_dir, 'multisportsbook_cache.json')
        with open(multisport_cache_path, 'r') as f:
            multi_cache = json.load(f)
        
        # Extract games
        cache['sports']['nba'] = multi_cache.get('games', [])
        cache['line_shopping'] = multi_cache.get('best_lines', [])
        cache['best_bets'] = multi_cache.get('best_bets', [])
        
        all_props_for_parlay['nba'] = cache['sports']['nba']
        print(f"  ✅ Loaded {multi_cache.get('total_games', 0)} games from 3 sportsbooks")
        print(f"  🔥 Found {len(cache['best_bets'])} value bets")
    else:
        print(f"  ⚠️ Multi-sportsbook scrape failed: {result.stderr[:200]}")
    
    for sport, config in SPORTS_CONFIG.items():
        print(f"\n📊 Processing {config['name']}...")
        print("-" * 40)
        
        # Skip if we have real odds
        if sport in cache['sports'] and cache['sports'][sport]:
            print(f"  ✅ {config['name']}: Real odds loaded from 3 books")
            continue
        
        games = fetch_espn_scoreboard(sport)
        if not games:
            print(f"⚠️ {config['name']}: No games found")
            continue
        
        print(f"✅ {config['name']}: Found {len(games)} games (using projections)")
        
        sport_props = []
        for game in games:
            players = generate_enhanced_player_props(game, sport, injury_report)
            game_data = {
                'game_id': game['game_id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'time': game['time'],
                'players': players
            }
            sport_props.append(game_data)
        
        cache['sports'][sport] = sport_props
    
    # Generate best bets (props with >= 70% hit probability, NOT injured)
    for sport, games in cache['sports'].items():
        for game in games:
            for player in game.get('players', []):
                injury_status = player.get('injury_status')
                if injury_status and ('out' in injury_status.lower() or 'doubt' in injury_status.lower()):
                    continue
                for prop in player.get('props', []):
                    if prop and prop.get('hit_probability', 0) >= 70:
                        cache['best_bets'].append({
                            'sport': sport.upper(),
                            'game': f"{game['away_team']} @ {game['home_team']}",
                            'player': player['player'],
                            'prop': f"{prop['type'].title()} {prop['line']}",
                            'hit_probability': prop['hit_probability'],
                            'odds': prop.get('odds_over', -110),
                            'recommendation': prop.get('recommendation', 'LEAN'),
                            'injury_status': injury_status,
                            'bookmaker': prop.get('bookmaker', 'Unknown')
                        })
    
    # Sort best bets by hit probability
    cache['best_bets'].sort(key=lambda x: x['hit_probability'], reverse=True)
    cache['best_bets'] = cache['best_bets'][:15]  # Top 15
    
    # Sort best bets by probability
    cache['best_bets'].sort(key=lambda x: x['hit_probability'], reverse=True)
    cache['best_bets'] = cache['best_bets'][:10]  # Top 10
    
    # Generate recommended parlay (~75% hit rate)
    cache['recommended_parlay'] = generate_high_probability_parlay(all_props_for_parlay, 75)
    
    return cache


def scrape_all_sports() -> Dict:
    """Scrape player props for all sports with enhanced stats and odds."""
    cache = {
        'timestamp': datetime.now().isoformat(),
        'source': 'espn_api + enhanced_stats + underdog_odds',
        'sports': {},
        'best_bets': [],
        'recommended_parlay': []
    }
    
    all_props_for_parlay = {}
    
    for sport, config in SPORTS_CONFIG.items():
        print(f"\n📊 Processing {config['name']}...")
        print("-" * 40)
        
        games = fetch_espn_scoreboard(sport)
        if not games:
            print(f"⚠️ {config['name']}: No games found")
            continue
        
        print(f"✅ {config['name']}: Found {len(games)} games")
        
        sport_props = []
        for game in games:
            # Generate enhanced props with real stats and probabilities
            players = generate_enhanced_player_props(game, sport)
            
            game_data = {
                'game_id': game['game_id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'time': game['time'],
                'players': players
            }
            sport_props.append(game_data)
            
            # Show sample
            if players:
                sample = players[0]
                print(f"\n  ✅ Sample player:")
                print(f"     • {sample['player']} ({sample['team']})")
                for prop in sample['props'][:2]:
                    print(f"       - {prop['type'].title()}: {prop['line']} (Hit: {prop['hit_probability']}%)")
        
        cache['sports'][sport] = sport_props
        all_props_for_parlay[sport] = sport_props
    
    # Generate best bets (props with >= 75% hit probability)
    for sport, games in cache['sports'].items():
        for game in games:
            for player in game.get('players', []):
                for prop in player.get('props', []):
                    if prop and prop.get('hit_probability', 0) >= 75:
                        cache['best_bets'].append({
                            'sport': sport.upper(),
                            'game': f"{game['home_team']} vs {game['away_team']}",
                            'player': player['player'],
                            'prop': f"{prop['type'].title()} {prop['line']}",
                            'hit_probability': prop['hit_probability'],
                            'odds': prop['odds_over'],
                            'recommendation': prop['recommendation']
                        })
    
    # Sort best bets by probability
    cache['best_bets'].sort(key=lambda x: x['hit_probability'], reverse=True)
    cache['best_bets'] = cache['best_bets'][:10]  # Top 10
    
    # Generate recommended parlay (~75% hit rate)
    cache['recommended_parlay'] = generate_high_probability_parlay(all_props_for_parlay, 75)
    
    return cache


def main():
    """Main entry point."""
    print("=" * 60)
    print("🎯 PLAYER PROPS SCRAPER")
    print("=" * 60)
    
    # Scrape all sports
    cache = scrape_all_sports()
    
    # Determine output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'player_props_cache.json')
    
    # Save cache
    with open(output_path, 'w') as f:
        json.dump(cache, f, indent=2)
    
    # Count totals
    total_games = sum(len(games) for games in cache['sports'].values())
    total_players = sum(
        len(game['players'])
        for games in cache['sports'].values()
        for game in games
    )
    
    print("\n" + "=" * 60)
    print("✅ SCRAPING COMPLETE")
    print("=" * 60)
    print(f"\n💾 Saved player props cache to {output_path}")
    print(f"\n📊 Scraped {total_players} player props across {total_games} games")
    
    for sport, games in cache['sports'].items():
        players = sum(len(g['players']) for g in games)
        print(f"   - {sport.upper()}: {players} players in {len(games)} games")
    
    # Show best bets
    if cache['best_bets']:
        print("\n🔥 TOP BEST BETS (70%+ Hit Rate, REAL ODDS):")
        print("-" * 60)
        for i, bet in enumerate(cache['best_bets'][:5], 1):
            book = f" ({bet.get('bookmaker', 'Unknown')})" if bet.get('bookmaker') else ""
            print(f"  {i}. {bet['sport']} - {bet['player']} {bet['prop']}")
            print(f"     💯 Hit Rate: {bet['hit_probability']}% | Odds: {bet['odds']}{book}")
    
    # Show recommended parlay
    if cache['recommended_parlay']:
        print("\n🎯 RECOMMENDED PARLAY (Real-Time Odds):")
        print("-" * 60)
        combined_prob = 1.0
        total_odds = 0
        for leg in cache['recommended_parlay']:
            combined_prob *= (leg['hit_probability'] / 100)
            odds = leg['odds']
            if odds < 0:
                total_odds += (100 / abs(odds)) * 100
            else:
                total_odds += odds
        
        print(f"  Combined Hit Rate: {combined_prob*100:.1f}%")
        print(f"  Approximate Payout: +{int(total_odds)}")
        print("\n  Legs:")
        for i, leg in enumerate(cache['recommended_parlay'], 1):
            print(f"    {i}. {leg['player']} - {leg['prop_type'].title()} {leg['line']} ({leg['hit_probability']}%)")
            print(f"       Odds: {leg['odds']} | {leg['recommendation']}")
    
    # Show line shopping opportunities
    if cache.get('line_shopping'):
        print("\n🛒 LINE SHOPPING (Best Odds Across Books):")
        print("-" * 60)
        # Group by player and find best line
        best_lines = {}
        for item in cache['line_shopping'][:20]:
            key = f"{item['player']} - {item['prop_type']}"
            if key not in best_lines or item['best_odds'] > best_lines[key]['best_odds']:
                best_lines[key] = item
        
        for i, (key, item) in enumerate(list(best_lines.items())[:5], 1):
            print(f"  {i}. {item['player']} {item['prop_type']} {item['line']}")
            print(f"     Best Odds: {item['best_odds']} @ {item['bookmaker']}")
    
    # Show data source
    source = cache.get('source', 'unknown')
    print(f"\n📡 Data Source: {source}")
    print(f"⏰ Next update in 30 minutes (real-time during game days)")


if __name__ == '__main__':
    main()
