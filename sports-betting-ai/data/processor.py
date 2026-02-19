"""
Data Processor - Feature engineering for sports prediction models
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta

class SportsDataProcessor:
    """Process raw sports data into ML-ready features."""
    
    def __init__(self):
        self.feature_columns = []
    
    def parse_record(self, record: str) -> Tuple[int, int]:
        """Parse win-loss record string."""
        if not record or record == '0-0':
            return 0, 0
        try:
            parts = record.split('-')
            return int(parts[0]), int(parts[1])
        except:
            return 0, 0
    
    def calculate_win_pct(self, wins: int, losses: int) -> float:
        """Calculate win percentage."""
        total = wins + losses
        return wins / total if total > 0 else 0.5
    
    def calculate_elo(self, team_id: str, games_df: pd.DataFrame, base_elo: int = 1500, k: int = 20) -> float:
        """Calculate ELO rating for a team."""
        # Simplified ELO calculation
        # In production, you'd maintain ELO across seasons
        return base_elo
    
    def create_game_features(self, schedule_df: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for each game.
        
        Features:
        - Home/away win percentages
        - Home court advantage
        - Rest days (schedule density)
        - ELO ratings
        - Head-to-head history
        """
        features = []
        
        # Build team stats lookup
        team_stats = {}
        for _, team in teams_df.iterrows():
            wins, losses = self.parse_record(team.get('record', '0-0'))
            team_stats[team['id']] = {
                'name': team['name'],
                'wins': wins,
                'losses': losses,
                'win_pct': self.calculate_win_pct(wins, losses)
            }
        
        for _, game in schedule_df.iterrows():
            home_id = str(game.get('home_team_id'))
            away_id = str(game.get('away_team_id'))
            
            home_stats = team_stats.get(home_id, {'wins': 0, 'losses': 0, 'win_pct': 0.5})
            away_stats = team_stats.get(away_id, {'wins': 0, 'losses': 0, 'win_pct': 0.5})
            
            # Basic features
            feature = {
                'game_id': game.get('game_id'),
                'home_team': game.get('home_team'),
                'away_team': game.get('away_team'),
                'commence_time': game.get('date'),
                
                # Win percentages
                'home_win_pct': home_stats['win_pct'],
                'away_win_pct': away_stats['win_pct'],
                'win_pct_diff': home_stats['win_pct'] - away_stats['win_pct'],
                
                # Record breakdown
                'home_wins': home_stats['wins'],
                'home_losses': home_stats['losses'],
                'away_wins': away_stats['wins'],
                'away_losses': away_stats['losses'],
                
                # Home court advantage feature
                'home_advantage': 1.0,  # Binary flag
                
                # Total games played (experience proxy)
                'home_games_played': home_stats['wins'] + home_stats['losses'],
                'away_games_played': away_stats['wins'] + away_stats['losses'],
            }
            
            # Advanced features
            feature['home_advantage_x_win_pct'] = feature['home_advantage'] * feature['home_win_pct']
            feature['rest_advantage'] = 0  # Would calculate from previous game dates
            
            features.append(feature)
        
        return pd.DataFrame(features)
    
    def merge_with_odds(self, features_df: pd.DataFrame, odds_df: pd.DataFrame) -> pd.DataFrame:
        """Merge game features with betting odds."""
        # Match games by team names (fuzzy matching in production)
        merged = features_df.merge(
            odds_df,
            left_on=['home_team', 'away_team'],
            right_on=['home_team', 'away_team'],
            how='left'
        )
        
        # Calculate implied probabilities
        def american_to_prob(odds):
            if pd.isna(odds):
                return 0.5
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        if 'home_ml' in merged.columns:
            merged['home_implied_prob'] = merged['home_ml'].apply(american_to_prob)
            merged['away_implied_prob'] = merged['away_ml'].apply(american_to_prob)
        
        return merged
    
    def prepare_training_data(self, historical_games: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare historical game data for model training.
        
        Args:
            historical_games: DataFrame with game features and results
            
        Returns:
            X: Feature matrix
            y: Target vector (1 if home team won, 0 otherwise)
        """
        # Feature columns for model
        feature_cols = [
            'home_win_pct', 'away_win_pct', 'win_pct_diff',
            'home_wins', 'home_losses', 'away_wins', 'away_losses',
            'home_advantage', 'home_games_played', 'away_games_played',
            'home_advantage_x_win_pct'
        ]
        
        X = historical_games[feature_cols].fillna(0)
        y = historical_games['home_team_won'].fillna(0)  # Target column
        
        return X, y

if __name__ == "__main__":
    # Test with sample data
    processor = SportsDataProcessor()
    
    sample_schedule = pd.DataFrame([
        {'game_id': '1', 'home_team': 'Lakers', 'home_team_id': '1', 'away_team': 'Warriors', 'away_team_id': '2', 'date': '2024-01-01', 'home_record': '20-10', 'away_record': '18-12'},
        {'game_id': '2', 'home_team': 'Celtics', 'home_team_id': '3', 'away_team': 'Heat', 'away_team_id': '4', 'date': '2024-01-01', 'home_record': '25-5', 'away_record': '15-15'}
    ])
    
    sample_teams = pd.DataFrame([
        {'id': '1', 'name': 'Lakers', 'record': '20-10'},
        {'id': '2', 'name': 'Warriors', 'record': '18-12'},
        {'id': '3', 'name': 'Celtics', 'record': '25-5'},
        {'id': '4', 'name': 'Heat', 'record': '15-15'}
    ])
    
    features = processor.create_game_features(sample_schedule, sample_teams)
    print("Generated features:")
    print(features)
