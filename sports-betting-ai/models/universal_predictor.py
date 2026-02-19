"""
Universal Sports Predictor - Works with NBA, NFL, MLB, NHL
Sport-specific feature engineering and models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, brier_score_loss
import joblib
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class UniversalSportsPredictor:
    """Universal predictor for NBA, NFL, MLB, NHL."""
    
    def __init__(self, sport: str):
        self.sport = sport.lower()
        self.models = {}
        self.is_trained = False
        self.feature_importance = {}
        
        # Sport-specific configurations
        self.config = self._get_sport_config()
        self.feature_cols = self._get_feature_columns()
    
    def _get_sport_config(self) -> Dict:
        """Get sport-specific configuration."""
        configs = {
            'nba': {
                'home_advantage': 0.04,
                'k_factor': 20,
                'base_elo': 1500,
                'pace_factor': True,
                'player_importance': 0.3
            },
            'nfl': {
                'home_advantage': 0.03,
                'k_factor': 15,
                'base_elo': 1500,
                'pace_factor': False,
                'player_importance': 0.25
            },
            'mlb': {
                'home_advantage': 0.02,
                'k_factor': 10,
                'base_elo': 1500,
                'pace_factor': False,
                'player_importance': 0.2
            },
            'nhl': {
                'home_advantage': 0.025,
                'k_factor': 12,
                'base_elo': 1500,
                'pace_factor': False,
                'player_importance': 0.25
            }
        }
        return configs.get(self.sport, configs['nba'])
    
    def _get_feature_columns(self) -> List[str]:
        """Get feature columns for this sport."""
        base_features = [
            'home_win_pct', 'away_win_pct', 'win_pct_diff',
            'home_elo', 'away_elo', 'elo_diff',
            'home_point_diff', 'away_point_diff', 'point_diff_diff',
            'home_rest_days', 'away_rest_days', 'rest_diff',
            'home_advantage'
        ]
        
        sport_specific = {
            'nba': ['home_or', 'away_or', 'pace_diff'],  # Offensive rating, pace
            'nfl': ['home_offensive_rank', 'away_defensive_rank', 'turnover_diff'],
            'mlb': ['home_era', 'away_era', 'batting_avg_diff', 'starter_quality'],
            'nhl': ['home_goals_per_game', 'away_goals_allowed', 'power_play_diff']
        }
        
        return base_features + sport_specific.get(self.sport, [])
    
    def calculate_elo(self, wins: int, losses: int, base: int = 1500) -> float:
        """Calculate ELO rating."""
        total = wins + losses
        if total == 0:
            return base
        win_pct = wins / total
        # ELO adjustment based on win percentage
        rating = base + (win_pct - 0.5) * 400
        return rating
    
    def engineer_features(self, games_df: pd.DataFrame, 
                          teams_df: pd.DataFrame,
                          stats_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Engineer features for all games.
        
        Returns DataFrame with prediction features.
        """
        features = []
        config = self.config
        
        # Build team lookup
        team_data = {}
        for _, team in teams_df.iterrows():
            team_id = team.get('id', team.get('team_id'))
            if not team_id:
                continue
            
            record = team.get('record', '0-0')
            if isinstance(record, str) and '-' in record:
                try:
                    wins, losses = map(int, record.split('-'))
                except:
                    wins, losses = 0, 0
            else:
                wins, losses = 0, 0
            
            team_data[team_id] = {
                'wins': wins,
                'losses': losses,
                'win_pct': wins / (wins + losses) if (wins + losses) > 0 else 0.5,
                'elo': self.calculate_elo(wins, losses, config['base_elo']),
                'points_for': team.get('points_for', 100),
                'points_against': team.get('points_against', 100),
                'point_diff': team.get('points_for', 100) - team.get('points_against', 100)
            }
        
        for _, game in games_df.iterrows():
            home_id = game.get('home_team_id', game.get('home_id'))
            away_id = game.get('away_team_id', game.get('away_id'))
            
            home = team_data.get(home_id, {'wins': 0, 'losses': 0, 'win_pct': 0.5, 
                                           'elo': 1500, 'point_diff': 0})
            away = team_data.get(away_id, {'wins': 0, 'losses': 0, 'win_pct': 0.5, 
                                           'elo': 1500, 'point_diff': 0})
            
            feature = {
                'game_id': game.get('game_id', game.get('id')),
                'home_team': game.get('home_team', game.get('home_name')),
                'away_team': game.get('away_team', game.get('away_name')),
                
                # Core features
                'home_win_pct': home['win_pct'],
                'away_win_pct': away['win_pct'],
                'win_pct_diff': home['win_pct'] - away['win_pct'],
                
                'home_elo': home['elo'],
                'away_elo': away['elo'],
                'elo_diff': home['elo'] - away['elo'],
                
                'home_point_diff': home['point_diff'],
                'away_point_diff': away['point_diff'],
                'point_diff_diff': home['point_diff'] - away['point_diff'],
                
                'home_rest_days': 2,  # Default
                'away_rest_days': 2,
                'rest_diff': 0,
                
                'home_advantage': config['home_advantage']
            }
            
            # Sport-specific features
            if self.sport == 'nba':
                feature.update({
                    'home_or': home.get('offensive_rating', 110),
                    'away_or': away.get('offensive_rating', 110),
                    'pace_diff': 0
                })
            elif self.sport == 'nfl':
                feature.update({
                    'home_offensive_rank': 16,  # Middle rank
                    'away_defensive_rank': 16,
                    'turnover_diff': 0
                })
            elif self.sport == 'mlb':
                feature.update({
                    'home_era': 4.0,
                    'away_era': 4.0,
                    'batting_avg_diff': 0,
                    'starter_quality': 0.5
                })
            elif self.sport == 'nhl':
                feature.update({
                    'home_goals_per_game': 3.0,
                    'away_goals_allowed': 3.0,
                    'power_play_diff': 0
                })
            
            features.append(feature)
        
        result = pd.DataFrame(features)
        
        # Fill missing columns needed for prediction
        for col in self.feature_cols:
            if col not in result.columns:
                result[col] = 0
        
        return result
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train ensemble model."""
        # Ensure we have all features
        for col in self.feature_cols:
            if col not in X.columns:
                X[col] = 0
        
        X = X[[col for col in self.feature_cols if col in X.columns]].fillna(0)
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        metrics = {}
        
        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        self.models['random_forest'] = rf
        
        rf_pred = rf.predict_proba(X_val)[:, 1]
        metrics['random_forest'] = {
            'accuracy': accuracy_score(y_val, rf.predict(X_val)),
            'brier_score': brier_score_loss(y_val, rf_pred)
        }
        
        # Gradient Boosting
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb.fit(X_train, y_train)
        self.models['gradient_boosting'] = gb
        
        gb_pred = gb.predict_proba(X_val)[:, 1]
        metrics['gradient_boosting'] = {
            'accuracy': accuracy_score(y_val, gb.predict(X_val)),
            'brier_score': brier_score_loss(y_val, gb_pred)
        }
        
        # Logistic Regression
        lr = LogisticRegression(random_state=42)
        lr.fit(X_train, y_train)
        self.models['logistic_regression'] = lr
        
        lr_pred = lr.predict_proba(X_val)[:, 1]
        metrics['logistic_regression'] = {
            'accuracy': accuracy_score(y_val, lr.predict(X_val)),
            'brier_score': brier_score_loss(y_val, lr_pred)
        }
        
        self.is_trained = True
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """Generate predictions."""
        if not self.is_trained:
            # Use heuristic if not trained
            home_prob = X['home_win_pct'] * 0.6 + 0.5 * 0.4 + self.config['home_advantage']
            home_prob = np.clip(home_prob, 0.1, 0.9)
            return pd.DataFrame({
                'home_win_prob': home_prob,
                'away_win_prob': 1 - home_prob
            })
        
        for col in self.feature_cols:
            if col not in X.columns:
                X[col] = 0
        
        X = X[self.feature_cols].fillna(0)
        
        probs = []
        for name, model in self.models.items():
            prob = model.predict_proba(X)[:, 1]
            probs.append(prob)
        
        ensemble = np.mean(probs, axis=0)
        
        return pd.DataFrame({
            'home_win_prob': ensemble,
            'away_win_prob': 1 - ensemble
        })

if __name__ == "__main__":
    # Test all sports
    for sport in ['nba', 'nfl', 'mlb', 'nhl']:
        model = UniversalSportsPredictor(sport)
        print(f"{sport.upper()} model ready")
        print(f"  Features: {len(model.feature_cols)}")
        print(f"  Home advantage: {model.config['home_advantage']}")
