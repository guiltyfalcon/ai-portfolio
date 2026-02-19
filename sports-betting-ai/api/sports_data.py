"""
Sports Data API - Multi-sport player props
NBA: nba_api (free, no key) with static fallback
NFL/MLB/NHL: Static data (reliable, no API needed)
"""

import pandas as pd
from typing import Dict, List, Optional
import streamlit as st
import random

# Try to import NBA API
try:
    from nba_api.stats.static import players as nba_players
    from nba_api.stats.endpoints import playercareerstats
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False


# ============ STATIC DATA FOR ALL SPORTS ============

NBA_TEAMS = {
    'Lakers': [
        {'name': 'LeBron James', 'ppg': 25.2, 'rpg': 7.8, 'apg': 9.0, 'fg_pct': 0.52},
        {'name': 'Anthony Davis', 'ppg': 24.8, 'rpg': 12.5, 'apg': 3.5, 'fg_pct': 0.55},
        {'name': 'Austin Reaves', 'ppg': 15.8, 'rpg': 4.2, 'apg': 5.1, 'fg_pct': 0.48},
        {'name': "D'Angelo Russell", 'ppg': 14.2, 'rpg': 3.1, 'apg': 6.0, 'fg_pct': 0.45},
    ],
    'Warriors': [
        {'name': 'Stephen Curry', 'ppg': 28.5, 'rpg': 4.4, 'apg': 5.1, 'fg_pct': 0.47},
        {'name': 'Klay Thompson', 'ppg': 18.2, 'rpg': 3.5, 'apg': 2.3, 'fg_pct': 0.43},
        {'name': 'Draymond Green', 'ppg': 8.5, 'rpg': 7.2, 'apg': 6.8, 'fg_pct': 0.49},
        {'name': 'Andrew Wiggins', 'ppg': 13.8, 'rpg': 4.5, 'apg': 1.7, 'fg_pct': 0.46},
    ],
    'Celtics': [
        {'name': 'Jayson Tatum', 'ppg': 27.2, 'rpg': 8.3, 'apg': 4.9, 'fg_pct': 0.48},
        {'name': 'Jaylen Brown', 'ppg': 23.5, 'rpg': 5.6, 'apg': 3.4, 'fg_pct': 0.49},
        {'name': 'Kristaps Porzingis', 'ppg': 20.1, 'rpg': 7.2, 'apg': 2.0, 'fg_pct': 0.51},
        {'name': 'Derrick White', 'ppg': 15.2, 'rpg': 4.0, 'apg': 5.2, 'fg_pct': 0.46},
    ],
    'Nuggets': [
        {'name': 'Nikola Jokic', 'ppg': 25.9, 'rpg': 12.0, 'apg': 9.1, 'fg_pct': 0.58},
        {'name': 'Jamal Murray', 'ppg': 21.2, 'rpg': 4.1, 'apg': 6.5, 'fg_pct': 0.48},
        {'name': 'Aaron Gordon', 'ppg': 13.8, 'rpg': 6.5, 'apg': 3.2, 'fg_pct': 0.56},
        {'name': 'Michael Porter Jr', 'ppg': 16.5, 'rpg': 7.0, 'apg': 1.5, 'fg_pct': 0.48},
    ],
}

NFL_TEAMS = {
    'Chiefs': [
        {'name': 'Patrick Mahomes', 'pass_yds': 272, 'pass_td': 2.1, 'rush_yds': 28, 'rush_td': 0.3},
        {'name': 'Travis Kelce', 'rec': 6.5, 'rec_yds': 78, 'rec_td': 0.7},
        {'name': 'Rashee Rice', 'rec': 5.2, 'rec_yds': 62, 'rec_td': 0.5},
        {'name': 'Isiah Pacheco', 'rush': 15, 'rush_yds': 68, 'rush_td': 0.6, 'rec': 2.5},
    ],
    '49ers': [
        {'name': 'Brock Purdy', 'pass_yds': 265, 'pass_td': 1.9, 'rush_yds': 18, 'rush_td': 0.2},
        {'name': 'Christian McCaffrey', 'rush': 18, 'rush_yds': 85, 'rush_td': 0.8, 'rec': 4.5, 'rec_yds': 42},
        {'name': 'Deebo Samuel', 'rec': 4.8, 'rec_yds': 72, 'rec_td': 0.5, 'rush': 3.2},
        {'name': 'George Kittle', 'rec': 4.2, 'rec_yds': 58, 'rec_td': 0.4},
    ],
    'Ravens': [
        {'name': 'Lamar Jackson', 'pass_yds': 228, 'pass_td': 1.8, 'rush_yds': 68, 'rush_td': 0.6},
        {'name': 'Derrick Henry', 'rush': 22, 'rush_yds': 112, 'rush_td': 1.0, 'rec': 1.5},
        {'name': 'Zay Flowers', 'rec': 5.5, 'rec_yds': 68, 'rec_td': 0.4},
        {'name': 'Mark Andrews', 'rec': 4.2, 'rec_yds': 52, 'rec_td': 0.5},
    ],
    'Bills': [
        {'name': 'Josh Allen', 'pass_yds': 258, 'pass_td': 2.2, 'rush_yds': 52, 'rush_td': 0.7},
        {'name': 'Stefon Diggs', 'rec': 6.2, 'rec_yds': 85, 'rec_td': 0.6},
        {'name': 'James Cook', 'rush': 12, 'rush_yds': 48, 'rush_td': 0.3, 'rec': 4.5, 'rec_yds': 38},
        {'name': 'Dalton Kincaid', 'rec': 4.8, 'rec_yds': 48, 'rec_td': 0.3},
    ],
}

MLB_TEAMS = {
    'Dodgers': [
        {'name': 'Shohei Ohtani', 'avg': 0.304, 'hr': 0.28, 'rbi': 0.85, 'obp': 0.382, 'slg': 0.612},
        {'name': 'Mookie Betts', 'avg': 0.280, 'hr': 0.22, 'rbi': 0.72, 'obp': 0.358, 'slg': 0.512},
        {'name': 'Freddie Freeman', 'avg': 0.295, 'hr': 0.18, 'rbi': 0.78, 'obp': 0.375, 'slg': 0.508},
        {'name': 'Will Smith', 'avg': 0.262, 'hr': 0.16, 'rbi': 0.58, 'obp': 0.342, 'slg': 0.458},
    ],
    'Yankees': [
        {'name': 'Aaron Judge', 'avg': 0.285, 'hr': 0.35, 'rbi': 0.95, 'obp': 0.398, 'slg': 0.625},
        {'name': 'Juan Soto', 'avg': 0.292, 'hr': 0.25, 'rbi': 0.82, 'obp': 0.412, 'slg': 0.548},
        {'name': 'Giancarlo Stanton', 'avg': 0.245, 'hr': 0.32, 'rbi': 0.78, 'obp': 0.318, 'slg': 0.545},
        {'name': 'Gleyber Torres', 'avg': 0.272, 'hr': 0.15, 'rbi': 0.58, 'obp': 0.335, 'slg': 0.425},
    ],
    'Braves': [
        {'name': 'Ronald Acuna Jr', 'avg': 0.295, 'hr': 0.22, 'rbi': 0.68, 'obp': 0.385, 'slg': 0.525, 'sb': 0.45},
        {'name': 'Matt Olson', 'avg': 0.275, 'hr': 0.28, 'rbi': 0.88, 'obp': 0.358, 'slg': 0.545},
        {'name': 'Austin Riley', 'avg': 0.285, 'hr': 0.24, 'rbi': 0.82, 'obp': 0.345, 'slg': 0.515},
        {'name': 'Marcell Ozuna', 'avg': 0.280, 'hr': 0.25, 'rbi': 0.85, 'obp': 0.340, 'slg': 0.505},
    ],
    'Astros': [
        {'name': 'Yordan Alvarez', 'avg': 0.295, 'hr': 0.30, 'rbi': 0.92, 'obp': 0.375, 'slg': 0.598},
        {'name': 'Jose Altuve', 'avg': 0.305, 'hr': 0.18, 'rbi': 0.68, 'obp': 0.365, 'slg': 0.485},
        {'name': 'Kyle Tucker', 'avg': 0.285, 'hr': 0.22, 'rbi': 0.78, 'obp': 0.355, 'slg': 0.515},
        {'name': 'Alex Bregman', 'avg': 0.265, 'hr': 0.18, 'rbi': 0.68, 'obp': 0.355, 'slg': 0.445},
    ],
}

NHL_TEAMS = {
    'Avalanche': [
        {'name': 'Nathan MacKinnon', 'goals': 0.52, 'assists': 0.88, 'points': 1.40, 'shots': 4.5},
        {'name': 'Cale Makar', 'goals': 0.28, 'assists': 0.72, 'points': 1.00, 'shots': 3.2},
        {'name': 'Mikko Rantanen', 'goals': 0.42, 'assists': 0.58, 'points': 1.00, 'shots': 3.8},
        {'name': 'Valeri Nichushkin', 'goals': 0.35, 'assists': 0.42, 'points': 0.77, 'shots': 2.8},
    ],
    'Rangers': [
        {'name': 'Artemi Panarin', 'goals': 0.38, 'assists': 0.82, 'points': 1.20, 'shots': 3.5},
        {'name': 'Mika Zibanejad', 'goals': 0.42, 'assists': 0.55, 'points': 0.97, 'shots': 3.2},
        {'name': 'Vincent Trocheck', 'goals': 0.28, 'assists': 0.48, 'points': 0.76, 'shots': 2.5},
        {'name': 'Chris Kreider', 'goals': 0.45, 'assists': 0.32, 'points': 0.77, 'shots': 2.8},
    ],
    'Oilers': [
        {'name': 'Connor McDavid', 'goals': 0.55, 'assists': 1.05, 'points': 1.60, 'shots': 4.2},
        {'name': 'Leon Draisaitl', 'goals': 0.52, 'assists': 0.72, 'points': 1.24, 'shots': 3.5},
        {'name': 'Zach Hyman', 'goals': 0.45, 'assists': 0.42, 'points': 0.87, 'shots': 3.0},
        {'name': 'Ryan Nugent-Hopkins', 'goals': 0.28, 'assists': 0.55, 'points': 0.83, 'shots': 2.5},
    ],
    'Maple Leafs': [
        {'name': 'Auston Matthews', 'goals': 0.72, 'assists': 0.48, 'points': 1.20, 'shots': 4.2},
        {'name': 'Mitch Marner', 'goals': 0.35, 'assists': 0.82, 'points': 1.17, 'shots': 2.8},
        {'name': 'William Nylander', 'goals': 0.42, 'assists': 0.58, 'points': 1.00, 'shots': 3.5},
        {'name': 'John Tavares', 'goals': 0.38, 'assists': 0.48, 'points': 0.86, 'shots': 2.8},
    ],
}


# ============ NBA LIVE API (when available) ============

class NBADataAPI:
    """NBA Data from NBA.com via nba_api package"""
    
    def __init__(self):
        self.available = NBA_API_AVAILABLE
    
    def is_available(self) -> bool:
        return self.available
    
    @st.cache_data(ttl=3600)
    def get_active_players(_self, limit: int = 100) -> pd.DataFrame:
        if not _self.available:
            return pd.DataFrame()
        
        try:
            all_players = nba_players.get_active_players()
            df = pd.DataFrame(all_players)
            
            # Get stats for top players
            player_data = []
            for _, player in df.head(limit).iterrows():
                stats = _self._get_player_stats(player['id'])
                if stats:
                    player_data.append({
                        'id': player['id'],
                        'full_name': f"{player['first_name']} {player['last_name']}",
                        **stats
                    })
            
            return pd.DataFrame(player_data)
        except Exception as e:
            return pd.DataFrame()
    
    def _get_player_stats(self, player_id: int) -> Optional[Dict]:
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            df = career.get_data_frames()[0]
            
            if df.empty:
                return None
            
            latest = df.iloc[-1]
            gp = max(latest.get('GP', 1), 1)
            
            return {
                'ppg': round(latest.get('PTS', 0) / gp, 1),
                'rpg': round(latest.get('REB', 0) / gp, 1),
                'apg': round(latest.get('AST', 0) / gp, 1),
                'fg_pct': round(latest.get('FG_PCT', 0), 3),
                'games': latest.get('GP', 0),
            }
        except:
            return None


# ============ UNIFIED INTERFACE ============

SPORT_CONFIG = {
    'NBA': {
        'teams': NBA_TEAMS,
        'props': {
            'Points': 'ppg',
            'Rebounds': 'rpg',
            'Assists': 'apg',
            'PRA': ['ppg', 'rpg', 'apg']
        },
        'has_live_api': NBA_API_AVAILABLE
    },
    'NFL': {
        'teams': NFL_TEAMS,
        'props': {
            'Pass Yards': 'pass_yds',
            'Pass TDs': 'pass_td',
            'Rush Yards': 'rush_yds',
            'Receptions': 'rec',
            'Rec Yards': 'rec_yds',
            'Anytime TD': ['rush_td', 'rec_td']
        },
        'has_live_api': False
    },
    'MLB': {
        'teams': MLB_TEAMS,
        'props': {
            'Hits': 'avg',
            'Home Runs': 'hr',
            'RBIs': 'rbi',
            'Total Bases': ['hr', 'rbi']
        },
        'has_live_api': False
    },
    'NHL': {
        'teams': NHL_TEAMS,
        'props': {
            'Goals': 'goals',
            'Assists': 'assists',
            'Points': 'points',
            'Shots': 'shots'
        },
        'has_live_api': False
    }
}


def get_sports() -> List[str]:
    """Get list of available sports."""
    return list(SPORT_CONFIG.keys())


def get_teams(sport: str) -> List[str]:
    """Get list of teams for a sport."""
    config = SPORT_CONFIG.get(sport)
    if not config:
        return []
    return list(config['teams'].keys())


def get_props(sport: str) -> List[str]:
    """Get list of prop types for a sport."""
    config = SPORT_CONFIG.get(sport)
    if not config:
        return []
    return list(config['props'].keys())


def get_team_players(sport: str, team: str) -> List[Dict]:
    """Get players for a team."""
    config = SPORT_CONFIG.get(sport)
    if not config:
        return []
    
    players = config['teams'].get(team, [])
    
    # For NBA, try live API first
    if sport == 'NBA' and NBA_API_AVAILABLE:
        try:
            api = NBADataAPI()
            live_data = api.get_active_players(limit=50)
            if not live_data.empty:
                # Filter by team would require additional logic
                # For now, return static with LIVE indicator
                pass
        except:
            pass
    
    return players


def get_player_stat(player: Dict, prop: str, sport: str) -> float:
    """Get the appropriate stat for a prop type."""
    config = SPORT_CONFIG.get(sport)
    if not config:
        return 0.0
    
    prop_key = config['props'].get(prop)
    
    if isinstance(prop_key, list):
        # Combined stat (e.g., PRA = Points + Rebounds + Assists)
        return sum(player.get(k, 0) for k in prop_key)
    
    return player.get(prop_key, 0.0)


def calculate_line(base_stat: float, sport: str) -> float:
    """Calculate prop line based on sport and stat."""
    if sport == 'NBA':
        return round(base_stat * 0.95 * 2) / 2
    elif sport == 'NFL':
        # Round to whole numbers for most NFL props
        return round(base_stat * 0.95)
    elif sport == 'MLB':
        # MLB props are different (binary or averages)
        if base_stat < 1:  # Batting average
            return round(base_stat * 100) / 100
        return round(base_stat * 0.95, 1)
    elif sport == 'NHL':
        return round(base_stat * 0.95, 2)
    return round(base_stat * 0.95, 1)


# Backwards compatibility
NBADataStatic = None  # Mark as deprecated
