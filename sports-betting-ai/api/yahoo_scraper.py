"""
Yahoo Sports Odds Scraper - Free alternative to The Odds API
Uses Yahoo's hidden API endpoint to fetch live odds
Runs via cron every 2 hours
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Sport mapping for Yahoo API
SPORTS_CONFIG = {
    'nba': {'league': 'nba', 'key': 'basketball_nba'},
    'nfl': {'league': 'nfl', 'key': 'americanfootball_nfl'},
    'mlb': {'league': 'mlb', 'key': 'baseball_mlb'},
    'nhl': {'league': 'nhl', 'key': 'icehockey_nhl'},
    'ncaab': {'league': 'ncaab', 'key': 'basketball_ncaab'},
    'ncaaf': {'league': 'ncaaf', 'key': 'americanfootball_ncaaf'},
}

# Yahoo Sports API endpoint
YAHOO_API_URL = "https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard"

# Bookmaker ID to name mapping (Yahoo uses IDs)
BOOKMAKER_MAP = {
    '101': 'BetMGM',
    '102': 'DraftKings',
    '103': 'FanDuel',
    '104': 'Caesars',
    '105': 'PointsBet',
    '106': 'BetRivers',
}


def get_todays_date() -> str:
    """Get today's date in format YYYY-MM-DD."""
    return datetime.now().strftime('%Y-%m-%d')


def get_team_names_from_game(game_id: str, games_data: Dict) -> tuple:
    """Extract team names from game data."""
    if game_id not in games_data:
        return ('Unknown', 'Unknown')
    
    game = games_data[game_id]
    teams_ref = game.get('teams', [])
    
    # Get team IDs from the reference
    if len(teams_ref) >= 2:
        away_team_id = teams_ref[0] if teams_ref[0] != 'dataIslandPaths' else None
        home_team_id = teams_ref[1] if len(teams_ref) > 1 else None
    else:
        # Try to extract from game data
        away_team_id = game.get('away_team_id')
        home_team_id = game.get('home_team_id')
    
    return (away_team_id, home_team_id)


def get_team_details(team_id: str, teams_data: Dict) -> Dict:
    """Get team details from teams data island."""
    if not team_id or team_id not in teams_data:
        return {'name': 'Unknown', 'abbr': 'UNK'}
    
    team = teams_data[team_id]
    return {
        'name': team.get('display_name', 'Unknown'),
        'abbr': team.get('abbr', 'UNK'),
        'full_name': team.get('full_name', team.get('display_name', 'Unknown'))
    }


def safe_int(value) -> Optional[int]:
    """Safely convert value to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float(value) -> Optional[float]:
    """Safely convert value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def fetch_yahoo_odds(sport: str, date: str = None) -> List[Dict]:
    """
    Fetch odds for a specific sport from Yahoo Sports API.
    
    Args:
        sport: Sport key (nba, nfl, mlb, nhl, ncaab, ncaaf)
        date: Date in YYYY-MM-DD format (default: today)
    
    Returns:
        List of game dictionaries with odds data
    """
    config = SPORTS_CONFIG.get(sport.lower())
    if not config:
        print(f"❌ Unsupported sport: {sport}")
        return []
    
    if date is None:
        date = get_todays_date()
    
    params = {
        'leagues': config['league'],
        'date': date,
        'format': 'json'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        response = requests.get(YAHOO_API_URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        
        if 'service' not in data or 'scoreboard' not in data['service']:
            print(f"❌ {sport.upper()}: Invalid response structure")
            return []
        
        scoreboard = data['service']['scoreboard']
        
        # Get data islands
        games_data = scoreboard.get('games', {})
        odds_data = scoreboard.get('gameodds', {})
        teams_data = scoreboard.get('teams', {})
        
        if not odds_data:
            print(f"⚠️ {sport.upper()}: No odds data available for {date}")
            return []
        
        games = []
        
        for game_id, game_odds_list in odds_data.items():
            # Get game info
            game_info_raw = games_data.get(game_id, {})
            
            # Get team IDs
            away_team_id = game_info_raw.get('away_team_id')
            home_team_id = game_info_raw.get('home_team_id')
            
            # Get team names
            away_team = get_team_details(away_team_id, teams_data)
            home_team = get_team_details(home_team_id, teams_data)
            
            # Get game time
            commence_time = game_info_raw.get('start_time', 'TBD')
            
            # Handle both dict and list formats
            if isinstance(game_odds_list, dict):
                odds_iter = game_odds_list.items()
            elif isinstance(game_odds_list, list):
                odds_iter = enumerate(game_odds_list)
            else:
                continue
            
            # Parse odds from each bookmaker
            for book_key, odds in odds_iter:
                if isinstance(book_key, int):
                    book_id = str(odds.get('book_id', book_key))
                else:
                    book_id = book_key
                
                book_name = BOOKMAKER_MAP.get(book_id, f'Book_{book_id}')
                
                game_info = {
                    'game_id': game_id,
                    'sport': sport.upper(),
                    'home_team': home_team.get('name', 'Unknown'),
                    'away_team': away_team.get('name', 'Unknown'),
                    'home_team_abbr': home_team.get('abbr', 'UNK'),
                    'away_team_abbr': away_team.get('abbr', 'UNK'),
                    'commence_time': commence_time,
                    'bookmaker': book_name,
                    'bookmaker_count': len(game_odds_list) if isinstance(game_odds_list, list) else len(game_odds_list),
                    'source': 'yahoo_sports_api',
                    'cache_timestamp': datetime.now().isoformat()
                }
                
                # Parse moneyline
                if 'home_ml' in odds:
                    game_info['home_ml'] = safe_int(odds['home_ml'])
                if 'away_ml' in odds:
                    game_info['away_ml'] = safe_int(odds['away_ml'])
                
                # Parse spread
                if 'home_spread' in odds:
                    game_info['home_spread'] = safe_float(odds['home_spread'])
                if 'home_line' in odds:
                    game_info['home_spread_odds'] = safe_int(odds['home_line'])
                if 'away_spread' in odds:
                    game_info['away_spread'] = safe_float(odds['away_spread'])
                if 'away_line' in odds:
                    game_info['away_spread_odds'] = safe_int(odds['away_line'])
                
                # Parse totals
                if 'total' in odds:
                    game_info['total'] = safe_float(odds['total'])
                if 'over_line' in odds:
                    game_info['over_odds'] = safe_int(odds['over_line'])
                if 'under_line' in odds:
                    game_info['under_odds'] = safe_int(odds['under_line'])
                
                games.append(game_info)
        
        print(f"✅ {sport.upper()}: Found {len(games)} games with odds for {date}")
        return games
        
    except requests.exceptions.RequestException as e:
        print(f"❌ {sport.upper()}: Request failed - {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ {sport.upper()}: JSON parse error - {e}")
        return []
    except Exception as e:
        print(f"❌ {sport.upper()}: Error - {e}")
        return []


def scrape_all_odds(days_ahead: int = 1) -> Dict:
    """
    Scrape odds for all supported sports.
    
    Args:
        days_ahead: Number of days to fetch (1 = today only)
    
    Returns:
        Dictionary with all odds data
    """
    all_odds = {
        'timestamp': datetime.now().isoformat(),
        'source': 'yahoo_sports_api',
        'sports': {}
    }
    
    # Calculate dates to fetch
    dates = []
    for i in range(days_ahead):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        dates.append(date)
    
    for sport in SPORTS_CONFIG.keys():
        all_games = []
        for date in dates:
            games = fetch_yahoo_odds(sport, date)
            all_games.extend(games)
        
        if all_games:
            all_odds['sports'][sport] = all_games
    
    return all_odds


def save_odds_cache(data: Dict, cache_path: str = None):
    """Save odds data to cache file."""
    if cache_path is None:
        # Default to same directory as this script
        cache_path = os.path.join(os.path.dirname(__file__), 'yahoo_odds_cache.json')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Saved odds cache to {cache_path}")
    return cache_path


def load_odds_cache(cache_path: str = None) -> Optional[Dict]:
    """Load odds from cache file."""
    if cache_path is None:
        cache_path = os.path.join(os.path.dirname(__file__), 'yahoo_odds_cache.json')
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None


def get_sport_from_cache(sport: str, cache_path: str = None) -> List[Dict]:
    """Get odds for a specific sport from cache."""
    cache = load_odds_cache(cache_path)
    if not cache:
        return []
    
    return cache.get('sports', {}).get(sport.lower(), [])


if __name__ == '__main__':
    print(f"🏃 Starting Yahoo Sports odds scraper at {datetime.now()}")
    print(f"📅 Fetching odds for today and tomorrow")
    
    # Scrape all sports for today and tomorrow
    odds_data = scrape_all_odds(days_ahead=2)
    
    # Save to cache
    cache_file = save_odds_cache(odds_data)
    
    # Print summary
    total_games = sum(len(games) for games in odds_data['sports'].values())
    print(f"\n📊 Scraped {total_games} total games across {len(odds_data['sports'])} sports")
    for sport, games in odds_data['sports'].items():
        print(f"   - {sport.upper()}: {len(games)} games")
    print(f"\n💾 Cache saved to: {cache_file}")
    print(f"⏰ Next update in 2 hours")
