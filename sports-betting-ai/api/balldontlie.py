"""
BallDontLie API Client - Free NBA data with player stats, games, and advanced metrics
No API key required - https://www.balldontlie.io/
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class BallDontLieAPI:
    """Free NBA data API covering teams, players, games, and stats."""
    
    BASE_URL = "https://api.balldontlie.io/v1"
    
    def __init__(self):
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_teams(self) -> pd.DataFrame:
        """Get all NBA teams."""
        data = self._make_request("teams")
        teams = []
        for team in data.get('data', []):
            teams.append({
                'id': team.get('id'),
                'abbreviation': team.get('abbreviation'),
                'city': team.get('city'),
                'conference': team.get('conference'),
                'division': team.get('division'),
                'full_name': team.get('full_name'),
                'name': team.get('name')
            })
        return pd.DataFrame(teams)
    
    def get_players(self, team_id: Optional[int] = None, per_page: int = 100) -> pd.DataFrame:
        """Get players, optionally filtered by team."""
        params = {'per_page': per_page}
        if team_id:
            params['team_ids'] = [team_id]
        
        data = self._make_request("players", params)
        players = []
        for player in data.get('data', []):
            players.append({
                'id': player.get('id'),
                'first_name': player.get('first_name'),
                'last_name': player.get('last_name'),
                'position': player.get('position'),
                'height': player.get('height'),
                'weight': player.get('weight'),
                'team_id': player.get('team', {}).get('id') if player.get('team') else None,
                'team_name': player.get('team', {}).get('name') if player.get('team') else None
            })
        return pd.DataFrame(players)
    
    def get_games(self, team_ids: List[int] = None, 
                  start_date: str = None, 
                  end_date: str = None,
                  per_page: int = 100) -> pd.DataFrame:
        """Get games with optional filters."""
        params = {'per_page': per_page}
        if team_ids:
            params['team_ids'] = team_ids
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        data = self._make_request("games", params)
        games = []
        for game in data.get('data', []):
            games.append({
                'id': game.get('id'),
                'date': game.get('date'),
                'season': game.get('season'),
                'home_team_id': game.get('home_team', {}).get('id'),
                'home_team_name': game.get('home_team', {}).get('name'),
                'home_team_score': game.get('home_team_score'),
                'visitor_team_id': game.get('visitor_team', {}).get('id'),
                'visitor_team_name': game.get('visitor_team', {}).get('name'),
                'visitor_team_score': game.get('visitor_team_score'),
                'home_team_win': game.get('home_team_score', 0) > game.get('visitor_team_score', 0) if game.get('home_team_score') else None,
                'period': game.get('period'),
                'status': game.get('status'),
                'time': game.get('time')
            })
        return pd.DataFrame(games)
    
    def get_team_stats(self, team_id: int, season: int = 2024) -> pd.DataFrame:
        """Get team statistics for a season."""
        params = {'team_ids': [team_id], 'seasons': [season]}
        data = self._make_request("stats", params)
        stats = []
        for stat in data.get('data', []):
            stats.append({
                'team_id': team_id,
                'season': season,
                'games_played': stat.get('games_played'),
                'wins': stat.get('wins'),
                'losses': stat.get('losses'),
                'win_pct': stat.get('wins', 0) / stat.get('games_played', 1) if stat.get('games_played') else 0,
                'points_scored': stat.get('points_scored'),
                'points_allowed': stat.get('points_allowed'),
                'field_goal_pct': stat.get('field_goal_pct'),
                'three_point_pct': stat.get('three_point_pct'),
                'free_throw_pct': stat.get('free_throw_pct'),
                'rebounds': stat.get('rebounds'),
                'assists': stat.get('assists'),
                'steals': stat.get('steals'),
                'blocks': stat.get('blocks'),
                'turnovers': stat.get('turnovers'),
                'personal_fouls': stat.get('personal_fouls')
            })
        return pd.DataFrame(stats)
    
    def get_player_stats(self, player_ids: List[int] = None,
                         game_ids: List[int] = None,
                         per_page: int = 100) -> pd.DataFrame:
        """Get player statistics."""
        params = {'per_page': per_page}
        if player_ids:
            params['player_ids'] = player_ids
        if game_ids:
            params['game_ids'] = game_ids
            
        data = self._make_request("stats", params)
        stats = []
        for stat in data.get('data', []):
            stats.append({
                'player_id': stat.get('player', {}).get('id'),
                'player_name': f"{stat.get('player', {}).get('first_name', '')} {stat.get('player', {}).get('last_name', '')}",
                'team_id': stat.get('team', {}).get('id'),
                'game_id': stat.get('game', {}).get('id'),
                'minutes': stat.get('min'),
                'points': stat.get('pts'),
                'rebounds': stat.get('reb'),
                'assists': stat.get('ast'),
                'steals': stat.get('stl'),
                'blocks': stat.get('blk'),
                'turnovers': stat.get('turnover'),
                'field_goals_made': stat.get('fgm'),
                'field_goals_attempted': stat.get('fga'),
                'fg_pct': stat.get('fg_pct'),
                'three_points_made': stat.get('fg3m'),
                'three_points_attempted': stat.get('fg3a'),
                'three_pct': stat.get('fg3_pct'),
                'free_throws_made': stat.get('ftm'),
                'free_throws_attempted': stat.get('fta'),
                'ft_pct': stat.get('ft_pct')
            })
        return pd.DataFrame(stats)
    
    def get_season_averages(self, player_ids: List[int], season: int = 2024) -> pd.DataFrame:
        """Get season averages for players."""
        params = {'player_ids': player_ids, 'season': season}
        data = self._make_request("season_averages", params)
        return pd.DataFrame(data.get('data', []))
    
    def get_injuries(self) -> pd.DataFrame:
        """Get current player injuries - Note: This endpoint may not exist in free tier."""
        # BallDontLie doesn't have direct injury endpoint
        # Return empty DataFrame, use ESPN for injuries
        return pd.DataFrame()

if __name__ == "__main__":
    api = BallDontLieAPI()
    teams = api.get_teams()
    print(f"Loaded {len(teams)} NBA teams")
    print(teams.head())
