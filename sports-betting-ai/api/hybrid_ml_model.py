#!/usr/bin/env python3
"""
Hybrid ML Model - Ensemble of weighted probability + ML prediction
Combines current weighted model with scikit-learn classifier
Based on research: University of Malta dissertation (2023)
"""

import json
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not available - using weighted model only")


class HybridMLModel:
    """
    Hybrid ensemble model combining:
    1. Weighted probability model (current system)
    2. ML classifier (Random Forest / Gradient Boosting)
    
    Returns ensemble prediction with confidence interval.
    """
    
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'ml_model.pkl')
        self.scaler_path = os.path.join(model_dir, 'ml_scaler.pkl')
        self.training_data_path = os.path.join(model_dir, 'ml_training_data.json')
        
        self.model = None
        self.scaler = None
        self.training_data = {'features': [], 'labels': []}
        
        # Load existing model if available
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk."""
        if not SKLEARN_AVAILABLE:
            return
        
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print(f"  ✅ Loaded ML model from {self.model_path}")
            except Exception as e:
                print(f"  ⚠️ Could not load ML model: {e}")
        
        # Load training data
        if os.path.exists(self.training_data_path):
            with open(self.training_data_path, 'r') as f:
                self.training_data = json.load(f)
                print(f"  ✅ Loaded {len(self.training_data['features'])} training samples")
    
    def save_model(self):
        """Save trained model to disk."""
        if not SKLEARN_AVAILABLE or self.model is None:
            return
        
        import joblib
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        with open(self.training_data_path, 'w') as f:
            json.dump(self.training_data, f, indent=2)
        
        print(f"  💾 Saved ML model to {self.model_path}")
    
    def extract_features(self, player_data: Dict, prop: Dict, game_context: Dict) -> np.ndarray:
        """
        Extract feature vector for ML model.
        
        Features (15 total):
        1-3: Historical hit rates (season, last5, last10)
        4-5: Usage rate, minutes
        6-7: Home/away splits
        8: Rest days
        9: Back-to-back flag
        10: Matchup rating
        11: Line vs season avg
        12: Line vs last5 avg
        13-15: Odds (American), implied probability, book margin
        """
        features = []
        
        # 1. Historical hit rate (most important feature per research)
        hist_rate = prop.get('historical_hit_rate')
        features.append((hist_rate if hist_rate else 50) / 100)
        
        # 2-3. Season avg hit rate estimate
        season_avg = player_data.get('pts', 0)
        line = prop.get('line', 0)
        season_hit_rate = 50 + (season_avg - line) * 8
        features.append(max(0, min(100, season_hit_rate)) / 100)
        
        # 4. Last 5 games hit rate estimate
        last5_avg = player_data.get('last5_pts', season_avg)
        last5_hit_rate = 50 + (last5_avg - line) * 10
        features.append(max(0, min(100, last5_hit_rate)) / 100)
        
        # 5-6. Usage rate & minutes (normalized)
        features.append(player_data.get('usage_rate', 25) / 40)  # League max ~40%
        features.append(player_data.get('minutes', 32) / 40)  # League max ~40 min
        
        # 7-8. Home/away performance
        home_split = player_data.get('home_pts', season_avg)
        away_split = player_data.get('away_pts', season_avg)
        is_home = 1 if game_context.get('is_home', False) else 0
        expected_avg = home_split if is_home else away_split
        home_away_hit_rate = 50 + (expected_avg - line) * 8
        features.append(max(0, min(100, home_away_hit_rate)) / 100)
        
        # 9. Rest days (0-3 scale)
        rest_days = game_context.get('rest_days', 1)
        features.append(min(rest_days, 3) / 3)
        
        # 10. Back-to-back flag
        features.append(1 if game_context.get('is_b2b', False) else 0)
        
        # 11. Matchup rating (-5 to +5, normalized)
        matchup = game_context.get('matchup_rating', 0)
        features.append((matchup + 5) / 10)
        
        # 12. Line vs season avg (value indicator)
        line_diff_season = (season_avg - line) / 10  # Normalize
        features.append(max(-1, min(1, line_diff_season)))
        
        # 13. Line vs last5 avg (form indicator)
        line_diff_last5 = (last5_avg - line) / 10
        features.append(max(-1, min(1, line_diff_last5)))
        
        # 14. Odds (normalized American)
        odds = prop.get('odds_over', -110)
        odds_normalized = odds / 300 if odds < 0 else odds / 500
        features.append(max(-1, min(1, odds_normalized)))
        
        # 15. Implied probability from odds
        implied_prob = abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100)
        features.append(implied_prob)
        
        return np.array(features)
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train ML model on historical data.
        
        X: Feature matrix (n_samples, n_features)
        y: Labels (n_samples,) - 1 if hit, 0 if miss
        """
        if not SKLEARN_AVAILABLE:
            print("  ⚠️ Cannot train - scikit-learn not available")
            return
        
        if len(X) < 50:
            print(f"  ⚠️ Need at least 50 samples, have {len(X)}")
            return
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Try multiple models, pick best
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42),
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
        }
        
        best_model = None
        best_score = 0
        best_name = ''
        
        for name, model in models.items():
            scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
            avg_score = scores.mean()
            print(f"  {name}: {avg_score*100:.1f}% accuracy (±{scores.std()*100:.1f}%)")
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
                best_name = name
        
        # Train best model on full dataset
        self.model = best_model
        self.model.fit(X_scaled, y)
        
        print(f"  ✅ Trained {best_name} with {best_score*100:.1f}% accuracy")
        print(f"  📊 Training samples: {len(X)}")
        
        # Save model
        self.save_model()
    
    def predict(self, features: np.ndarray) -> Tuple[float, float]:
        """
        Predict probability of prop hitting.
        
        Returns: (probability, confidence)
        - probability: 0-1 chance of hitting
        - confidence: 0-1 model confidence in prediction
        """
        if not SKLEARN_AVAILABLE or self.model is None or self.scaler is None:
            return 0.5, 0.0  # No prediction
        
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get probability
        prob = self.model.predict_proba(features_scaled)[0][1]
        
        # Estimate confidence based on distance from decision boundary
        # (closer to 0.5 = less confident)
        confidence = abs(prob - 0.5) * 2  # 0.0 to 1.0 scale
        
        return prob, confidence
    
    def add_training_sample(self, features: np.ndarray, label: int):
        """Add a new training sample (for online learning)."""
        self.training_data['features'].append(features.tolist())
        self.training_data['labels'].append(label)
        
        # Retrain every 100 new samples
        if len(self.training_data['features']) % 100 == 0:
            self.retrain()
    
    def retrain(self):
        """Retrain model on all accumulated data."""
        if len(self.training_data['features']) < 50:
            return
        
        X = np.array(self.training_data['features'])
        y = np.array(self.training_data['labels'])
        
        self.train(X, y)
    
    def ensemble_prediction(self, weighted_prob: float, ml_prob: float, ml_confidence: float) -> Tuple[float, str]:
        """
        Combine weighted model + ML model predictions.
        
        Strategy:
        - If ML confidence is high (>0.7): Weight ML at 60%, weighted model at 40%
        - If ML confidence is medium (0.4-0.7): Weight 50/50
        - If ML confidence is low (<0.4): Weight weighted model at 70%, ML at 30%
        
        Returns: (ensemble_probability, reasoning)
        """
        if ml_confidence > 0.7:
            ensemble_prob = weighted_prob * 0.4 + ml_prob * 0.6
            reasoning = "ML high confidence (60/40 split)"
        elif ml_confidence > 0.4:
            ensemble_prob = weighted_prob * 0.5 + ml_prob * 0.5
            reasoning = "Balanced ensemble (50/50 split)"
        else:
            ensemble_prob = weighted_prob * 0.7 + ml_prob * 0.3
            reasoning = "Weighted model dominant (70/30 split)"
        
        return round(ensemble_prob * 100, 1), reasoning


def create_training_data_from_cache(cache_dir: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create training dataset from historical cache files.
    
    For each historical prediction, extract features and label (hit/miss).
    Note: Would need actual game results to label correctly.
    """
    features_list = []
    labels_list = []
    
    # Load historical caches
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cache_file = os.path.join(cache_dir, f'player_props_cache_{date}.json')
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                
                for bet in cache.get('best_bets', []):
                    # Would need actual game result to label
                    # For now, skip (or use mock labels for testing)
                    pass
    
    return np.array(features_list), np.array(labels_list)


def main():
    """Test hybrid ML model."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model = HybridMLModel(script_dir)
    
    # Mock player data
    player_data = {
        'pts': 27.5,
        'last5_pts': 31.5,
        'usage_rate': 33.8,
        'minutes': 34.5,
        'home_pts': 29.2,
        'away_pts': 25.8,
    }
    
    # Mock prop
    prop = {
        'line': 27.5,
        'odds_over': -115,
        'historical_hit_rate': 57.7,  # 30/52 games
    }
    
    # Mock game context
    game_context = {
        'is_home': True,
        'rest_days': 1,
        'is_b2b': False,
        'matchup_rating': 2,  # Favorable
    }
    
    # Extract features
    features = model.extract_features(player_data, prop, game_context)
    print(f"\n📊 Feature vector ({len(features)} features):")
    print(f"  {features}")
    
    # Get ML prediction
    ml_prob, ml_conf = model.predict(features)
    print(f"\n🤖 ML Prediction:")
    print(f"  Probability: {ml_prob*100:.1f}%")
    print(f"  Confidence: {ml_conf*100:.1f}%")
    
    # Get weighted model prediction (from current system)
    weighted_prob = 60.3 / 100  # Example from current model
    
    # Ensemble
    ensemble_prob, reasoning = model.ensemble_prediction(weighted_prob, ml_prob, ml_conf)
    print(f"\n🎯 Ensemble Prediction:")
    print(f"  Weighted Model: {weighted_prob*100:.1f}%")
    print(f"  ML Model: {ml_prob*100:.1f}%")
    print(f"  **Ensemble: {ensemble_prob}%**")
    print(f"  Strategy: {reasoning}")


if __name__ == '__main__':
    from datetime import timedelta
    main()
