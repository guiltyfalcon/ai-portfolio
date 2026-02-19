"""
Advanced Data Processor - Feature engineering for ML models
Includes player stats, injuries, rest days, advanced metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from datetime import datetime, timedelta

class AdvancedDataProcessor:
    """Advanced feature engineering for sports prediction."""
    
    def __init__(self):
        self.team_stats_cache = {}
        self.player_stats_cache = {}
    
    def parse_record(self, record: str) -> Tuple[int, int]:
        """Parse win-loss record."""
        if not record or record == '0-0':
            return 0, 0
        try:
            wins, losses = map(int, str(record).split('-'))
            return wins, losses
        except:
            return 0, 0
    
    def calculate_win_pct(self, wins: int, losses: int) -> float:
        """Calculate win percentage."""
        total = wins + losses
        return wins / total if total > 0 else 0.5
    
    def calculate_elo_rating(self, wins: int, losses: int, base: int = 1500) -> float:
        """Simple ELO rating calculation."""
        win_pct = self.calculate_win_pct(wins, losses)
        # Adjust based on win percentage
        rating = base + (win_pct - 0.5) * 400
        return rating
    
    def calculate_rest_days(self, last_game_date: Optional[str], current_date: str) -> int:
        """Calculate days since last game."""
        if not last_game_date:
            return 3  # Assume average rest
        try:
            last = pd.to_datetime(last_game_date)
            current = pd.to_datetime(current_date)
            return (current - last).days
        except:
            return 3
    
    def create_advanced_features(self, schedule: pd.DataFrame, 
                                   team_stats: pd.DataFrame,
                                   injuries: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Create comprehensive features for ML models.
        
        Features include:
        - Win percentages
        - ELO ratings
        - Rest days
        - Home court advantage
        - Key player injuries
        - Recent form (last 5 games)
        - Point differential
        - Pace/opponent strength
        """
        features = []
        
        # Build team lookup
        team_lookup = {}
        for _, team in team_stats.iterrows():
            team_id = str(team.get('id', team.get('team_id')))
            if not team_id:
                continue
            
            record = team.get('record', '0-0')
            wins, losses = self.parse_record(record)
            
            team_lookup[team_id] = {
                'name': team.get('name', ''),
                'wins': wins,
                'losses': losses,
                'win_pct': self.calculate_win_pct(wins, losses),
                'elo': self.calculate_elo_rating(wins, losses),
                'avg_points': team.get('points_for', 0),
                'avg_allowed': team.get('points_against', 0),
                'point_diff': team.get('points_for', 0) - team.get('points_against', 0)
            }
        
        # Build injury lookup
        injury_counts = {}
        if injuries is not None and not injuries.empty:
            injury_counts = injuries.groupby('team_id').size().to_dict()
        
        for _, game in schedule.iterrows():
            home_id = str(game.get('home_team_id', ''))
            away_id = str(game.get('away_team_id', ''))
            
            home_stats = team_lookup.get(home_id, {
                'wins': 0, 'losses': 0, 'win_pct': 0.5, 'elo': 1500,
                'avg_points': 100, 'avg_allowed': 100, 'point_diff': 0
            })
            
            away_stats = team_lookup.get(away_id, {
                'wins': 0, 'losses': 0, 'win_pct': 0.5, 'elo': 1500,
                'avg_points': 100, 'avg_allowed': 100, 'point_diff': 0
            })
            
            # Calculate rest days (if game date available)
            game_date = game.get('date', game.get('scheduled', datetime.now()))
            if isinstance(game_date, str):
                game_date = pd.to_datetime(game_date)
            
            feature = {
                'game_id': game.get('game_id', game.get('id')),
                'home_team': game.get('home_team', game.get('home', {}).get('name', 'TBD')),
                'away_team': game.get('away_team', game.get('away', {}).get('name', 'TBD')),
                
                # Basic features
                'home_win_pct': home_stats['win_pct'],
                'away_win_pct': away_stats['win_pct'],
                'win_pct_diff': home_stats['win_pct'] - away_stats['win_pct'],
                
                'home_elo': home_stats['elo'],
                'away_elo': away_stats['elo'],
                'elo_diff': home_stats['elo'] - away_stats['elo'],
                
                # Strength metrics
                'home_avg_points': home_stats['avg_points'],
                'home_avg_allowed': home_stats['avg_allowed'],
                'home_point_diff': home_stats['point_diff'],
                'away_avg_points': away_stats['avg_points'],
                'away_avg_allowed': away_stats['avg_allowed'],
                'away_point_diff': away_stats['point_diff'],
                
                'point_diff_diff': home_stats['point_diff'] - away_stats['point_diff'],
                
                # Schedule factors
                'home_advantage': 1.0,
                'home_rest_days': 2,  # Placeholder
                'away_rest_days': 2,  # Placeholder
                
                # Injury impact
                'home_injuries': injury_counts.get(home_id, 0),
                'away_injuries': injury_counts.get(away_id, 0),
                'injury_diff': injury_counts.get(away_id, 0) - injury_counts.get(home_id, 0),
                
                # Experience (games played)
                'home_games': home_stats['wins'] + home_stats['losses'],
                'away_games': away_stats['wins'] + away_stats['losses'],
                'experience_diff': (home_stats['wins'] + home_stats['losses']) - 
                                  (away_stats['wins'] + away_stats['losses']),
                
                # Interactions
                'win_pct_x_home': home_stats['win_pct'] * 1.0,
                'elo_x_home': (home_stats['elo'] - 1500) / 100,
            }
            
            features.append(feature)
        
        return pd.DataFrame(features)
    
    def merge_with_odds_advanced(self, features: pd.DataFrame, 
                                   odds: pd.DataFrame,
                                   calculate_value: bool = True) -> pd.DataFrame:
        """
        Merge features with odds and calculate value bets.
        
        Adds columns:
        - implied_prob_home/away
        - model_prob_home/away (from features)
        - value_edge_home/away
        - is_value_bet
        """
        def odds_to_implied(odds):
            if pd.isna(odds):
                return 0.5
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        def calculate_model_prob(row):
            """Simple model: win_pct + home_advantage + elo_adjustment"""
            base_prob = (row['home_win_pct'] + 0.5 - row['away_win_pct']) / 2
            elo_adj = (row['elo_diff'] / 400) * 0.1
            point_adj = (row['point_diff_diff'] / 10) * 0.1
            home_adv = 0.03
            
            prob = base_prob + elo_adj + point_adj + home_adj - row['home_injuries'] * 0.02
            return min(max(prob, 0.1), 0.9)
        
        # Merge on team names
        merged = features.merge(
            odds[['home_team', 'away_team', 'home_ml', 'away_ml']],
            left_on=['home_team', 'away_team'],
            right_on=['home_team', 'away_team'],
            how='left'
        )
        
        # Calculate implied probabilities
        merged['implied_prob_home'] = merged['home_ml'].apply(odds_to_implied)
        merged['implied_prob_away'] = merged['away_ml'].apply(odds_to_implied)
        
        # Calculate model probabilities
        merged['model_prob_home'] = merged.apply(lambda x: calculate_model_prob(x), axis=1)
        merged['model_prob_away'] = 1 - merged['model_prob_home']
        
        # Calculate value
        merged['value_edge_home'] = merged['model_prob_home'] - merged['implied_prob_home']
        merged['value_edge_away'] = merged['model_prob_away'] - merged['implied_prob_away']
        merged['max_edge'] = merged[['value_edge_home', 'value_edge_away']].max(axis=1)
        merged['is_value_bet'] = merged['max_edge'] > 0.05
        
        return merged

if __name__ == "__main__":
    processor = AdvancedDataProcessor()
    print("Advanced Data Processor ready")
