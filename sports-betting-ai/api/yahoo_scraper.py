"""
Yahoo Sports Odds Scraper - Free alternative to The Odds API
Uses Yahoo's hidden API endpoint to fetch live odds
Runs via cron every 2 hours
"""

import requests
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Try to import BeautifulSoup, fallback to regex if not installed
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️ BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")

# Sport mapping for Yahoo API
SPORTS_CONFIG = {
    'nba': {'league': 'nba', 'key': 'basketball_nba', 'espn_path': 'nba'},
    'nfl': {'league': 'nfl', 'key': 'americanfootball_nfl', 'espn_path': 'nfl'},
    'mlb': {'league': 'mlb', 'key': 'baseball_mlb', 'espn_path': 'mlb'},
    'nhl': {'league': 'nhl', 'key': 'icehockey_nhl', 'espn_path': 'nhl'},
    'ncaab': {'league': 'ncaab', 'key': 'basketball_ncaab', 'espn_path': 'mens-college-basketball'},
    'ncaaf': {'league': 'ncaaf', 'key': 'americanfootball_ncaaf', 'espn_path': 'college-football'},
}

# ESPN URLs for different data types
ESPN_URLS = {
    'standings': 'https://www.espn.com/{sport}/standings',
    'injuries': 'https://www.espn.com/{sport}/injuries',
    'teams': 'https://www.espn.com/{sport}/teams',
}

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


# ========== ESPN SCRAPING FUNCTIONS ==========

def get_headers():
    """Get headers for web scraping requests."""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }


def scrape_espn_standings(sport: str) -> Dict[str, Dict]:
    """
    Scrape team standings from ESPN.
    
    Args:
        sport: Sport key (nba, nfl, mlb, nhl, ncaab, ncaaf)
    
    Returns:
        Dict mapping team names to their records
    """
    if not BS4_AVAILABLE:
        print(f"⚠️ {sport.upper()}: BeautifulSoup not available, skipping ESPN standings")
        return {}
    
    config = SPORTS_CONFIG.get(sport.lower())
    if not config:
        return {}
    
    espn_path = config['espn_path']
    url = ESPN_URLS['standings'].format(sport=espn_path)
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        team_records = {}
        
        # Find standings tables
        tables = soup.find_all('table', class_='standings')
        if not tables:
            tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    # Try to find team name
                    team_cell = cells[0]
                    team_link = team_cell.find('a', href=re.compile(r'/team/'))
                    if not team_link:
                        team_link = team_cell.find('a')
                    
                    if team_link:
                        team_name = team_link.get_text(strip=True)
                        # Handle different ESPN formats
                        if team_name and len(team_name) > 1:
                            # Look for record in format XX-XX
                            for cell in cells[1:]:
                                text = cell.get_text(strip=True)
                                match = re.match(r'(\d+)-(\d+)', text)
                                if match:
                                    wins = int(match.group(1))
                                    losses = int(match.group(2))
                                    team_records[team_name] = {
                                        'wins': wins,
                                        'losses': losses,
                                        'record': f"{wins}-{losses}",
                                        'win_pct': round(wins / (wins + losses), 3) if (wins + losses) > 0 else 0
                                    }
                                    break
        
        print(f"✅ {sport.upper()}: Scraped {len(team_records)} team records from ESPN")
        return team_records
        
    except Exception as e:
        print(f"⚠️ {sport.upper()}: Could not scrape ESPN standings - {e}")
        return {}


def scrape_espn_injuries(sport: str) -> Dict[str, List[Dict]]:
    """
    Scrape injury reports from ESPN.
    
    Args:
        sport: Sport key (nba, nfl, mlb, nhl)
    
    Returns:
        Dict mapping team names to list of injured players
    """
    if not BS4_AVAILABLE:
        print(f"⚠️ {sport.upper()}: BeautifulSoup not available, skipping ESPN injuries")
        return {}
    
    config = SPORTS_CONFIG.get(sport.lower())
    if not config:
        return {}
    
    # College sports don't have reliable injury pages
    if sport in ['ncaab', 'ncaaf']:
        return {}
    
    espn_path = config['espn_path']
    url = ESPN_URLS['injuries'].format(sport=espn_path)
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        team_injuries = {}
        
        # Find team sections
        team_sections = soup.find_all('div', class_=re.compile(r'team|injury'))
        
        for section in team_sections:
            # Get team name
            team_header = section.find(['h3', 'h2', 'div'], class_=re.compile(r'team-name|header'))
            if not team_header:
                team_header = section.find(['h3', 'h2'])
            
            if team_header:
                team_name = team_header.get_text(strip=True)
                
                # Find injured players
                injuries = []
                player_rows = section.find_all('tr') or section.find_all('div', class_=re.compile(r'player|injury'))
                
                for row in player_rows:
                    player_name = None
                    injury_status = None
                    injury_desc = None
                    
                    # Try different formats
                    name_elem = row.find(['td', 'span', 'div'], class_=re.compile(r'player|name'))
                    if name_elem:
                        player_name = name_elem.get_text(strip=True)
                    
                    status_elem = row.find(['td', 'span', 'div'], class_=re.compile(r'status|position'))
                    if status_elem:
                        status_text = status_elem.get_text(strip=True)
                        if any(x in status_text.lower() for x in ['out', 'questionable', 'doubtful', 'probable']):
                            injury_status = status_text
                    
                    desc_elem = row.find(['td', 'span', 'div'], class_=re.compile(r'desc|comment'))
                    if desc_elem:
                        injury_desc = desc_elem.get_text(strip=True)
                    
                    if player_name and len(player_name) > 2:
                        injuries.append({
                            'name': player_name,
                            'status': injury_status or 'Unknown',
                            'description': injury_desc or 'No details available'
                        })
                
                if injuries:
                    team_injuries[team_name] = injuries
        
        print(f"✅ {sport.upper()}: Scraped injuries for {len(team_injuries)} teams from ESPN")
        return team_injuries
        
    except Exception as e:
        print(f"⚠️ {sport.upper()}: Could not scrape ESPN injuries - {e}")
        return {}


def scrape_espn_recent_form(sport: str) -> Dict[str, Dict]:
    """
    Scrape recent game results/schedule to determine form.
    
    Args:
        sport: Sport key (nba, nfl, mlb, nhl, ncaab, ncaaf)
    
    Returns:
        Dict mapping team names to recent form data
    """
    if not BS4_AVAILABLE:
        print(f"⚠️ {sport.upper()}: BeautifulSoup not available, skipping ESPN form data")
        return {}
    
    config = SPORTS_CONFIG.get(sport.lower())
    if not config:
        return {}
    
    espn_path = config['espn_path']
    url = f"https://www.espn.com/{espn_path}/scoreboard"
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        team_form = {}
        
        # Find completed games
        games = soup.find_all('article', class_=re.compile(r'scoreboard'))
        if not games:
            games = soup.find_all('div', class_=re.compile(r'scoreboard|game'))
        
        for game in games:
            # Try to find teams and scores
            teams = game.find_all('div', class_=re.compile(r'team|participant'))
            if len(teams) >= 2:
                for team_elem in teams:
                    team_name_elem = team_elem.find(['span', 'a', 'div'], class_=re.compile(r'team|name'))
                    if team_name_elem:
                        team_name = team_name_elem.get_text(strip=True)
                        
                        # Get score if available
                        score_elem = team_elem.find(['span', 'div'], class_=re.compile(r'score'))
                        if score_elem:
                            score_text = score_elem.get_text(strip=True)
                            if team_name not in team_form:
                                team_form[team_name] = {'last_5': [], 'points_per_game': []}
        
        # Format last 5 for teams with data
        for team, data in team_form.items():
            if data['last_5']:
                recent = data['last_5'][-5:]  # Last 5 games
                wins = recent.count('W')
                form_str = ''.join(recent)
                data['last_5_form'] = form_str
                data['last_5_wins'] = wins
        
        print(f"✅ {sport.upper()}: Scraped recent form for {len(team_form)} teams")
        return team_form
        
    except Exception as e:
        print(f"⚠️ {sport.upper()}: Could not scrape ESPN schedule - {e}")
        return {}


def enrich_game_data(game: Dict, sport: str, standings: Dict, injuries: Dict, recent_form: Dict) -> Dict:
    """
    Enrich game data with ESPN scraped information.
    
    Args:
        game: Game dictionary from Yahoo
        sport: Sport key
        standings: Team standings from ESPN
        injuries: Injury data from ESPN  
        recent_form: Recent form data from ESPN
    
    Returns:
        Enriched game dictionary
    """
    home_team = game.get('home_team', '')
    away_team = game.get('away_team', '')
    
    # Helper to find team data with fuzzy matching
    def find_team_data(team_name: str, data_dict: Dict) -> Dict:
        if not team_name:
            return {}
        
        # Try exact match first
        if team_name in data_dict:
            return data_dict[team_name]
        
        # Try partial match
        for key in data_dict:
            if team_name.lower() in key.lower() or key.lower() in team_name.lower():
                return data_dict[key]
        
        return {}
    
    # Add standings data
    home_standings = find_team_data(home_team, standings)
    away_standings = find_team_data(away_team, standings)
    
    if home_standings:
        game['home_record'] = home_standings.get('record', '0-0')
        game['home_win_pct'] = home_standings.get('win_pct', 0)
        game['home_wins'] = home_standings.get('wins', 0)
        game['home_losses'] = home_standings.get('losses', 0)
    
    if away_standings:
        game['away_record'] = away_standings.get('record', '0-0')
        game['away_win_pct'] = away_standings.get('win_pct', 0)
        game['away_wins'] = away_standings.get('wins', 0)
        game['away_losses'] = away_standings.get('losses', 0)
    
    # Add injury data
    home_injuries = find_team_data(home_team, injuries)
    away_injuries = find_team_data(away_team, injuries)
    
    if home_injuries:
        game['home_injuries'] = home_injuries
        # Create summary string
        key_injuries = [f"{p['name']} ({p['status']})" for p in home_injuries[:3]]
        game['home_injuries_summary'] = '; '.join(key_injuries) if key_injuries else 'None reported'
    
    if away_injuries:
        game['away_injuries'] = away_injuries
        key_injuries = [f"{p['name']} ({p['status']})" for p in away_injuries[:3]]
        game['away_injuries_summary'] = '; '.join(key_injuries) if key_injuries else 'None reported'
    
    # Add recent form
    home_form = find_team_data(home_team, recent_form)
    away_form = find_team_data(away_team, recent_form)
    
    if home_form and 'last_5_form' in home_form:
        game['home_last_5'] = home_form['last_5_form']
    
    if away_form and 'last_5_form' in away_form:
        game['away_last_5'] = away_form['last_5_form']
    
    # Calculate home court advantage factor
    game['home_court_advantage'] = calculate_home_advantage(game)
    
    return game


def calculate_home_advantage(game: Dict) -> float:
    """
    Calculate home court advantage factor based on records.
    
    Returns:
        Float between 0-1 representing home advantage (0.5 = no advantage)
    """
    home_pct = game.get('home_win_pct', 0.5)
    away_pct = game.get('away_win_pct', 0.5)
    
    if home_pct == 0.5 and away_pct == 0.5:
        return 0.5
    
    if home_pct == 0:
        home_pct = 0.1
    if away_pct == 0:
        away_pct = 0.1
    
    # Calculate advantage (home team performance relative to away)
    total_performance = home_pct + away_pct
    if total_performance == 0:
        return 0.5
    
    return home_pct / total_performance


# ========== YAHOO ODDS FUNCTIONS ==========


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
    Scrape odds from Yahoo AND team data from ESPN for all supported sports.
    
    Args:
        days_ahead: Number of days to fetch (1 = today only)
    
    Returns:
        Dictionary with all odds data enriched with ESPN team stats
    """
    all_odds = {
        'timestamp': datetime.now().isoformat(),
        'source': 'yahoo_sports_api + espn_team_data',
        'sports': {}
    }
    
    # ESPN API mapping
    espn_api_map = {
        'nba': 'basketball/nba',
        'nfl': 'football/nfl',
        'mlb': 'baseball/mlb',
        'nhl': 'hockey/nhl',
        'ncaab': 'basketball/mens-college-basketball',
        'ncaaf': 'football/college-football',
    }
    
    def fetch_espn_standings_api(sport: str) -> Dict:
        """Fetch team standings from ESPN API."""
        if sport not in espn_api_map:
            return {}
        
        url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_api_map[sport]}/standings"
        try:
            response = requests.get(url, headers=get_headers(), timeout=15)
            data = response.json()
            team_records = {}
            
            if 'standings' in data:
                entries = []
                if 'entries' in data['standings']:
                    entries = data['standings']['entries']
                elif 'conferences' in data['standings']:
                    for conf in data['standings']['conferences']:
                        if 'entries' in conf:
                            entries.extend(conf['entries'])
                elif 'divisions' in data['standings']:
                    for div in data['standings']['divisions']:
                        if 'entries' in div:
                            entries.extend(div['entries'])
                
                for entry in entries:
                    team_info = entry.get('team', {})
                    team_name = team_info.get('displayName', '')
                    if team_name:
                        stats = entry.get('stats', [])
                        wins, losses = 0, 0
                        for stat in stats:
                            if stat.get('name') == 'wins':
                                wins = int(stat.get('value', 0))
                            elif stat.get('name') == 'losses':
                                losses = int(stat.get('value', 0))
                        if wins == 0 and losses == 0:
                            for stat in stats:
                                if stat.get('abbreviation') == 'W':
                                    wins = int(stat.get('value', 0))
                                elif stat.get('abbreviation') == 'L':
                                    losses = int(stat.get('value', 0))
                        if wins > 0 or losses > 0:
                            total = wins + losses
                            team_records[team_name] = {
                                'wins': wins,
                                'losses': losses,
                                'record': f"{wins}-{losses}",
                                'win_pct': round(wins / total, 3) if total > 0 else 0
                            }
            return team_records
        except Exception as e:
            print(f"⚠️ {sport.upper()}: ESPN standings API error - {e}")
            return {}
    
    def fetch_espn_injuries_api(sport: str) -> Dict:
        """Fetch injury reports from ESPN API."""
        if sport not in espn_api_map or sport in ['ncaab', 'ncaaf']:
            return {}
        
        url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_api_map[sport]}/injuries"
        try:
            response = requests.get(url, headers=get_headers(), timeout=15)
            data = response.json()
            team_injuries = {}
            
            if 'injuries' in data:
                for team_data in data['injuries']:
                    team_name = team_data.get('team', {}).get('displayName', '')
                    injuries = []
                    for athlete in team_data.get('athletes', []):
                        player_name = athlete.get('athlete', {}).get('displayName', '')
                        status = athlete.get('status', 'Unknown')
                        desc = "No details"
                        if 'injuries' in athlete and athlete['injuries']:
                            desc = athlete['injuries'][0].get('detail', 'No details')
                        if player_name:
                            injuries.append({'name': player_name, 'status': status, 'description': desc})
                    if injuries and team_name:
                        team_injuries[team_name] = injuries
            return team_injuries
        except Exception as e:
            print(f"⚠️ {sport.upper()}: ESPN injuries API error - {e}")
            return {}
    
    def fetch_espn_results_api(sport: str) -> Dict:
        """Fetch recent game results from ESPN API."""
        if sport not in espn_api_map:
            return {}
        
        # Get games from last 3 days
        team_form = {}
        for day_offset in range(1, 4):
            date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y%m%d')
            url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_api_map[sport]}/scoreboard?dates={date}"
            try:
                response = requests.get(url, headers=get_headers(), timeout=10)
                data = response.json()
                if 'events' in data:
                    for event in data['events']:
                        if not event.get('status', {}).get('type', {}).get('completed', False):
                            continue
                        for comp in event.get('competitions', []):
                            for competitor in comp.get('competitors', []):
                                team_name = competitor.get('team', {}).get('displayName', '')
                                winner = competitor.get('winner', False)
                                if team_name:
                                    if team_name not in team_form:
                                        team_form[team_name] = {'last_5': []}
                                    team_form[team_name]['last_5'].append('W' if winner else 'L')
            except:
                continue
        
        # Format last 5 for each team
        for team, data in team_form.items():
            recent = data['last_5'][-5:] if len(data['last_5']) >= 5 else data['last_5']
            data['last_5_form'] = ''.join(recent)
            data['last_5_wins'] = recent.count('W')
        
        return team_form
    
    print(f"\n{'='*60}")
    print(f"🏃 YAHOO + ESPN SCRAPER STARTED")
    print(f"{'='*60}\n")
    
    dates = []
    for i in range(days_ahead):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        dates.append(date)
    
    for sport in SPORTS_CONFIG.keys():
        print(f"\n📊 Processing {sport.upper()}...")
        print("-" * 40)
        
        # Fetch ESPN data via API
        print(f"  ⏳ Fetching ESPN standings...")
        standings = fetch_espn_standings_api(sport)
        
        print(f"  ⏳ Fetching ESPN injuries...")
        injuries = fetch_espn_injuries_api(sport)
        
        print(f"  ⏳ Fetching ESPN recent results...")
        recent_form = fetch_espn_results_api(sport)
        
        # Fetch Yahoo odds
        all_games = []
        for date in dates:
            games = fetch_yahoo_odds(sport, date)
            all_games.extend(games)
        
        # Enrich games with ESPN data
        if all_games:
            enriched_games = []
            for game in all_games:
                home_team = game.get('home_team', '')
                away_team = game.get('away_team', '')
                
                # Find team data
                def find_team(team_name, data_dict):
                    if team_name in data_dict:
                        return data_dict[team_name]
                    for key in data_dict:
                        if team_name.lower() in key.lower() or key.lower() in team_name.lower():
                            return data_dict[key]
                    return {}
                
                # Add standings
                home_stand = find_team(home_team, standings)
                away_stand = find_team(away_team, standings)
                if home_stand:
                    game['home_record'] = home_stand.get('record', '0-0')
                    game['home_win_pct'] = home_stand.get('win_pct', 0)
                if away_stand:
                    game['away_record'] = away_stand.get('record', '0-0')
                    game['away_win_pct'] = away_stand.get('win_pct', 0)
                
                # Add injuries
                home_inj = find_team(home_team, injuries)
                away_inj = find_team(away_team, injuries)
                if home_inj:
                    game['home_injuries'] = home_inj
                    summary = '; '.join([f"{p['name']} ({p['status']})" for p in home_inj[:3]])
                    game['home_injuries_summary'] = summary or 'None reported'
                if away_inj:
                    game['away_injuries'] = away_inj
                    summary = '; '.join([f"{p['name']} ({p['status']})" for p in away_inj[:3]])
                    game['away_injuries_summary'] = summary or 'None reported'
                
                # Add recent form
                home_form = find_team(home_team, recent_form)
                away_form = find_team(away_team, recent_form)
                if home_form:
                    game['home_last_5'] = home_form.get('last_5_form', '')
                if away_form:
                    game['away_last_5'] = away_form.get('last_5_form', '')
                
                enriched_games.append(game)
            
            all_odds['sports'][sport] = enriched_games
            if enriched_games:
                sample = enriched_games[0]
                print(f"\n  ✅ Sample enriched game:")
                print(f"     • {sample.get('home_team', '?')} ({sample.get('home_record', 'N/A')}) vs")
                print(f"     • {sample.get('away_team', '?')} ({sample.get('away_record', 'N/A')})")
                if sample.get('home_injuries_summary'):
                    print(f"     • Home inj: {sample['home_injuries_summary']}")
    
    print(f"\n{'='*60}")
    print(f"✅ SCRAPING COMPLETE")
    print(f"{'='*60}\n")
    
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
