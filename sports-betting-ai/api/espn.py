"""
ESPN API Client - Free sports data for NBA, NFL, MLB, NHL
No API key required - Enhanced with caching and error handling
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st

class ESPNAPI:
    """Client for ESPN's public API endpoints with caching."""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    SPORT_ENDPOINTS = {
        'nba': 'basketball/nba',
        'nfl': 'football/nfl',
        'mlb': 'baseball/mlb',
        'nhl': 'hockey/nhl',
        'ncaab': 'basketball/mens-college-basketball',
        'ncaaf': 'football/college-football'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_teams(_self, sport: str) -> pd.DataFrame:
        """Get all teams for a sport."""
        endpoint = _self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{_self.BASE_URL}/{endpoint}/teams"
        
        try:
            response = _self.session.get(url, timeout=10)
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
        except requests.RequestException as e:
            st.warning(f"Could not load teams for {sport}: {e}")
            return pd.DataFrame(columns=['id', 'name', 'abbreviation', 'location', 'record'])
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_schedule(_self, sport: str, days: int = 7) -> pd.DataFrame:
        """Get upcoming games for a sport."""
        endpoint = _self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{_self.BASE_URL}/{endpoint}/scoreboard"
        params = {'limit': 100, 'days': days}
        
        try:
            response = _self.session.get(url, params=params, timeout=10)
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
                
                home_team_data = home_team.get('team', {})
                away_team_data = away_team.get('team', {})
                
                games.append({
                    'game_id': event.get('id'),
                    'date': event.get('date'),
                    'home_team': home_team_data.get('name'),
                    'home_team_id': home_team_data.get('id'),
                    'away_team': away_team_data.get('name'),
                    'away_team_id': away_team_data.get('id'),
                    'home_record': home_team.get('records', [{}])[0].get('summary', '0-0'),
                    'away_record': away_team.get('records', [{}])[0].get('summary', '0-0'),
                    'home_score': home_team.get('score'),
                    'away_score': away_team.get('score'),
                    'status': event.get('status', {}).get('type', {}).get('description', 'Scheduled'),
                    'status_state': event.get('status', {}).get('type', {}).get('state', 'pre')
                })
            
            return pd.DataFrame(games)
        except requests.RequestException as e:
            st.warning(f"Could not load schedule for {sport}: {e}")
            return pd.DataFrame(columns=[
                'game_id', 'date', 'home_team', 'home_team_id', 'away_team', 'away_team_id',
                'home_record', 'away_record', 'home_score', 'away_score', 'status', 'status_state'
            ])
    
    def get_team_stats(self, sport: str, team_id: str) -> Dict:
        """Get detailed stats for a specific team."""
        endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{self.BASE_URL}/{endpoint}/teams/{team_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.warning(f"Could not load team stats: {e}")
            return {}
    
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_standings(_self, sport: str) -> pd.DataFrame:
        """Get current standings for a sport."""
        endpoint = _self.SPORT_ENDPOINTS.get(sport.lower())
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{_self.BASE_URL}/{endpoint}/standings"
        
        try:
            response = _self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings = []
            
            for team in data.get('standings', []):
                team_data = team.get('team', {})
                standings.append({
                    'team': team_data.get('name'),
                    'wins': team.get('wins', 0),
                    'losses': team.get('losses', 0),
                    'win_pct': team.get('winPercent', 0),
                    'home_record': team.get('homeRecord', '0-0'),
                    'away_record': team.get('awayRecord', '0-0')
                })
            
            return pd.DataFrame(standings)
        except requests.RequestException as e:
            st.warning(f"Could not load standings: {e}")
            return pd.DataFrame()
    
    def get_live_games(self, sport: str) -> pd.DataFrame:
        """Get currently live games."""
        schedule = self.get_schedule(sport, days=1)
        if schedule.empty:
            return pd.DataFrame()
        
        live = schedule[schedule['status_state'] == 'in']
        return live

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
