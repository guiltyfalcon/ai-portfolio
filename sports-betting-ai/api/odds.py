"""
The Odds API Client - Live betting lines and odds
Requires API key from https://the-odds-api.com
Enhanced with better error handling and caching
"""

import requests
import pandas as pd
import os
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st

class OddsAPI:
    """Client for The Odds API - live sports betting lines."""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    SPORTS = {
        'nba': 'basketball_nba',
        'nfl': 'americanfootball_nfl',
        'mlb': 'baseball_mlb',
        'nhl': 'icehockey_nhl',
        'ncaab': 'basketball_ncaab',
        'ncaaf': 'americanfootball_ncaaf',
        'soccer_epl': 'soccer_epl',
        'soccer_la_liga': 'soccer_spain_la_liga',
        'ufc': 'mma_mixed_martial_arts'
    }
    
    BOOKMAKERS = ['draftkings', 'fanduel', 'betmgm', 'williamhill', 'bet365', 'pinnacle']
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('THEODDS_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return self.api_key is not None and len(self.api_key) > 10
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_sports(_self) -> pd.DataFrame:
        """Get list of available sports."""
        if not _self.is_configured():
            return pd.DataFrame()
        
        url = f"{_self.BASE_URL}/sports"
        params = {'apiKey': _self.api_key}
        
        try:
            response = _self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return pd.DataFrame(response.json())
        except requests.RequestException as e:
            st.warning(f"Could not load sports list: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_odds(_self, sport: str, regions: str = 'us', markets: str = 'h2h,spreads,totals') -> pd.DataFrame:
        """
        Get odds for a sport.
        
        Args:
            sport: 'nba', 'nfl', 'mlb', 'nhl', etc.
            regions: 'us', 'uk', 'au', 'eu'
            markets: 'h2h' (moneyline), 'spreads', 'totals'
        """
        if not _self.is_configured():
            raise ValueError("Odds API key not configured. Set THEODDS_API_KEY environment variable.")
        
        sport_key = _self.SPORTS.get(sport.lower())
        if not sport_key:
            raise ValueError(f"Unsupported sport: {sport}")
        
        url = f"{_self.BASE_URL}/sports/{sport_key}/odds"
        params = {
            'apiKey': _self.api_key,
            'regions': regions,
            'markets': markets,
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        try:
            response = _self.session.get(url, params=params, timeout=15)
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
                            for outcome in market.get('outcomes', []):
                                if outcome.get('name', '').lower() == 'over':
                                    game_info['over_odds'] = outcome.get('price')
                                elif outcome.get('name', '').lower() == 'under':
                                    game_info['under_odds'] = outcome.get('price')
                
                games.append(game_info)
            
            return pd.DataFrame(games)
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch odds: {e}")
    
    def calculate_implied_probability(self, american_odds: float) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def calculate_true_probability(self, american_odds: float, vig: float = 0.05) -> float:
        """
        Calculate true probability by removing vig.
        
        Args:
            american_odds: The odds
            vig: The vig percentage (default 5%)
        """
        implied = self.calculate_implied_probability(american_odds)
        return implied / (1 + vig)
    
    def find_value_bets(self, predictions: pd.DataFrame, odds: pd.DataFrame, 
                        threshold: float = 0.05) -> pd.DataFrame:
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
            if 'home_ml' in game and pd.notna(game['home_ml']):
                implied_home = self.calculate_implied_probability(game['home_ml'])
                model_home = pred.get('home_win_prob', 0.5)
                
                if model_home > implied_home + threshold:
                    value_bets.append({
                        'game_id': game_id,
                        'team': game['home_team'],
                        'opponent': game['away_team'],
                        'bet_type': 'Moneyline',
                        'odds': game['home_ml'],
                        'implied_prob': implied_home,
                        'model_prob': model_home,
                        'edge': model_home - implied_home,
                        'pick': f"{game['home_team']} ML",
                        'confidence': 'High' if model_home > implied_home + 0.1 else 'Medium',
                        'ev': (model_home * self.odds_to_decimal(game['home_ml']) - 1) * 100
                    })
            
            # Check away team value
            if 'away_ml' in game and pd.notna(game['away_ml']):
                implied_away = self.calculate_implied_probability(game['away_ml'])
                model_away = pred.get('away_win_prob', 0.5)
                
                if model_away > implied_away + threshold:
                    value_bets.append({
                        'game_id': game_id,
                        'team': game['away_team'],
                        'opponent': game['home_team'],
                        'bet_type': 'Moneyline',
                        'odds': game['away_ml'],
                        'implied_prob': implied_away,
                        'model_prob': model_away,
                        'edge': model_away - implied_away,
                        'pick': f"{game['away_team']} ML",
                        'confidence': 'High' if model_away > implied_away + 0.1 else 'Medium',
                        'ev': (model_away * self.odds_to_decimal(game['away_ml']) - 1) * 100
                    })
        
        return pd.DataFrame(value_bets)
    
    def odds_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal odds."""
        if american_odds > 0:
            return 1 + (american_odds / 100)
        else:
            return 1 + (100 / abs(american_odds))
    
    def get_line_movement(self, game_id: str) -> pd.DataFrame:
        """
        Get historical line movement for a game.
        Note: This requires a premium Odds API subscription.
        """
        if not self.is_configured():
            raise ValueError("Odds API key not configured.")
        
        url = f"{self.BASE_URL}/sports/{game_id}/odds-history"
        params = {'apiKey': self.api_key}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return pd.DataFrame(response.json())
        except requests.RequestException as e:
            st.warning(f"Could not load line movement: {e}")
            return pd.DataFrame()
    
    def get_best_odds(self, odds_df: pd.DataFrame, team: str, bet_type: str = 'ml') -> Dict:
        """
        Find the best odds for a team across all bookmakers.
        
        Args:
            odds_df: DataFrame with odds
            team: Team name
            bet_type: 'ml' (moneyline), 'spread', or 'total'
            
        Returns:
            Dict with best odds and bookmaker
        """
        best = {'odds': None, 'bookmaker': None}
        
        # This would require fetching odds from all bookmakers
        # For now, return the available odds
        if not odds_df.empty:
            game = odds_df[
                (odds_df['home_team'] == team) | (odds_df['away_team'] == team)
            ]
            if not game.empty:
                game = game.iloc[0]
                is_home = game['home_team'] == team
                
                if bet_type == 'ml':
                    best['odds'] = game.get('home_ml') if is_home else game.get('away_ml')
                    best['bookmaker'] = 'DraftKings'
                elif bet_type == 'spread':
                    best['spread'] = game.get('home_spread') if is_home else game.get('away_spread')
                    best['odds'] = game.get('home_spread_odds') if is_home else game.get('away_spread_odds')
                    best['bookmaker'] = 'DraftKings'
        
        return best

if __name__ == "__main__":
    # Test with API key if available
    import os
    api_key = os.getenv('THEODDS_API_KEY', '')
    
    if api_key:
        odds_api = OddsAPI(api_key)
        
        print("Testing available sports...")
        sports = odds_api.get_sports()
        print(f"Available sports: {len(sports)}")
        if not sports.empty:
            print(sports[['key', 'title']].head(10))
        
        print("\nTesting NBA odds...")
        try:
            nba_odds = odds_api.get_odds('nba')
            print(f"Found {len(nba_odds)} games with odds")
            print(nba_odds[['home_team', 'away_team', 'home_ml', 'away_ml']].head())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No API key found. Set THEODDS_API_KEY to test.")
