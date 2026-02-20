"""
MySportsFeeds API Client
Free tier available for non-commercial use
Covers: NBA, NFL, MLB, NHL
"""

import requests
import base64
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st

# Get API key from Streamlit secrets
try:
    import streamlit as st
    API_KEY = st.secrets.get("MYSPORTSFEEDS_API_KEY", "")
except:
    API_KEY = ""

BASE_URL = "https://api.mysportsfeeds.com/v2.1/pull"


class MySportsFeedsAPI:
    """
    MySportsFeeds client for all sports
    Free tier: 500 calls/day
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("MySportsFeeds API key required. Get free key at mysportsfeeds.com/register")
        
        # Create auth header (username:password where password is API key)
        auth_str = f"{self.api_key}:MYSPORTSFEEDS"
        self.auth_header = base64.b64encode(auth_str.encode()).decode()
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated API request."""
        url = f"{BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Basic {self.auth_header}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                st.error("MySportsFeeds rate limit reached (500/day free tier)")
                return None
            else:
                return None
        except Exception as e:
            return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _fetch_seasonal_player_stats(_self, sport: str, season: str, season_type: str) -> pd.DataFrame:
        """Fetch cumulative seasonal player stats."""
        endpoint = f"{sport}/{season}/{season_type}/player_stats_totals.json"
        data = _self._make_request(endpoint)
        
        if not data or 'playerStatsTotals' not in data:
            return pd.DataFrame()
        
        players = []
        for player_data in data['playerStatsTotals']:
            player = player_data.get('player', {})
            team = player_data.get('team', {})
            stats = player_data.get('stats', {})
            
            # Build player record
            record = {
                'id': player.get('id'),
                'firstName': player.get('firstName'),
                'lastName': player.get('lastName'),
                'fullName': f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
                'position': player.get('primaryPosition'),
                'team': team.get('abbreviation'),
                'teamName': team.get('name'),
            }
            
            # Add sport-specific stats
            record.update(_self._parse_stats(sport, stats))
            players.append(record)
        
        return pd.DataFrame(players)
    
    def _parse_stats(self, sport: str, stats: Dict) -> Dict:
        """Parse stats based on sport."""
        result = {}
        
        if sport == 'nba':
            totals = stats.get('offense', {})
            games = stats.get('gamesPlayed', 1)
            result = {
                'games': games,
                'ppg': round(totals.get('pts', 0) / max(games, 1), 1),
                'rpg': round(totals.get('reb', 0) / max(games, 1), 1),
                'apg': round(totals.get('ast', 0) / max(games, 1), 1),
                'fg_pct': round(totals.get('fgAtt', 0) / max(totals.get('fgMade', 1) * 2, 1), 3),
                'fg2': totals.get('fg2Made', 0),
                'fg3': totals.get('fg3Made', 0),
                'ft': totals.get('ftMade', 0),
                'minutes': totals.get('min', 0),
            }
        
        elif sport == 'nfl':
            # QB stats
            passing = stats.get('passing', {})
            rushing = stats.get('rushing', {})
            receiving = stats.get('receiving', {})
            games = stats.get('gamesPlayed', 1)
            
            result = {
                'games': games,
                'pass_yds_total': passing.get('passYards', 0),
                'pass_td_total': passing.get('passTD', 0),
                'pass_int': passing.get('int', 0),
                'pass_yds_pg': round(passing.get('passYards', 0) / max(games, 1), 1),
                'pass_td_pg': round(passing.get('passTD', 0) / max(games, 1), 1),
                'rush_yds_total': rushing.get('rushYards', 0),
                'rush_td_total': rushing.get('rushTD', 0),
                'rush_yds_pg': round(rushing.get('rushYards', 0) / max(games, 1), 1),
                'rec_total': receiving.get('receptions', 0),
                'rec_yds_total': receiving.get('recYards', 0),
                'rec_td_total': receiving.get('recTD', 0),
                'rec_pg': round(receiving.get('receptions', 0) / max(games, 1), 1),
                'rec_yds_pg': round(receiving.get('recYards', 0) / max(games, 1), 1),
            }
        
        elif sport == 'mlb':
            hitting = stats.get('hitting', {})
            games = hitting.get('gamesPlayed', 1)
            
            result = {
                'games': games,
                'avg': round(hitting.get('avg', 0), 3),
                'hr': hitting.get('homeruns', 0),
                'rbi': hitting.get('runsBattedIn', 0),
                'hits': hitting.get('hits', 0),
                'doubles': hitting.get('secondBaseHits', 0),
                'triples': hitting.get('thirdBaseHits', 0),
                'runs': hitting.get('runs', 0),
                'sb': hitting.get('stolenBases', 0),
                'ab': hitting.get('atBats', 0),
                'obp': round(hitting.get('onBasePercentage', 0), 3),
                'slg': round(hitting.get('slugPercentage', 0), 3),
                'tb': hitting.get('totalBases', 0),
            }
        
        elif sport == 'nhl':
            totals = stats.get('scoring', {})
            games = stats.get('gamesPlayed', 1)
            
            result = {
                'games': games,
                'goals': totals.get('goals', 0),
                'assists': totals.get('assists', 0),
                'points': totals.get('points', 0),
                'shots': totals.get('shots', 0),
                'goals_pg': round(totals.get('goals', 0) / max(games, 1), 2),
                'assists_pg': round(totals.get('assists', 0) / max(games, 1), 2),
                'points_pg': round(totals.get('points', 0) / max(games, 1), 2),
                'shots_pg': round(totals.get('shots', 0) / max(games, 1), 2),
                'plus_minus': totals.get('plusMinus', 0),
                'pim': totals.get('penaltyMinutes', 0),
            }
        
        return result
    
    def get_players_by_team(self, sport: str, team_abbr: str, season: str = "2025-2026") -> pd.DataFrame:
        """Get all players for a specific team."""
        season_type = "regular" if sport != 'nfl' else "regular"
        df = self._fetch_seasonal_player_stats(sport, season, season_type)
        
        if df.empty:
            return df
        
        return df[df['team'] == team_abbr] if team_abbr else df
    
    def get_player_props(self, sport: str, prop_type: str, team_abbr: str = None, limit: int = 20) -> pd.DataFrame:
        """Get player props for betting."""
        season_map = {
            'nba': '2025-2026',
            'nfl': '2024-2025',
            'mlb': '2025-2026',
            'nhl': '2025-2026'
        }
        
        df = self._fetch_seasonal_player_stats(sport, season_map.get(sport, '2025-2026'), 'regular')
        
        if df.empty:
            return df
        
        # Filter by team if specified
        if team_abbr:
            df = df[df['team'] == team_abbr]
        
        # Add prop lines (95% of season average)
        df = self._add_prop_lines(df, sport, prop_type)
        
        return df.head(limit)
    
    def _add_prop_lines(self, df: pd.DataFrame, sport: str, prop_type: str) -> pd.DataFrame:
        """Calculate prop lines based on sport and prop type."""
        
        if sport == 'nba':
            if prop_type == 'Points':
                df['prop_line'] = (df['ppg'] * 0.95).round(1)
                df['prop_avg'] = df['ppg']
            elif prop_type == 'Rebounds':
                df['prop_line'] = (df['rpg'] * 0.95).round(1)
                df['prop_avg'] = df['rpg']
            elif prop_type == 'Assists':
                df['prop_line'] = (df['apg'] * 0.95).round(1)
                df['prop_avg'] = df['apg']
            elif prop_type == 'PRA':
                df['prop_avg'] = df['ppg'] + df['rpg'] + df['apg']
                df['prop_line'] = (df['prop_avg'] * 0.95).round(1)
        
        elif sport == 'nfl':
            if prop_type == 'Pass Yards':
                df['prop_line'] = (df['pass_yds_pg'] * 0.95).round()
                df['prop_avg'] = df['pass_yds_pg']
            elif prop_type == 'Pass TDs':
                df['prop_line'] = (df['pass_td_pg'] * 0.95).round(1)
                df['prop_avg'] = df['pass_td_pg']
            elif prop_type == 'Rush Yards':
                df['prop_line'] = (df['rush_yds_pg'] * 0.95).round()
                df['prop_avg'] = df['rush_yds_pg']
            elif prop_type == 'Receptions':
                df['prop_line'] = (df['rec_pg'] * 0.95).round(1)
                df['prop_avg'] = df['rec_pg']
            elif prop_type == 'Rec Yards':
                df['prop_line'] = (df['rec_yds_pg'] * 0.95).round()
                df['prop_avg'] = df['rec_yds_pg']
        
        elif sport == 'mlb':
            if prop_type == 'Hits':
                df['prop_line'] = df['avg']  # Batting average as proxy
                df['prop_avg'] = df['avg']
            elif prop_type == 'Home Runs':
                df['prop_line'] = (df['hr'] / df['games'] * 0.95).round(2)
                df['prop_avg'] = (df['hr'] / df['games']).round(2)
            elif prop_type == 'RBIs':
                df['prop_line'] = (df['rbi'] / df['games'] * 0.95).round(2)
                df['prop_avg'] = (df['rbi'] / df['games']).round(2)
        
        elif sport == 'nhl':
            if prop_type == 'Goals':
                df['prop_line'] = (df['goals_pg'] * 0.95).round(2)
                df['prop_avg'] = df['goals_pg']
            elif prop_type == 'Assists':
                df['prop_line'] = (df['assists_pg'] * 0.95).round(2)
                df['prop_avg'] = df['assists_pg']
            elif prop_type == 'Points':
                df['prop_line'] = (df['points_pg'] * 0.95).round(2)
                df['prop_avg'] = df['points_pg']
            elif prop_type == 'Shots':
                df['prop_line'] = (df['shots_pg'] * 0.95).round(1)
                df['prop_avg'] = df['shots_pg']
        
        # Calculate over probability
        df['over_prob'] = df.apply(
            lambda row: min(0.90, max(0.10, 0.5 + (row['prop_avg'] - row['prop_line']) / max(row['prop_line'] * 0.2, 2))),
            axis=1
        )
        
        return df


# Backwards compatibility and unified interface
def get_mysportsfeeds_client(api_key: str = None) -> MySportsFeedsAPI:
    """Get MySportsFeeds client with API key."""
    return MySportsFeedsAPI(api_key=api_key)


# Default sport configurations
SPORT_CONFIG = {
    'nba': {
        'name': 'NBA',
        'season': '2025-2026',
        'props': ['Points', 'Rebounds', 'Assists', 'PRA'],
        'teams': ['LAL', 'GSW', 'BOS', 'DEN', 'PHX', 'MIL', 'DAL', 'MIA', 'NYK', 'PHI']
    },
    'nfl': {
        'name': 'NFL',
        'season': '2024-2025',
        'props': ['Pass Yards', 'Pass TDs', 'Rush Yards', 'Receptions', 'Rec Yards', 'Anytime TD'],
        'teams': ['KC', 'SF', 'BAL', 'BUF', 'PHI', 'DAL', 'MIA', 'DET', 'CLE', 'CIN']
    },
    'mlb': {
        'name': 'MLB',
        'season': '2025-2026',
        'props': ['Hits', 'Home Runs', 'RBIs'],
        'teams': ['LAD', 'NYY', 'ATL', 'HOU', 'PHI', 'TEX', 'TOR', 'BAL', 'TB', 'ARI']
    },
    'nhl': {
        'name': 'NHL',
        'season': '2025-2026',
        'props': ['Goals', 'Assists', 'Points', 'Shots'],
        'teams': ['COL', 'NYR', 'EDM', 'TOR', 'DAL', 'CAR', 'FLA', 'VGK', 'BOS', 'TB']
    }
}
