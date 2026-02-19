"""
ESPN API Client - Free sports data for NBA, NFL, MLB, NHL
Includes caching and retry logic for reliability
"""

import requests
import pandas as pd
import time
from typing import Dict, List, Optional
from functools import lru_cache

class ESPNAPI:
    """Client for ESPN's public API endpoints with caching."""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    SPORT_ENDPOINTS = {
        'nba': 'basketball/nba',
        'nfl': 'football/nfl',
        'mlb': 'baseball/mlb',
        'nhl': 'hockey/nhl'
    }
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize ESPN API client.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 5 minutes)
        """
        self.session = requests.Session()
        self.cache_ttl = cache_ttl
        self._last_request_time = 0
        self._min_request_interval = 0.5  # seconds between requests
        self._cache = {}
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                      retries: int = 3) -> Optional[Dict]:
        """Make request with retry logic."""
        for attempt in range(retries):
            try:
                self._rate_limit()
                response = self.session.get(url, params=params, timeout=10)
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt == retries - 1:
                    raise Exception(f"Request timed out after {retries} attempts")
                time.sleep(1)
                
            except requests.exceptions.ConnectionError:
                if attempt == retries - 1:
                    raise Exception("Connection failed - check internet connection")
                time.sleep(1)
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    return None  # No data available
                if attempt == retries - 1:
                    raise Exception(f"HTTP error: {e}")
                time.sleep(1)
        
        return None
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        return str(args)
    
    def _get_cached(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached data if not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _set_cached(self, key: str, data: pd.DataFrame):
        """Cache data with timestamp."""
        self._cache[key] = (data, time.time())
    
    def get_teams(self, sport: str, use_cache: bool = True) -> pd.DataFrame:
        """Get all teams for a sport with caching."""
        sport = sport.lower()
        endpoint = self.SPORT_ENDPOINTS.get(sport)
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        cache_key = self._get_cache_key('teams', sport)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.BASE_URL}/{endpoint}/teams"
        data = self._make_request(url)
        
        if data is None:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['id', 'name', 'abbreviation', 'location', 'record'])
        
        teams = []
        try:
            for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
                team_data = team.get('team', {})
                teams.append({
                    'id': team_data.get('id'),
                    'name': team_data.get('name'),
                    'abbreviation': team_data.get('abbreviation'),
                    'location': team_data.get('location'),
                    'record': team_data.get('record', {}).get('summary', '0-0')
                })
        except (IndexError, KeyError) as e:
            raise Exception(f"Unexpected API response format: {e}")
        
        df = pd.DataFrame(teams)
        if use_cache:
            self._set_cached(cache_key, df)
        return df
    
    def get_schedule(self, sport: str, days: int = 7, use_cache: bool = True) -> pd.DataFrame:
        """Get upcoming games for a sport with caching."""
        sport = sport.lower()
        endpoint = self.SPORT_ENDPOINTS.get(sport)
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        cache_key = self._get_cache_key('schedule', sport, days)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.BASE_URL}/{endpoint}/scoreboard"
        params = {'limit': 100, 'days': days}
        
        data = self._make_request(url, params)
        
        if data is None:
            return pd.DataFrame(columns=[
                'game_id', 'date', 'home_team', 'home_team_id', 
                'away_team', 'away_team_id', 'home_record', 'away_record', 'status'
            ])
        
        games = []
        try:
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
        except (IndexError, KeyError) as e:
            raise Exception(f"Unexpected API response format: {e}")
        
        df = pd.DataFrame(games)
        if use_cache:
            self._set_cached(cache_key, df)
        return df
    
    def get_team_stats(self, sport: str, team_id: str) -> Optional[Dict]:
        """Get detailed stats for a specific team."""
        sport = sport.lower()
        endpoint = self.SPORT_ENDPOINTS.get(sport)
        if not endpoint:
            raise ValueError(f"Unsupported sport: {sport}")
        
        cache_key = self._get_cache_key('team_stats', sport, team_id)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached.to_dict() if isinstance(cached, pd.DataFrame) else cached
        
        url = f"{self.BASE_URL}/{endpoint}/teams/{team_id}"
        data = self._make_request(url)
        
        if data:
            self._set_cached(cache_key, pd.DataFrame([data]))
        return data
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()

if __name__ == "__main__":
    # Test the API with caching
    espn = ESPNAPI()
    
    print("Testing NBA teams (first call - from API)...")
    start = time.time()
    nba_teams = espn.get_teams('nba')
    print(f"Found {len(nba_teams)} NBA teams in {time.time()-start:.2f}s")
    
    print("\nTesting NBA teams (second call - from cache)...")
    start = time.time()
    nba_teams = espn.get_teams('nba')
    print(f"Found {len(nba_teams)} NBA teams in {time.time()-start:.2f}s (cached)")
    
    print("\nTesting NBA schedule...")
    nba_games = espn.get_schedule('nba', days=3)
    print(f"Found {len(nba_games)} upcoming games")
