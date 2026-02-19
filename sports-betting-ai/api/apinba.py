"""
API-NBA Client - Free NBA data with player/stats/injuries
Get free key at: https://rapidapi.com/callmebono/api/sports-live-scores/ or similar
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
import os

class APIBasketball:
    """Free NBA data API with player stats, injuries, advanced metrics."""
    
    BASE_URL = "https://api-nba-v1.p.rapidapi.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        if not self.api_key:
            raise ValueError("RapidAPI key required")
        self.session = requests.Session()
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
        }
    
    def get_teams(self) -> pd.DataFrame:
        """Get all NBA teams."""
        url = f"{self.BASE_URL}/teams"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        teams = [team['team'] for team in data.get('response', [])]
        return pd.DataFrame(teams)
    
    def get_games(self, season: int = 2026) -> pd.DataFrame:
        """Get games for a season."""
        url = f"{self.BASE_URL}/games"
        params = {"season": season}
        response = self.session.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        games = []
        for game in data.get('response', []):
            games.append({
                'game_id': game.get('id'),
                'date': game.get('date', {}).get('start'),
                'home_team_id': game.get('teams', {}).get('home', {}).get('id'),
                'home_team': game.get('teams', {}).get('home', {}).get('name'),
                'home_score': game.get('scores', {}).get('home', {}).get('points'),
                'away_team_id': game.get('teams', {}).get('visitors', {}).get('id'),
                'away_team': game.get('teams', {}).get('visitors', {}).get('name'),
                'away_score': game.get('scores', {}).get('visitors', {}).get('points'),
                'home_winner': game.get('scores', {}).get('home', {}).get('win'),
                'season': season
            })
        return pd.DataFrame(games)
    
    def get_team_statistics(self, team_id: int, season: int = 2026) -> pd.DataFrame:
        """Get advanced team statistics."""
        url = f"{self.BASE_URL}/teams/statistics"
        params = {"id": team_id, "season": season}
        response = self.session.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get('response'):
            return pd.DataFrame([data['response']])
        return pd.DataFrame()
    
    def get_player_statistics(self, game_id: int) -> pd.DataFrame:
        """Get player stats for a game."""
        url = f"{self.BASE_URL}/players/statistics"
        params = {"game": game_id}
        response = self.session.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        players = []
        for player in data.get('response', []):
            players.append({
                'player_id': player.get('player', {}).get('id'),
                'player_name': player.get('player', {}).get('name'),
                'team_id': player.get('team', {}).get('id'),
                'points': player.get('points'),
                'assists': player.get('assists'),
                'rebounds': player.get('totReb'),
                'minutes': player.get('min'),
                'fg_pct': player.get('fgp'),
                '3p_pct': player.get('tpp'),
                'ft_pct': player.get('ftp')
            })
        return pd.DataFrame(players)
    
    def get_injuries(self) -> pd.DataFrame:
        """Get current player injuries."""
        url = f"{self.BASE_URL}/injuries"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        injuries = []
        for injury in data.get('response', []):
            injuries.append({
                'player_id': injury.get('player', {}).get('id'),
                'player_name': injury.get('player', {}).get('name'),
                'team_id': injury.get('team', {}).get('id'),
                'team_name': injury.get('team', {}).get('name'),
                'status': injury.get('status'),
                'description': injury.get('description')
            })
        return pd.DataFrame(injuries)

if __name__ == "__main__":
    key = os.getenv('RAPIDAPI_KEY', 'YOUR_KEY')
    api = APIBasketball(key)
    teams = api.get_teams()
    print(f"Loaded {len(teams)} teams")
