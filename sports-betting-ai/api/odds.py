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

BOOKMAKER_MAP = {
    'draftkings': 'draftkings',
    'fanduel': 'fanduel', 
    'betmgm': 'betmgm',
    'pinnacle': 'pinnacle',
    'williamhill': 'williamhill_us',
    'bet365': 'bet365'
}


def get_session() -> requests.Session:
    """Create a requests session."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    return session


@st.cache_data(ttl=60)  # Cache for 1 minute (shorter for bookmaker switching)
def _fetch_odds(api_key: str, sport: str, bookmaker: str = None, regions: str = 'us', markets: str = 'h2h,spreads,totals') -> pd.DataFrame:
    """
    Internal cached function to fetch odds.
    Cache key includes api_key, sport, and bookmaker.
    """
    sport_key = SPORTS.get(sport.lower())
    if not sport_key:
        return pd.DataFrame()
    
    url = f"{BASE_URL}/sports/{sport_key}/odds"
    params = {
        'apiKey': api_key,
        'regions': regions,
        'markets': markets,
        'oddsFormat': 'american',
        'dateFormat': 'iso'
    }
    
    session = get_session()
    
    try:
        response = session.get(url, params=params, timeout=15)
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
            
            # Extract odds from selected bookmaker
            bookmakers = game.get('bookmakers', [])
            if bookmakers:
                # Get selected bookmaker or first available
                target_key = BOOKMAKER_MAP.get(bookmaker.lower(), 'draftkings') if bookmaker else 'draftkings'
                selected = next((b for b in bookmakers if b['key'] == target_key), bookmakers[0])
                
                # Store which bookmaker we got odds from
                game_info['bookmaker'] = selected.get('title', selected.get('key', 'Unknown'))
                
                for market in selected.get('markets', []):
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
    except Exception as e:
        st.error(f"Error fetching odds: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def _fetch_sports(api_key: str) -> pd.DataFrame:
    """Internal cached function to fetch sports list."""
    url = f"{BASE_URL}/sports"
    params = {'apiKey': api_key}
    session = get_session()
    
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        return pd.DataFrame()


class OddsAPI:
    """Client for The Odds API - live sports betting lines."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('THEODDS_API_KEY')
    
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return self.api_key is not None and len(self.api_key) > 10
    
    def get_sports(self) -> pd.DataFrame:
        """Get list of available sports."""
        if not self.is_configured():
            return pd.DataFrame()
        return _fetch_sports(self.api_key)
    
    def get_odds(self, sport: str, bookmaker: str = None, regions: str = 'us', markets: str = 'h2h,spreads,totals') -> pd.DataFrame:
        """
        Get odds for a sport from a specific bookmaker.
        
        Args:
            sport: 'nba', 'nfl', 'mlb', 'nhl', etc.
            bookmaker: 'draftkings', 'fanduel', 'betmgm', 'pinnacle', etc.
            regions: 'us', 'uk', 'au', 'eu'
            markets: 'h2h' (moneyline), 'spreads', 'totals'
        """
        if not self.is_configured():
            raise ValueError("Odds API key not configured. Set THEODDS_API_KEY environment variable.")
        
        sport_key = SPORTS.get(sport.lower())
        if not sport_key:
            raise ValueError(f"Unsupported sport: {sport}")
        
        # Pass api_key, sport, and bookmaker to cached function
        # Changing bookmaker will create a different cache entry
        return _fetch_odds(self.api_key, sport, bookmaker, regions, markets)
    
    def calculate_implied_probability(self, american_odds: float) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def find_value_bets(self, predictions: pd.DataFrame, odds: pd.DataFrame, 
                        threshold: float = 0.05) -> pd.DataFrame:
        """
        Find value bets where model probability > implied probability + threshold.
        """
        value_bets = []
        
        for _, game in odds.iterrows():
            game_id = game.get('game_id')
            pred = predictions[predictions['game_id'] == game_id]
            
            if pred.empty:
                continue
            
            home_ml = game.get('home_ml')
            away_ml = game.get('away_ml')
            home_prob = pred.iloc[0].get('home_win_prob', 0.5)
            away_prob = pred.iloc[0].get('away_win_prob', 0.5)
            
            if pd.notna(home_ml):
                implied_home = self.calculate_implied_probability(home_ml)
                if home_prob > implied_home + threshold:
                    value_bets.append({
                        'game_id': game_id,
                        'team': game['home_team'],
                        'odds': home_ml,
                        'model_prob': home_prob,
                        'implied_prob': implied_home,
                        'edge': home_prob - implied_home
                    })
            
            if pd.notna(away_ml):
                implied_away = self.calculate_implied_probability(away_ml)
                if away_prob > implied_away + threshold:
                    value_bets.append({
                        'game_id': game_id,
                        'team': game['away_team'],
                        'odds': away_ml,
                        'model_prob': away_prob,
                        'implied_prob': implied_away,
                        'edge': away_prob - implied_away
                    })
        
        return pd.DataFrame(value_bets)


# Keep backward compatibility
OddsClient = OddsAPI
