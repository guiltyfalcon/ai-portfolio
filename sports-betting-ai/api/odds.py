"""
The Odds API Client - Live betting lines and odds
Requires API key from https://the-odds-api.com
"""

import requests
import pandas as pd
import os
from typing import Dict, List, Optional
from datetime import datetime

class OddsAPI:
    """Client for The Odds API - live sports betting lines."""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    SPORTS = {
        'nba': 'basketball_nba',
        'nfl': 'americanfootball_nfl',
        'mlb': 'baseball_mlb',
        'nhl': 'icehockey_nhl'
    }
    
    BOOKMAKERS = ['draftkings', 'fanduel', 'betmgm', 'williamhill', 'bet365']
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('THEODDS_API_KEY')
        if not self.api_key:
            raise ValueError("Odds API key required. Set THEODDS_API_KEY env var.")
        self.session = requests.Session()
    
    def get_sports(self) -> pd.DataFrame:
        """Get list of available sports."""
        url = f"{self.BASE_URL}/sports"
        params = {'apiKey': self.api_key}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return pd.DataFrame(response.json())
    
    def get_odds(self, sport: str, regions: str = 'us', markets: str = 'h2h,spreads,totals') -> pd.DataFrame:
        """
        Get odds for a sport.
        
        Args:
            sport: 'nba', 'nfl', 'mlb', 'nhl'
            regions: 'us', 'uk', 'au', 'eu'
            markets: 'h2h' (moneyline), 'spreads', 'totals' (over/under)
        """
        sport_key = self.SPORTS.get(sport.lower())
        if not sport_key:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{self.BASE_URL}/sports/{sport_key}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': regions,
            'markets': markets,
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        games = []
        
        for game in data:
            game_info = {
                'game_id': game.get('id'),
                'sport': sport.upper(),
                'home_team': game.get('home_team'),
                'away_team': game.get('away_team'),
                'commence_time': game.get('commence_time'),
                'bookmaker_count': len(game.get('bookmakers', []))
            }
            
            # Extract best odds across bookmakers
            bookmakers = game.get('bookmakers', [])
            if bookmakers:
                # Get DraftKings or first available
                dk = next((b for b in bookmakers if b['key'] == 'draftkings'), bookmakers[0])
                
                for market in dk.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            if outcome['name'] == game_info['home_team']:
                                game_info['home_ml'] = outcome['price']
                            elif outcome['name'] == game_info['away_team']:
                                game_info['away_ml'] = outcome['price']
                    
                    elif market['key'] == 'spreads':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            if outcome['name'] == game_info['home_team']:
                                game_info['home_spread'] = outcome.get('point')
                                game_info['home_spread_odds'] = outcome['price']
                            elif outcome['name'] == game_info['away_team']:
                                game_info['away_spread'] = outcome.get('point')
                                game_info['away_spread_odds'] = outcome['price']
                    
                    elif market['key'] == 'totals':
                        game_info['total'] = market.get('outcomes', [{}])[0].get('point')
            
            games.append(game_info)
        
        return pd.DataFrame(games)
    
    def calculate_implied_probability(self, american_odds: float) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def find_value_bets(self, predictions: pd.DataFrame, odds: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
        """
        Find value bets where model probability > implied probability + threshold.
        
        Args:
            predictions: DataFrame with 'home_win_prob' and 'away_win_prob'
            odds: DataFrame with moneyline odds
            threshold: Minimum edge required (default 5%)
        """
        value_bets = []
        
        for _, game in odds.iterrows():
            game_id = game.get('game_id')
            pred = predictions[predictions['game_id'] == game_id]
            
            if pred.empty:
                continue
            
            pred = pred.iloc[0]
            
            # Check home team value
            if 'home_ml' in game and not pd.isna(game['home_ml']):
                implied_home = self.calculate_implied_probability(game['home_ml'])
                model_home = pred.get('home_win_prob', 0.5)
                
                if model_home > implied_home + threshold:
                    value_bets.append({
                        'game_id': game_id,
                        'team': game['home_team'],
                        'bet_type': 'Moneyline',
                        'odds': game['home_ml'],
                        'implied_prob': implied_home,
                        'model_prob': model_home,
                        'edge': model_home - implied_home,
                        'pick': f"{game['home_team']} ML",
                        'confidence': 'High' if model_home > implied_home + 0.1 else 'Medium'
                    })
            
            # Check away team value
            if 'away_ml' in game and not pd.isna(game['away_ml']):
                implied_away = self.calculate_implied_probability(game['away_ml'])
                model_away = pred.get('away_win_prob', 0.5)
                
                if model_away > implied_away + threshold:
                    value_bets.append({
                        'game_id': game_id,
                        'team': game['away_team'],
                        'bet_type': 'Moneyline',
                        'odds': game['away_ml'],
                        'implied_prob': implied_away,
                        'model_prob': model_away,
                        'edge': model_away - implied_away,
                        'pick': f"{game['away_team']} ML",
                        'confidence': 'High' if model_away > implied_away + 0.1 else 'Medium'
                    })
        
        return pd.DataFrame(value_bets)

if __name__ == "__main__":
    # Test with your API key
    import os
    api_key = os.getenv('THEODDS_API_KEY', '8fcaab13355be4098fc79f7dbce9821b')
    
    odds_api = OddsAPI(api_key)
    
    print("Testing available sports...")
    sports = odds_api.get_sports()
    print(f"Available sports: {len(sports)}")
    print(sports[['key', 'title']].head(10))
    
    print("\nTesting NBA odds...")
    nba_odds = odds_api.get_odds('nba')
    print(f"Found {len(nba_odds)} games with odds")
    print(nba_odds[['home_team', 'away_team', 'home_ml', 'away_ml']].head())
