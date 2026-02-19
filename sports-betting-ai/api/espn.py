"""
ESPN API Client - Free sports data for NBA, NFL, MLB, NHL
No API key required
"""

import requests
import pandas as pd
from typing import Dict, List, Optional

class ESPNAPI:
    """Client for ESPN's public API endpoints."""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    SPORT_ENDPOINTS = {
        'nba': 'basketball/nba',
        'nfl': 'football/nfl',
        'mlb': 'baseball/mlb',
        'nhl': 'hockey/nhl'
    }
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_teams(self, sport: str) -> pd.DataFrame:
        """Get all teams for a sport."""
        endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{self.BASE_URL}/{endpoint}/teams"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        teams = []
        
        for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
            team_data = team.get('team', {})
            teams.append({
                'id': team_data.get('id'),
                'name': team_data.get('name'),
                'abbreviation': team_data.get('abbreviation'),
                'location': team_data.get('location'),
                'record': team_data.get('record', {}).get('summary', '0-0')
            })
        
        return pd.DataFrame(teams)
    
    def get_schedule(self, sport: str, days: int = 7) -> pd.DataFrame:
        """Get upcoming games for a sport."""
        endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{self.BASE_URL}/{endpoint}/scoreboard"
        params = {'limit': 100, 'days': days}
        
        response = self.session.get(url, params=params)
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
            
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
            
            games.append({
                'game_id': event.get('id'),
                'date': event.get('date'),
                'home_team': home_team.get('team', {}).get('name'),
                'home_team_id': home_team.get('team', {}).get('id'),
                'away_team': away_team.get('team', {}).get('name'),
                'away_team_id': away_team.get('team', {}).get('id'),
                'home_record': home_team.get('records', [{}])[0].get('summary', '0-0'),
                'away_record': away_team.get('records', [{}])[0].get('summary', '0-0'),
                'status': event.get('status', {}).get('type', {}).get('description', 'Scheduled')
            })
        
        return pd.DataFrame(games)
    
    def get_team_stats(self, sport: str, team_id: str) -> Dict:
        """Get detailed stats for a specific team."""
        endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{self.BASE_URL}/{endpoint}/teams/{team_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()

if __name__ == "__main__":
    # Test the API
    espn = ESPNAPI()
    
    print("Testing NBA teams...")
    nba_teams = espn.get_teams('nba')
    print(f"Found {len(nba_teams)} NBA teams")
    print(nba_teams.head())
    
    print("\nTesting NBA schedule...")
    nba_games = espn.get_schedule('nba', days=3)
    print(f"Found {len(nba_games)} upcoming games")
    print(nba_games.head())
