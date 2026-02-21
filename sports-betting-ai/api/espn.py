"""
ESPN API Client - Free sports data for NBA, NFL, MLB, NHL
No API key required - Enhanced with caching and error handling
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

SPORT_ENDPOINTS = {
    'nba': 'basketball/nba',
    'nfl': 'football/nfl',
    'mlb': 'baseball/mlb',
    'nhl': 'hockey/nhl',
    'ncaab': 'basketball/mens-college-basketball',
    'ncaaf': 'football/college-football'
}


def get_session():
    """Create a requests session with proper headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    return session


@st.cache_data(ttl=300)
def _fetch_teams(sport: str) -> pd.DataFrame:
    """Internal cached function to fetch teams."""
    endpoint = SPORT_ENDPOINTS.get(sport.lower())
    if not endpoint:
        return pd.DataFrame(columns=['id', 'name', 'abbreviation', 'location', 'record'])
    
    url = f"{BASE_URL}/{endpoint}/teams"
    session = get_session()
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        teams = []
        
        sports_data = data.get('sports', [{}])
        if not sports_data:
            return pd.DataFrame(columns=['id', 'name', 'abbreviation', 'location', 'record'])
        
        leagues = sports_data[0].get('leagues', [{}])
        if not leagues:
            return pd.DataFrame(columns=['id', 'name', 'abbreviation', 'location', 'record'])
        
        for team in leagues[0].get('teams', []):
            team_data = team.get('team', {})
            teams.append({
                'id': team_data.get('id'),
                'name': team_data.get('name'),
                'abbreviation': team_data.get('abbreviation'),
                'location': team_data.get('location'),
                'record': team_data.get('record', {}).get('summary', '0-0')
            })
        
        return pd.DataFrame(teams)
    except Exception as e:
        return pd.DataFrame(columns=['id', 'name', 'abbreviation', 'location', 'record'])


@st.cache_data(ttl=300)
def _fetch_schedule(sport: str, days: int = 7) -> pd.DataFrame:
    """Internal cached function to fetch schedule."""
    endpoint = SPORT_ENDPOINTS.get(sport.lower())
    if not endpoint:
        return pd.DataFrame(columns=['id', 'name', 'date', 'home_team', 'away_team', 'home_record', 'away_record'])
    
    url = f"{BASE_URL}/{endpoint}/scoreboard"
    params = {'limit': 100, 'days': days}
    session = get_session()
    
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        games = []
        
        for event in data.get('events', []):
            competitions = event.get('competitions', [])
            if not competitions:
                continue
            
            comp = competitions[0]
            competitors = comp.get('competitors', [])
            if len(competitors) < 2:
                continue
            
            # Skip games that have already finished
            status = event.get('status', {}).get('type', {}).get('description', '').lower()
            if status in ['final', 'post', 'ended', 'completed']:
                continue
            
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
            
            game_date = event.get('date', '')
            if game_date:
                try:
                    game_date = datetime.fromisoformat(game_date.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                except:
                    game_date = game_date[:16].replace('T', ' ')
            
            games.append({
                'id': event.get('id'),
                'name': event.get('name', ''),
                'date': game_date,
                'home_team': home_team.get('team', {}).get('name', 'TBD'),
                'away_team': away_team.get('team', {}).get('name', 'TBD'),
                'home_record': home_team.get('records', [{}])[0].get('summary', '0-0') if home_team else '0-0',
                'away_record': away_team.get('records', [{}])[0].get('summary', '0-0') if away_team else '0-0'
            })
        
        return pd.DataFrame(games)
    except Exception as e:
        return pd.DataFrame(columns=['id', 'name', 'date', 'home_team', 'away_team', 'home_record', 'away_record'])


@st.cache_data(ttl=3600)
def _fetch_team_stats(sport: str, team_name: str) -> Dict:
    """Fetch team statistics from ESPN - using available data."""
    try:
        # Get basic team info which includes record
        teams_df = _fetch_teams(sport)
        if teams_df.empty:
            return _get_default_team_stats(team_name)
        
        team_row = teams_df[teams_df['name'].str.contains(team_name, case=False, na=False)]
        if team_row.empty:
            return _get_default_team_stats(team_name)
        
        # Get the record and calculate basic stats
        record = team_row.iloc[0]['record']
        
        # Parse record (e.g., "35-15" or "28-27-2" for NHL)
        if '-' in str(record):
            parts = str(record).split('-')
            if len(parts) >= 2:
                wins = int(parts[0])
                losses = int(parts[1])
                total_games = wins + losses
                
                # Calculate win percentage
                win_pct = wins / total_games if total_games > 0 else 0
                
                return {
                    'team_name': team_row.iloc[0]['name'],
                    'record': record,
                    'wins': wins,
                    'losses': losses,
                    'win_pct': f"{win_pct*100:.1f}%",
                    'ppg': 'N/A',  # Not available from ESPN basic API
                    'papg': 'N/A',
                    'fg_pct': 'N/A',
                    'three_pct': 'N/A',
                    'rpg': 'N/A',
                    'apg': 'N/A',
                    'form': f"{wins}-{losses} ({win_pct*100:.0f}%)",
                    'top_scorer': {'name': 'View ESPN', 'ppg': 'Full Stats'}
                }
        
        return {
            'team_name': team_row.iloc[0]['name'],
            'record': record,
            'wins': 0,
            'losses': 0,
            'win_pct': 'N/A',
            'ppg': 'N/A',
            'papg': 'N/A',
            'fg_pct': 'N/A',
            'three_pct': 'N/A',
            'rpg': 'N/A',
            'apg': 'N/A',
            'form': record,
            'top_scorer': {'name': 'N/A', 'ppg': 'N/A'}
        }
        
    except Exception as e:
        return _get_default_team_stats(team_name)


def _parse_sport_stats(sport: str, data: Dict) -> Dict:
    """Parse stats based on sport type."""
    stats = {}
    
    # Generic stat parsing
    for category in data.get('splits', {}).get('categories', []):
        cat_name = category.get('displayName', '').lower()
        
        for stat in category.get('stats', []):
            name = stat.get('displayName', '')
            value = stat.get('value', 0)
            
            # Common stats across sports
            if 'points' in name.lower() or 'runs' in name.lower() or 'goals' in name.lower():
                stats['ppg'] = round(value, 1) if isinstance(value, (int, float)) else value
            elif 'allowed' in name.lower() or 'against' in name.lower():
                stats['papg'] = round(value, 1) if isinstance(value, (int, float)) else value
            elif 'field goal' in name.lower() or 'shooting' in name.lower():
                stats['fg_pct'] = round(value * 100, 1) if value < 1 else round(value, 1)
            elif 'three' in name.lower() or '3-pt' in name.lower():
                stats['three_pct'] = round(value * 100, 1) if value < 1 else round(value, 1)
            elif 'rebound' in name.lower():
                stats['rpg'] = round(value, 1)
            elif 'assist' in name.lower():
                stats['apg'] = round(value, 1)
    
    if not stats:
        return _get_default_team_stats('')
    
    return stats


def _get_default_team_stats(team_name: str) -> Dict:
    """Return default team stats when API fails."""
    return {
        'team_name': team_name,
        'record': 'N/A',
        'ppg': 'N/A',
        'papg': 'N/A',
        'fg_pct': 'N/A',
        'three_pct': 'N/A',
        'rpg': 'N/A',
        'apg': 'N/A',
        'top_scorer': {'name': 'N/A', 'ppg': 'N/A'},
        'form': 'N/A'
    }


@st.cache_data(ttl=3600)
def _fetch_player_leaders(sport: str, stat: str = 'points') -> List[Dict]:
    """Fetch league leaders for a stat category."""
    endpoint = SPORT_ENDPOINTS.get(sport.lower())
    if not endpoint:
        return []
    
    try:
        # ESPN stats leaders endpoint
        url = f"{BASE_URL}/{endpoint}/leaders"
        params = {'limit': 5}
        session = get_session()
        response = session.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        leaders = []
        
        for category in data.get('categories', []):
            if stat.lower() in category.get('displayName', '').lower():
                for leader in category.get('leaders', [])[:3]:
                    athlete = leader.get('athlete', {})
                    leaders.append({
                        'name': athlete.get('displayName', 'N/A'),
                        'team': athlete.get('team', {}).get('name', 'N/A'),
                        'stat': leader.get('value', 0),
                        'rank': leader.get('rank', 0)
                    })
        
        return leaders
    except:
        return []


class ESPNAPI:
    """Client for ESPN's public API endpoints - now with working caching!"""
    
    def __init__(self):
        self.session = get_session()
    
    def get_teams(self, sport: str) -> pd.DataFrame:
        """Get all teams for a sport with caching."""
        return _fetch_teams(sport)
    
    def get_schedule(self, sport: str, days: int = 7) -> pd.DataFrame:
        """Get upcoming games with caching."""
        return _fetch_schedule(sport, days)
    
    def get_team_stats(self, sport: str, team_name: str) -> Dict:
        """Get detailed team stats for a specific team."""
        return _fetch_team_stats(sport, team_name)
    
    def get_player_leaders(self, sport: str, stat: str = 'points') -> List[Dict]:
        """Get league scoring leaders."""
        return _fetch_player_leaders(sport, stat)
