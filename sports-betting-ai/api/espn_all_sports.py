"""
ESPN API Client for ALL sports
Free, no authentication required
Supports: NBA, NFL, MLB, NHL
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st
import time

# ESPN API Base URLs
ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"
ESPN_CORE = "https://sports.core.api.espn.com/v2"

SPORT_CONFIG = {
    'NBA': {
        'path': 'basketball/nba',
        'season': 2026,
        'player_stats': ['points', 'rebounds', 'assists', 'fieldGoalsMade']
    },
    'NFL': {
        'path': 'football/nfl',
        'season': 2024,  # NFL uses different season numbering
        'player_stats': ['passingYards', 'rushingYards', 'receivingYards', 'receptions', 'passingTouchdowns', 'rushingTouchdowns', 'receivingTouchdowns']
    },
    'MLB': {
        'path': 'baseball/mlb',
        'season': 2026,
        'player_stats': ['hits', 'homeRuns', 'runsBattedIn', 'battingAverage', 'atBats']
    },
    'NHL': {
        'path': 'hockey/nhl',
        'season': 2026,
        'player_stats': ['goals', 'assists', 'points', 'shots']
    }
}


class ESPNSportsAPI:
    """
    Unified ESPN API client for all major sports
    Free, no API key required
    """
    
    def __init__(self, sport: str):
        self.sport = sport.upper()
        self.config = SPORT_CONFIG.get(self.sport)
        if not self.config:
            raise ValueError(f"Sport {sport} not supported. Use: NBA, NFL, MLB, NHL")
    
    def _make_request(self, url: str, retries: int = 2) -> Optional[Dict]:
        """Make API request with retry logic."""
        for attempt in range(retries + 1):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
                time.sleep(0.5 * (attempt + 1))
            except Exception as e:
                if attempt == retries:
                    return None
                time.sleep(0.5 * (attempt + 1))
        return None
    
    @st.cache_data(ttl=1800)  # 30 min cache
    def get_teams(_self) -> List[Dict]:
        """Get all teams for the sport."""
        url = f"{ESPN_BASE}/{_self.config['path']}/teams"
        data = _self._make_request(url)
        
        if not data or 'sports' not in data:
            return []
        
        teams = []
        try:
            for sport in data.get('sports', []):
                for league in sport.get('leagues', []):
                    for team in league.get('teams', []):
                        team_data = team.get('team', {})
                        teams.append({
                            'id': team_data.get('id'),
                            'name': team_data.get('name'),
                            'abbreviation': team_data.get('abbreviation'),
                            'displayName': team_data.get('displayName'),
                            'logo': team_data.get('logos', [{}])[0].get('href', '')
                        })
        except:
            pass
        
        return teams
    
    @st.cache_data(ttl=1800)
    def get_team_players(_self, team_id: int) -> List[Dict]:
        """Get roster for a specific team."""
        url = f"{ESPN_CORE}/sports/{_self.config['path']}/seasons/{_self.config['season']}/teams/{team_id}?enable=roster"
        data = _self._make_request(url)
        
        if not data:
            return []
        
        players = []
        try:
            roster = data.get('athletes', [])
            for group in roster if isinstance(roster, list) else []:
                if isinstance(group, dict) and 'items' in group:
                    for player in group.get('items', []):
                        players.append({
                            'id': player.get('id'),
                            'name': player.get('displayName'),
                            'position': player.get('position', {}).get('abbreviation', ''),
                            'jersey': player.get('jersey', ''),
                            'headshot': player.get('headshot', {}).get('href', '')
                        })
                elif isinstance(group, dict):
                    players.append({
                        'id': group.get('id'),
                        'name': group.get('displayName'),
                        'position': group.get('position', {}).get('abbreviation', ''),
                        'jersey': group.get('jersey', ''),
                        'headshot': group.get('headshot', {}).get('href', '')
                    })
        except Exception as e:
            pass
        
        return players
    
    @st.cache_data(ttl=3600)
    def get_player_stats(_self, player_id: int) -> Optional[Dict]:
        """Get season stats for a player."""
        url = f"{ESPN_CORE}/sports/{_self.config['path']}/seasons/{_self.config['season']}/athletes/{player_id}"
        data = _self._make_request(url)
        
        if not data:
            return None
        
        try:
            stats = data.get('statistics', {})
            
            if _self.sport == 'NBA':
                return _self._parse_nba_stats(stats)
            elif _self.sport == 'NFL':
                return _self._parse_nfl_stats(stats)
            elif _self.sport == 'MLB':
                return _self._parse_mlb_stats(stats)
            elif _self.sport == 'NHL':
                return _self._parse_nhl_stats(stats)
        except:
            pass
        
        return None
    
    def _parse_nba_stats(self, stats: Dict) -> Dict:
        """Parse NBA player stats."""
        result = {'ppg': 0, 'rpg': 0, 'apg': 0, 'games': 0}
        
        for stat_group in stats.get('$ref', []):
            if isinstance(stat_group, dict):
                for stat in stat_group.get('statistics', []):
                    name = stat.get('name', '')
                    value = stat.get('value', 0)
                    
                    if 'points' in name.lower():
                        result['ppg'] = round(value, 1)
                    elif 'rebounds' in name.lower():
                        result['rpg'] = round(value, 1)
                    elif 'assists' in name.lower():
                        result['apg'] = round(value, 1)
                    elif 'gamesPlayed' in name:
                        result['games'] = int(value)
        
        return result
    
    def _parse_nfl_stats(self, stats: Dict) -> Dict:
        """Parse NFL player stats."""
        result = {
            'pass_yds': 0, 'pass_td': 0, 'rush_yds': 0, 'rush_td': 0,
            'rec': 0, 'rec_yds': 0, 'rec_td': 0, 'games': 0
        }
        
        # NFL stats structure varies by position
        categories = stats.get('categories', [])
        for cat in categories:
            for stat in cat.get('stats', []):
                name = stat.get('name', '')
                value = stat.get('value', 0)
                
                if name == 'passingYards':
                    result['pass_yds'] = round(value, 1)
                elif name == 'passingTouchdowns':
                    result['pass_td'] = round(value, 1)
                elif name == 'rushingYards':
                    result['rush_yds'] = round(value, 1)
                elif name == 'rushingTouchdowns':
                    result['rush_td'] = round(value, 1)
                elif name == 'receptions':
                    result['rec'] = round(value, 1)
                elif name == 'receivingYards':
                    result['rec_yds'] = round(value, 1)
                elif name == 'receivingTouchdowns':
                    result['rec_td'] = round(value, 1)
                elif name == 'gamesPlayed':
                    result['games'] = int(value)
        
        return result
    
    def _parse_mlb_stats(self, stats: Dict) -> Dict:
        """Parse MLB player stats."""
        result = {'avg': 0, 'hr': 0, 'rbi': 0, 'hits': 0, 'games': 0}
        
        categories = stats.get('categories', [])
        for cat in categories:
            for stat in cat.get('stats', []):
                name = stat.get('name', '')
                value = stat.get('value', 0)
                
                if name == 'battingAverage':
                    result['avg'] = round(value, 3)
                elif name == 'homeRuns':
                    result['hr'] = round(value, 2)
                elif name == 'runsBattedIn':
                    result['rbi'] = round(value, 2)
                elif name == 'hits':
                    result['hits'] = round(value, 2)
                elif name == 'gamesPlayed':
                    result['games'] = int(value)
        
        return result
    
    def _parse_nhl_stats(self, stats: Dict) -> Dict:
        """Parse NHL player stats."""
        result = {'goals': 0, 'assists': 0, 'points': 0, 'shots': 0, 'games': 0}
        
        categories = stats.get('categories', [])
        for cat in categories:
            for stat in cat.get('stats', []):
                name = stat.get('name', '')
                value = stat.get('value', 0)
                
                if name == 'goals':
                    result['goals'] = round(value, 2)
                elif name == 'assists':
                    result['assists'] = round(value, 2)
                elif name == 'points':
                    result['points'] = round(value, 2)
                elif name == 'shots':
                    result['shots'] = round(value, 2)
                elif name == 'gamesPlayed':
                    result['games'] = int(value)
        
        return result
    
    @st.cache_data(ttl=1800)
    def get_all_players_with_stats(_self, limit_per_team: int = 5) -> pd.DataFrame:
        """Get top players with stats from all teams."""
        teams = _self.get_teams()
        all_players = []
        
        for team in teams[:10]:  # Limit to first 10 teams to avoid rate limits
            team_id = team.get('id')
            if not team_id:
                continue
            
            players = _self.get_team_players(team_id)
            
            for player in players[:limit_per_team]:
                player_id = player.get('id')
                if player_id:
                    stats = _self.get_player_stats(player_id)
                    if stats:
                        all_players.append({
                            'name': player.get('name'),
                            'team': team.get('name'),
                            'position': player.get('position'),
                            **stats
                        })
        
        return pd.DataFrame(all_players)


# Static fallback data (when ESPN API fails)
STATIC_FALLBACK = {
    'NBA': {
        'Lakers': [
            {'name': 'LeBron James', 'ppg': 25.2, 'rpg': 7.8, 'apg': 9.0},
            {'name': 'Anthony Davis', 'ppg': 24.8, 'rpg': 12.5, 'apg': 3.5},
        ],
        'Warriors': [
            {'name': 'Stephen Curry', 'ppg': 28.5, 'rpg': 4.4, 'apg': 5.1},
            {'name': 'Klay Thompson', 'ppg': 18.2, 'rpg': 3.5, 'apg': 2.3},
        ],
    },
    'NFL': {
        'Chiefs': [
            {'name': 'Patrick Mahomes', 'pass_yds': 272, 'pass_td': 2.1, 'rush_yds': 28},
            {'name': 'Travis Kelce', 'rec': 6.5, 'rec_yds': 78, 'rec_td': 0.7},
        ],
        '49ers': [
            {'name': 'Brock Purdy', 'pass_yds': 265, 'pass_td': 1.9, 'rush_yds': 18},
            {'name': 'Christian McCaffrey', 'rush': 18, 'rush_yds': 85, 'rush_td': 0.8, 'rec': 4.5},
        ],
    },
    'MLB': {
        'Dodgers': [
            {'name': 'Shohei Ohtani', 'avg': 0.304, 'hr': 0.28, 'rbi': 0.85},
            {'name': 'Mookie Betts', 'avg': 0.280, 'hr': 0.22, 'rbi': 0.72},
        ],
        'Yankees': [
            {'name': 'Aaron Judge', 'avg': 0.285, 'hr': 0.35, 'rbi': 0.95},
            {'name': 'Juan Soto', 'avg': 0.292, 'hr': 0.25, 'rbi': 0.82},
        ],
    },
    'NHL': {
        'Avalanche': [
            {'name': 'Nathan MacKinnon', 'goals': 0.52, 'assists': 0.88, 'points': 1.40, 'shots': 4.5},
            {'name': 'Cale Makar', 'goals': 0.28, 'assists': 0.72, 'points': 1.00, 'shots': 3.2},
        ],
        'Oilers': [
            {'name': 'Connor McDavid', 'goals': 0.55, 'assists': 1.05, 'points': 1.60, 'shots': 4.2},
            {'name': 'Leon Draisaitl', 'goals': 0.52, 'assists': 0.72, 'points': 1.24, 'shots': 3.5},
        ],
    }
}


def get_player_data_unified(sport: str, team: str = None, use_api: bool = True) -> List[Dict]:
    """
    Get player data for any sport.
    Tries ESPN API first, falls back to static data.
    """
    if use_api:
        try:
            api = ESPNSportsAPI(sport)
            
            if team:
                # Get team ID first
                teams = api.get_teams()
                team_id = None
                for t in teams:
                    if t.get('name') == team or t.get('abbreviation') == team:
                        team_id = t.get('id')
                        break
                
                if team_id:
                    players = api.get_team_players(team_id)
                    result = []
                    for player in players[:10]:  # Top 10 players
                        stats = api.get_player_stats(player.get('id'))
                        if stats:
                            result.append({
                                'name': player.get('name'),
                                **stats
                            })
                    if result:
                        return result
            else:
                # Get all players
                df = api.get_all_players_with_stats(limit_per_team=3)
                if not df.empty:
                    return df.to_dict('records')
        except Exception as e:
            pass
    
    # Fallback to static
    return STATIC_FALLBACK.get(sport, {}).get(team, [])


# Prop configurations per sport
PROP_CONFIG = {
    'NBA': {
        'props': ['Points', 'Rebounds', 'Assists', 'PRA'],
        'stat_map': {
            'Points': 'ppg',
            'Rebounds': 'rpg',
            'Assists': 'apg',
            'PRA': ['ppg', 'rpg', 'apg']
        }
    },
    'NFL': {
        'props': ['Pass Yards', 'Pass TDs', 'Rush Yards', 'Receptions', 'Rec Yards', 'Anytime TD'],
        'stat_map': {
            'Pass Yards': 'pass_yds',
            'Pass TDs': 'pass_td',
            'Rush Yards': 'rush_yds',
            'Receptions': 'rec',
            'Rec Yards': 'rec_yds',
            'Anytime TD': ['rush_td', 'rec_td']
        }
    },
    'MLB': {
        'props': ['Hits', 'Home Runs', 'RBIs'],
        'stat_map': {
            'Hits': 'hits',
            'Home Runs': 'hr',
            'RBIs': 'rbi'
        }
    },
    'NHL': {
        'props': ['Goals', 'Assists', 'Points', 'Shots'],
        'stat_map': {
            'Goals': 'goals',
            'Assists': 'assists',
            'Points': 'points',
            'Shots': 'shots'
        }
    }
}
