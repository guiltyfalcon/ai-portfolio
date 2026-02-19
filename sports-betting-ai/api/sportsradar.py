"""
SportsRadar API Client - Premium sports data
Requires API key from developer.sportradar.com
Trial: 60 days, 1000 calls/month, 1 call/sec
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
import os

class SportsRadarAPI:
    """Client for SportsRadar API - comprehensive sports data."""
    
    BASE_URL = "https://api.sportradar.us"
    
    SPORT_KEYS = {
        'nba': {'version': 'v7', 'league': 'nba'},
        'nfl': {'version': 'v7', 'league': 'nfl'},
        'mlb': {'version': 'v7', 'league': 'mlb'},
        'nhl': {'version': 'v7', 'league': 'nhl'}
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SPORTSRADAR_API_KEY')
        if not self.api_key:
            raise ValueError("SportsRadar API key required")
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str) -> Dict:
        """Make authenticated API request."""
        url = f"{self.BASE_URL}/{endpoint}?api_key={self.api_key}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_schedule(self, sport: str, year: int = 2026, season: str = 'reg') -> pd.DataFrame:
        """Get schedule for a sport."""
        sport_info = self.SPORT_KEYS.get(sport.lower())
        if not sport_info:
            raise ValueError(f"Sport {sport} not supported")
        
        endpoint = f"{sport_info['league']}-{sport_info['version']}/games/{year}/{season}/schedule.json"
        data = self._make_request(endpoint)
        
        games = []
        for game in data.get('games', []):
            games.append({
                'game_id': game.get('id'),
                'scheduled': game.get('scheduled'),
                'home_team': game.get('home', {}).get('name'),
                'home_team_id': game.get('home', {}).get('id'),
                'away_team': game.get('away', {}).get('name'),
                'away_team_id': game.get('away', {}).get('id'),
                'venue': game.get('venue', {}).get('name'),
                'status': game.get('status')
            })
        
        return pd.DataFrame(games)
    
    def get_team_stats(self, sport: str, team_id: str, season: str = '2025') -> pd.DataFrame:
        """Get team season statistics."""
        sport_info = self.SPORT_KEYS.get(sport.lower())
        endpoint = f"{sport_info['league']}-{sport_info['version']}/teams/{team_id}/statistics.json"
        data = self._make_request(endpoint)
        return pd.DataFrame([data.get('statistics', {})])
    
    def get_player_injuries(self, sport: str) -> pd.DataFrame:
        """Get current player injuries."""
        sport_info = self.SPORT_KEYS.get(sport.lower())
        endpoint = f"{sport_info['league']}-{sport_info['version']}/injuries.json"
        data = self._make_request(endpoint)
        
        injuries = []
        for player in data.get('injuries', []):
            injuries.append({
                'player_id': player.get('id'),
                'player_name': player.get('full_name'),
                'team_id': player.get('team', {}).get('id'),
                'team_name': player.get('team', {}).get('name'),
                'injury_type': player.get('injury_type'),
                'status': player.get('status'),
                'start_date': player.get('start_date')
            })
        
        return pd.DataFrame(injuries)

if __name__ == "__main__":
    # Test with trial key
    api_key = os.getenv('SPORTSRADAR_API_KEY', 'YOUR_TRIAL_KEY')
    sr = SportsRadarAPI(api_key)
    print("SportsRadar API ready (requires valid key)")
