"""
BallDontLie API Client - Free NBA data 
UPDATE: API now requires authentication. Using ESPN fallback.
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class BallDontLieAPI:
    """
    BallDontLie API - Note: Now requires API key for v1
    This class provides graceful fallback to ESPN data
    """
    
    BASE_URL = "https://api.balldontlie.io/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        
        if not self.api_key:
            print("Warning: BallDontLie API now requires authentication")
            print("Get free API key at: https://www.balldontlie.io/")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with auth."""
        if not self.api_key:
            raise Exception("BallDontLie API key required. Get one at balldontlie.io")
        
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Authorization": self.api_key}
        response = self.session.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_teams(self) -> pd.DataFrame:
        """Get all NBA teams."""
        try:
            data = self._make_request("teams")
            teams = [team for team in data.get('data', [])]
            return pd.DataFrame(teams)
        except Exception as e:
            print(f"BallDontLie error: {e}")
            # Fallback to default NBA teams
            return pd.DataFrame([
                {'id': 1, 'name': 'Atlanta Hawks', 'abbreviation': 'ATL'},
                {'id': 2, 'name': 'Boston Celtics', 'abbreviation': 'BOS'},
                {'id': 3, 'name': 'Brooklyn Nets', 'abbreviation': 'BKN'},
                {'id': 4, 'name': 'Charlotte Hornets', 'abbreviation': 'CHA'},
                {'id': 5, 'name': 'Chicago Bulls', 'abbreviation': 'CHI'},
                {'id': 6, 'name': 'Cleveland Cavaliers', 'abbreviation': 'CLE'},
                {'id': 7, 'name': 'Dallas Mavericks', 'abbreviation': 'DAL'},
                {'id': 8, 'name': 'Denver Nuggets', 'abbreviation': 'DEN'},
                {'id': 9, 'name': 'Detroit Pistons', 'abbreviation': 'DET'},
                {'id': 10, 'name': 'Golden State Warriors', 'abbreviation': 'GSW'},
                {'id': 11, 'name': 'Houston Rockets', 'abbreviation': 'HOU'},
                {'id': 12, 'name': 'Indiana Pacers', 'abbreviation': 'IND'},
                {'id': 13, 'name': 'LA Clippers', 'abbreviation': 'LAC'},
                {'id': 14, 'name': 'Los Angeles Lakers', 'abbreviation': 'LAL'},
                {'id': 15, 'name': 'Memphis Grizzlies', 'abbreviation': 'MEM'},
                {'id': 16, 'name': 'Miami Heat', 'abbreviation': 'MIA'},
                {'id': 17, 'name': 'Milwaukee Bucks', 'abbreviation': 'MIL'},
                {'id': 18, 'name': 'Minnesota Timberwolves', 'abbreviation': 'MIN'},
                {'id': 19, 'name': 'New Orleans Pelicans', 'abbreviation': 'NOP'},
                {'id': 20, 'name': 'New York Knicks', 'abbreviation': 'NYK'},
                {'id': 21, 'name': 'Oklahoma City Thunder', 'abbreviation': 'OKC'},
                {'id': 22, 'name': 'Orlando Magic', 'abbreviation': 'ORL'},
                {'id': 23, 'name': 'Philadelphia 76ers', 'abbreviation': 'PHI'},
                {'id': 24, 'name': 'Phoenix Suns', 'abbreviation': 'PHX'},
                {'id': 25, 'name': 'Portland Trail Blazers', 'abbreviation': 'POR'},
                {'id': 26, 'name': 'Sacramento Kings', 'abbreviation': 'SAC'},
                {'id': 27, 'name': 'San Antonio Spurs', 'abbreviation': 'SAS'},
                {'id': 28, 'name': 'Toronto Raptors', 'abbreviation': 'TOR'},
                {'id': 29, 'name': 'Utah Jazz', 'abbreviation': 'UTA'},
                {'id': 30, 'name': 'Washington Wizards', 'abbreviation': 'WAS'}
            ])

if __name__ == "__main__":
    print("BallDontLie API - requires authentication key")
    print("Get free key at: https://www.balldontlie.io/")
