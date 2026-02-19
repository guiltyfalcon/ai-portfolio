"""
BallDontLie API Client - Free NBA player/team/game data
API Key required since 2024
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st
import os

BASE_URL = "https://api.balldontlie.io/v1"


def get_session(api_key: str) -> requests.Session:
    """Create a requests session with auth headers."""
    session = requests.Session()
    session.headers.update({
        "Authorization": api_key,
        "Accept": "application/json"
    })
    return session


@st.cache_data(ttl=3600)
def _search_players(api_key: str, search: str = None, per_page: int = 100) -> pd.DataFrame:
    """Internal cached function to search players."""
    url = f"{BASE_URL}/players"
    params = {"per_page": per_page}
    if search:
        params["search"] = search
    
    session = get_session(api_key)
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        players = data.get('data', [])
        return pd.DataFrame(players)
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def _get_season_averages(api_key: str, player_id: int, season: int = 2026) -> Dict:
    """Internal cached function to get season averages."""
    url = f"{BASE_URL}/season_averages"
    params = {
        "player_ids[]": player_id,
        "season": season
    }
    
    session = get_session(api_key)
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        stats = data.get('data', [])
        if stats:
            s = stats[0]
            return {
                'ppg': s.get('pts', 0),
                'rpg': s.get('reb', 0),
                'apg': s.get('ast', 0),
                'fg_pct': s.get('fg_pct', 0),
                'fg3_pct': s.get('fg3_pct', 0),
                'min': s.get('min', '0.0'),
                'games': s.get('games_played', 0),
                'spg': s.get('stl', 0),
                'bpg': s.get('blk', 0),
                'tpg': s.get('turnover', 0),
                'ft_pct': s.get('ft_pct', 0)
            }
        return {}
    except Exception as e:
        return {}


@st.cache_data(ttl=3600)
def _get_all_players(api_key: str, per_page: int = 600) -> pd.DataFrame:
    """Internal cached function to get all players."""
    url = f"{BASE_URL}/players"
    all_players = []
    cursor = None
    
    session = get_session(api_key)
    
    while True:
        params = {"per_page": 100}
        if cursor:
            params["cursor"] = cursor
        
        try:
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            players = data.get('data', [])
            if not players:
                break
            
            all_players.extend(players)
            
            if len(all_players) >= per_page:
                break
            
            meta = data.get('meta', {})
            cursor = meta.get('next_cursor')
            if not cursor:
                break
                
        except Exception as e:
            break
    
    return pd.DataFrame(all_players) if all_players else pd.DataFrame()


class BallDontLieAPI:
    """
    BallDontLie API - Requires API key (free tier available)
    Get key at: https://www.balldontlie.io/
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('BALLDONTLIE_API_KEY')
    
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return self.api_key is not None and len(self.api_key) > 10
    
    def get_players(self, search: str = None, per_page: int = 100) -> pd.DataFrame:
        """Search for NBA players."""
        if not self.is_configured():
            return pd.DataFrame()
        return _search_players(self.api_key, search, per_page)
    
    def get_player_season_averages(self, player_id: int, season: int = 2026) -> Dict:
        """Get season averages for a player (default 2026)."""
        if not self.is_configured():
            return {}
        return _get_season_averages(self.api_key, player_id, season)
    
    def get_all_players(self, per_page: int = 600) -> pd.DataFrame:
        """Get all active NBA players."""
        if not self.is_configured():
            return pd.DataFrame()
        return _get_all_players(self.api_key, per_page)
    
    def get_top_players(self, limit: int = 50) -> pd.DataFrame:
        """Get top scorers with season stats."""
        if not self.is_configured():
            return pd.DataFrame()
        
        players = self.get_all_players()
        if players.empty:
            return players
        
        player_stats = []
        for _, player in players.head(200).iterrows():
            stats = self.get_player_season_averages(player['id'])
            if stats and stats.get('games', 0) > 10:
                player_stats.append({
                    'id': player['id'],
                    'first_name': player['first_name'],
                    'last_name': player['last_name'],
                    'full_name': f"{player['first_name']} {player['last_name']}",
                    'position': player.get('position', ''),
                    'team': player.get('team', {}).get('full_name', ''),
                    **stats
                })
        
        df = pd.DataFrame(player_stats)
        if not df.empty and 'ppg' in df.columns:
            df = df.sort_values('ppg', ascending=False).head(limit)
        
        return df


# Keep backward compatibility
BallDontLieClient = BallDontLieAPI
