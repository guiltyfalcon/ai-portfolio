"""
The Odds API Client - Live betting lines and odds
Requires API key from https://the-odds-api.com
Enhanced with better error handling and caching
Includes Yahoo Sports fallback when API quota exceeded
"""

import requests
import pandas as pd
import os
import json
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

# Sample odds data for fallback when API is rate limited
SAMPLE_ODDS = {
    'nba': [
        {
            'game_id': 'sample_1',
            'sport': 'NBA',
            'home_team': 'Los Angeles Lakers',
            'away_team': 'Los Angeles Clippers',
            'commence_time': '2026-02-20T20:00:00Z',
            'bookmaker': 'DraftKings (Sample)',
            'home_ml': -240,
            'away_ml': 198,
            'home_spread': -6.5,
            'home_spread_odds': -110,
            'away_spread': 6.5,
            'away_spread_odds': -110,
            'total': 225.5,
            'over_odds': -110,
            'under_odds': -110,
            'bookmaker_count': 1
        },
        {
            'game_id': 'sample_2',
            'sport': 'NBA',
            'home_team': 'Denver Nuggets',
            'away_team': 'Portland Trail Blazers',
            'commence_time': '2026-02-20T22:00:00Z',
            'bookmaker': 'DraftKings (Sample)',
            'home_ml': -142,
            'away_ml': 120,
            'home_spread': -3.0,
            'home_spread_odds': -110,
            'away_spread': 3.0,
            'away_spread_odds': -110,
            'total': 220.5,
            'over_odds': -110,
            'under_odds': -110,
            'bookmaker_count': 1
        }
    ],
    'nfl': [
        {
            'game_id': 'sample_1',
            'sport': 'NFL',
            'home_team': 'Kansas City Chiefs',
            'away_team': 'San Francisco 49ers',
            'commence_time': '2026-02-09T23:30:00Z',
            'bookmaker': 'DraftKings (Sample)',
            'home_ml': -130,
            'away_ml': 110,
            'home_spread': -2.5,
            'home_spread_odds': -110,
            'away_spread': 2.5,
            'away_spread_odds': -110,
            'total': 47.5,
            'over_odds': -110,
            'under_odds': -110,
            'bookmaker_count': 1
        }
    ]
}


def get_session() -> requests.Session:
    """Create a requests session."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    return session


def get_yahoo_fallback_odds(sport: str) -> pd.DataFrame:
    """
    Load odds from Yahoo Sports cache when The Odds API is unavailable.
    Returns empty DataFrame if no cache available.
    """
    try:
        # Look for Yahoo cache file
        cache_paths = [
            os.path.join(os.path.dirname(__file__), 'yahoo_odds_cache.json'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'yahoo_odds_cache.json'),
            '/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/yahoo_odds_cache.json',
        ]
        
        cache_data = None
        for path in cache_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    cache_data = json.load(f)
                break
        
        if not cache_data or 'sports' not in cache_data:
            return pd.DataFrame()
        
        games = cache_data['sports'].get(sport.lower(), [])
        if not games:
            return pd.DataFrame()
        
        # Add cache timestamp info
        cache_time = cache_data.get('timestamp', 'Unknown')
        for game in games:
            game['cache_timestamp'] = cache_time
            game['data_source'] = 'Yahoo Sports (Cached)'
        
        return pd.DataFrame(games)
        
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=120)  # Cache for 2 minutes
def _fetch_odds(api_key: str, sport: str, bookmaker: str = None, regions: str = 'us', markets: str = 'h2h,spreads,totals') -> pd.DataFrame:
    """
    Internal cached function to fetch odds.
    Returns Yahoo cache data if API fails (rate limiting).
    Returns sample data only if both API and cache fail.
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
        
        # Handle rate limiting / unauthorized - use Yahoo cache silently
        if response.status_code == 401:
            yahoo_df = get_yahoo_fallback_odds(sport)
            if not yahoo_df.empty:
                return yahoo_df
            else:
                return pd.DataFrame(SAMPLE_ODDS.get(sport.lower(), []))
        
        if response.status_code == 429:
            yahoo_df = get_yahoo_fallback_odds(sport)
            if not yahoo_df.empty:
                return yahoo_df
            else:
                return pd.DataFrame(SAMPLE_ODDS.get(sport.lower(), []))
        
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
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            yahoo_df = get_yahoo_fallback_odds(sport)
            if not yahoo_df.empty:
                return yahoo_df
        else:
            yahoo_df = get_yahoo_fallback_odds(sport)
            if not yahoo_df.empty:
                return yahoo_df
        
        return pd.DataFrame(SAMPLE_ODDS.get(sport.lower(), []))
        
    except Exception as e:
        # Silently fall back to Yahoo cache
        yahoo_df = get_yahoo_fallback_odds(sport)
        if not yahoo_df.empty:
            return yahoo_df
        return pd.DataFrame(SAMPLE_ODDS.get(sport.lower(), []))


@st.cache_data(ttl=300)
def _fetch_sports(api_key: str) -> pd.DataFrame:
    """Internal cached function to fetch sports list."""
    url = f"{BASE_URL}/sports"
    params = {'apiKey': api_key}
    session = get_session()
    
    try:
        response = session.get(url, params=params, timeout=10)
        if response.status_code == 401:
            return pd.DataFrame([{'key': 'basketball_nba', 'title': 'NBA'}])
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        return pd.DataFrame([{'key': 'basketball_nba', 'title': 'NBA'}])


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
        Returns sample data if API fails.
        """
        if not self.is_configured():
            st.warning("⚠️ Odds API key not configured. Showing sample data.")
            return pd.DataFrame(SAMPLE_ODDS.get(sport.lower(), []))
        
        sport_key = SPORTS.get(sport.lower())
        if not sport_key:
            st.error(f"Unsupported sport: {sport}")
            return pd.DataFrame()
        
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
