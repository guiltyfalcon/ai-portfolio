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


# Keep backward compatibility
ESPNClient = ESPNAPI
