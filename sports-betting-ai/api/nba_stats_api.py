#!/usr/bin/env python3
"""
NBA Stats API - Real-time player statistics
Uses BallDontLie API (free, no auth required)
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# BallDontLie API (free tier)
BALLOTLIE_BASE_URL = "https://www.balldontlie.io/api/v1"

# Alternative: API-NBA (requires API key)
API_NBA_BASE_URL = "https://v3.basketball.api-sports.io"


def fetch_player_season_stats(player_id: int, season: str = "2025") -> Optional[Dict]:
    """
    Fetch player season averages from BallDontLie.
    Returns: pts, reb, ast, games_played, etc.
    """
    try:
        url = f"{BALLOTLIE_BASE_URL}/players/{player_id}/stats"
        params = {
            'seasons[]': season,
            'per_page': 100
        }
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('data', [])
            
            if not games:
                return None
            
            # Calculate averages
            total_pts = sum(g.get('pts', 0) for g in games)
            total_reb = sum(g.get('reb', 0) for g in games)
            total_ast = sum(g.get('ast', 0) for g in games)
            # Skip minutes calculation for now (string format)
            total_min = 0
            
            games_played = len(games)
            
            return {
                'games_played': games_played,
                'pts': round(total_pts / games_played, 1) if games_played > 0 else 0,
                'reb': round(total_reb / games_played, 1) if games_played > 0 else 0,
                'ast': round(total_ast / games_played, 1) if games_played > 0 else 0,
                'min': total_min / games_played if games_played > 0 else '0:00',
            }
    except Exception as e:
        print(f"⚠️ BallDontLie API error: {e}")
    
    return None


def fetch_player_last_n_games(player_id: int, n: int = 5) -> List[Dict]:
    """Fetch player's last N games with box score stats."""
    try:
        url = f"{BALLOTLIE_BASE_URL}/games"
        params = {
            'player_ids[]': player_id,
            'per_page': n,
            'sort': 'date',
            'direction': 'desc'
        }
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('data', [])
            
            last_n_stats = []
            for game in games:
                # Find player stats in this game
                for home_stat in game.get('home_team_stats', []):
                    if home_stat.get('player_id') == player_id:
                        last_n_stats.append({
                            'date': game.get('date'),
                            'opponent': game.get('visitor_team', {}).get('abbreviation'),
                            'home': True,
                            'pts': home_stat.get('pts', 0),
                            'reb': home_stat.get('reb', 0),
                            'ast': home_stat.get('ast', 0),
                            'min': home_stat.get('min', '0:00'),
                        })
                
                for visitor_stat in game.get('visitor_team_stats', []):
                    if visitor_stat.get('player_id') == player_id:
                        last_n_stats.append({
                            'date': game.get('date'),
                            'opponent': game.get('home_team', {}).get('abbreviation'),
                            'home': False,
                            'pts': visitor_stat.get('pts', 0),
                            'reb': visitor_stat.get('reb', 0),
                            'ast': visitor_stat.get('ast', 0),
                            'min': visitor_stat.get('min', '0:00'),
                        })
            
            return last_n_stats[:n]
    except Exception as e:
        print(f"⚠️ BallDontLie API error: {e}")
    
    return []


def calculate_hit_rate_at_line(player_games: List[Dict], line: float) -> float:
    """
    Calculate actual hit rate for a player at a specific line.
    Example: If line is 27.5, count how many games player scored 28+
    """
    if not player_games:
        return None
    
    hits = sum(1 for g in player_games if g.get('pts', 0) >= line)
    return round(hits / len(player_games) * 100, 1)


def fetch_team_schedule(team_id: int, season: str = "2025") -> List[Dict]:
    """Fetch team schedule to identify back-to-backs and rest days."""
    try:
        url = f"{BALLOTLIE_BASE_URL}/games"
        params = {
            'team_ids[]': team_id,
            'seasons[]': season,
            'per_page': 100
        }
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
    except Exception as e:
        print(f"⚠️ BallDontLie API error: {e}")
    
    return []


def get_rest_days(games: List[Dict], game_date: str) -> int:
    """Calculate rest days before a specific game."""
    if not games:
        return 0
    
    # Find previous game
    game_dates = sorted([g.get('date', '')[:10] for g in games if g.get('date', '') < game_date])
    
    if not game_dates:
        return 3  # No previous game = 3+ days rest
    
    last_game = game_dates[-1]
    rest = (datetime.strptime(game_date[:10], '%Y-%m-%d') - datetime.strptime(last_game, '%Y-%m-%d')).days
    return rest - 1  # -1 because game day doesn't count as rest


def is_back_to_back(games: List[Dict], game_date: str) -> bool:
    """Check if a game is on a back-to-back."""
    rest_days = get_rest_days(games, game_date)
    return rest_days == 0


def fetch_all_players_stats() -> Dict:
    """
    Fetch stats for all tracked NBA players.
    Returns comprehensive data for hit probability calculation.
    """
    # Player ID mapping (would need to be maintained or fetched from API)
    PLAYER_IDS = {
        'Giannis Antetokounmpo': 15,
        'Ja Morant': 246,
        'Joel Embiid': 145,
        'Shai Gilgeous-Alexander': 237,
        'Jayson Tatum': 192,
        'Luka Doncic': 132,
        'Nikola Jokic': 246,
        'LeBron James': 237,
        'Stephen Curry': 115,
        'Kevin Durant': 140,
    }
    
    all_stats = {}
    
    for player_name, player_id in PLAYER_IDS.items():
        print(f"  Fetching {player_name}...")
        
        # Season stats
        season_stats = fetch_player_season_stats(player_id)
        
        # Last 5 games
        last_5 = fetch_player_last_n_games(player_id, 5)
        last_5_avg = sum(g.get('pts', 0) for g in last_5) / len(last_5) if last_5 else 0
        
        # Last 10 games
        last_10 = fetch_player_last_n_games(player_id, 10)
        last_10_avg = sum(g.get('pts', 0) for g in last_10) / len(last_10) if last_10 else 0
        
        # Historical hit rates at common lines
        hit_rates = {}
        for line in [20, 22, 25, 27, 30, 32]:
            hit_rates[f'over_{line}_count'] = sum(1 for g in last_10 if g.get('pts', 0) >= line)
        
        all_stats[player_name] = {
            **season_stats,
            'last5_pts': round(last_5_avg, 1),
            'last10_pts': round(last_10_avg, 1),
            'last_5_games': last_5,
            'last_10_games': last_10,
            **hit_rates,
        }
    
    return all_stats


def main():
    """Test function - fetch stats for all tracked players."""
    print("=" * 60)
    print("🏀 NBA STATS API - Real-time Data Fetch")
    print("=" * 60)
    
    stats = fetch_all_players_stats()
    
    print(f"\n✅ Fetched stats for {len(stats)} players")
    
    for player_name, data in stats.items():
        print(f"\n{player_name}:")
        print(f"  Season Avg: {data.get('pts', 0)} PTS")
        print(f"  Last 5 Avg: {data.get('last5_pts', 0)} PTS")
        print(f"  Last 10 Avg: {data.get('last10_pts', 0)} PTS")
        print(f"  Games Played: {data.get('games_played', 0)}")


if __name__ == '__main__':
    main()
