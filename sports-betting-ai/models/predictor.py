"""
Prediction Models - Neural network and ensemble models for sports prediction
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, brier_score_loss, classification_report
from typing import Tuple, Dict, Optional
import joblib
import os

class SportsPredictionModel:
    """Ensemble model for predicting sports game outcomes."""
    
    def __init__(self, sport: str, model_type: str = 'ensemble'):
        self.sport = sport.lower()
        self.model_type = model_type
        self.models = {}
        self.is_trained = False
        self.feature_cols = [
            'home_win_pct', 'away_win_pct', 'win_pct_diff',
            'home_advantage', 'home_games_played', 'away_games_played'
        ]
    
    def train(self, X: pd.DataFrame, y: pd.Series, validation_split: float = 0.2) -> Dict:
        """
        Train the prediction model.
        
        Args:
            X: Feature matrix
            y: Target vector (1 = home win, 0 = away win)
            validation_split: Fraction for validation
            
        Returns:
            Training metrics dictionary
        """
        # Ensure we only use available features
        available_cols = [col for col in self.feature_cols if col in X.columns]
        X = X[available_cols].fillna(0)
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        metrics = {}
        
        # Train Random Forest
        print("Training Random Forest...")
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        self.models['random_forest'] = rf
        
        rf_pred = rf.predict(X_val)
        rf_prob = rf.predict_proba(X_val)[:, 1]
        metrics['random_forest'] = {
            'accuracy': accuracy_score(y_val, rf_pred),
            'brier_score': brier_score_loss(y_val, rf_prob)
        }
        
        # Train Gradient Boosting
        print("Training Gradient Boosting...")
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb.fit(X_train, y_train)
        self.models['gradient_boosting'] = gb
        
        gb_pred = gb.predict(X_val)
        gb_prob = gb.predict_proba(X_val)[:, 1]
        metrics['gradient_boosting'] = {
            'accuracy': accuracy_score(y_val, gb_pred),
            'brier_score': brier_score_loss(y_val, gb_prob)
        }
        
        # Train Logistic Regression
        print("Training Logistic Regression...")
        lr = LogisticRegression(random_state=42)
        lr.fit(X_train, y_train)
        self.models['logistic_regression'] = lr
        
        lr_pred = lr.predict(X_val)
        lr_prob = lr.predict_proba(X_val)[:, 1]
        metrics['logistic_regression'] = {
            'accuracy': accuracy_score(y_val, lr_pred),
            'brier_score': brier_score_loss(y_val, lr_prob)
        }
        
        self.is_trained = True
        self.feature_cols = available_cols
        
        print("\nTraining complete. Metrics:")
        for model_name, model_metrics in metrics.items():
            print(f"  {model_name}: Acc={model_metrics['accuracy']:.3f}, Brier={model_metrics['brier_score']:.3f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions using the ensemble.
        
        Returns DataFrame with home_win_prob and predictions from each model.
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before predicting")
        
        X = X[self.feature_cols].fillna(0)
        
        predictions = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            prob = model.predict_proba(X)[:, 1]
            predictions[name] = prob
        
        # Ensemble prediction (average)
        all_probs = np.array(list(predictions.values()))
        ensemble_prob = np.mean(all_probs, axis=0)
        
        results = pd.DataFrame({
            'home_win_prob': ensemble_prob,
            'away_win_prob': 1 - ensemble_prob,
            **{f'{name}_prob': prob for name, prob in predictions.items()}
        })
        
        return results
    
    def save(self, filepath: str):
        """Save the trained model."""
        if not self.is_trained:
            print("Model not trained, nothing to save")
            return
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump({
                'models': self.models,
                'feature_cols': self.feature_cols,
                'sport': self.sport,
                'is_trained': self.is_trained
            }, filepath)
            print(f"Model saved to {filepath}")
        except Exception as e:
            print(f"Warning: Could not save model: {e}")
    
    def load(self, filepath: str):
        """Load a trained model."""
        data = joblib.load(filepath)
        self.models = data['models']
        self.feature_cols = data['feature_cols']
        self.sport = data['sport']
        self.is_trained = data['is_trained']

if __name__ == "__main__":
    # Test with dummy data
    print("Testing SportsPredictionModel...")
    
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 500
    
    X = pd.DataFrame({
        'home_win_pct': np.random.uniform(0.3, 0.8, n_samples),
        'away_win_pct': np.random.uniform(0.3, 0.8, n_samples),
        'win_pct_diff': np.random.uniform(-0.3, 0.3, n_samples),
        'home_advantage': np.ones(n_samples),
        'home_games_played': np.random.randint(10, 50, n_samples),
        'away_games_played': np.random.randint(10, 50, n_samples)
    })
    
    # Synthetic target: home team wins more often with higher win_pct and home advantage
    y = (X['home_win_pct'] - X['away_win_pct'] + 0.1 * X['home_advantage'] + np.random.normal(0, 0.1, n_samples) > 0).astype(int)
    
    model = SportsPredictionModel('nba')
    metrics = model.train(X, y)
    
    # Test prediction
    test_games = X.head(5)
    preds = model.predict(test_games)
    print("\nSample predictions:")
    print(preds[['home_win_prob', 'away_win_prob']])
