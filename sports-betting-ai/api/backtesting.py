#!/usr/bin/env python3
"""
Backtesting Module - Validate hit probability model against historical results
Tests model accuracy by comparing predictions to actual game outcomes
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics


def load_historical_predictions(cache_path: str) -> List[Dict]:
    """Load historical player props predictions from cache files."""
    predictions = []
    
    # Load last 30 days of caches
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cache_file = cache_path.replace('player_props_cache.json', f'player_props_cache_{date}.json')
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                predictions.extend(cache.get('best_bets', []))
    
    return predictions


def fetch_actual_game_results(game_date: str) -> Dict:
    """
    Fetch actual box scores for a specific date.
    Returns: {player_name: {pts, reb, ast, ...}}
    """
    # Would use BallDontLie or NBA API to fetch actual results
    # For now, return mock structure
    return {}


def calculate_prediction_accuracy(predictions: List[Dict], actual_results: Dict) -> Dict:
    """
    Calculate model accuracy metrics.
    
    Returns:
    - Overall accuracy %
    - Accuracy by hit rate bucket (70-75%, 75-80%, etc.)
    - Brier score (probability calibration)
    - ROI if betting all predictions
    """
    correct = 0
    total = 0
    brier_scores = []
    roi_total = 0
    stake_per_bet = 100  # $100 per bet
    
    # Group by predicted hit rate buckets
    buckets = {
        '70-75%': {'correct': 0, 'total': 0},
        '75-80%': {'correct': 0, 'total': 0},
        '80-85%': {'correct': 0, 'total': 0},
        '85-90%': {'correct': 0, 'total': 0},
        '90%+': {'correct': 0, 'total': 0},
    }
    
    for pred in predictions:
        player = pred.get('player', '')
        prop_type = pred.get('prop', '').split()[0]  # e.g., "Pts" from "Pts OVER 27.5"
        line = float(pred.get('prop', '0').split()[-1])
        predicted_prob = pred.get('hit_probability', 50) / 100
        odds = pred.get('odds', -110)
        
        # Get actual stat from results
        actual_stat = actual_results.get(player, {}).get(prop_type.lower(), 0)
        
        # Determine if prediction was correct
        hit = actual_stat >= line
        total += 1
        
        if hit:
            correct += 1
            
            # Calculate ROI
            if odds < 0:
                profit = stake_per_bet * (100 / abs(odds))
            else:
                profit = stake_per_bet * (odds / 100)
            roi_total += profit
        else:
            roi_total -= stake_per_bet
        
        # Brier score (measures probability calibration)
        actual_outcome = 1 if hit else 0
        brier = (predicted_prob - actual_outcome) ** 2
        brier_scores.append(brier)
        
        # Bucket by predicted probability
        pred_pct = pred.get('hit_probability', 50)
        if pred_pct >= 90:
            buckets['90%+']['total'] += 1
            if hit:
                buckets['90%+']['correct'] += 1
        elif pred_pct >= 85:
            buckets['85-90%']['total'] += 1
            if hit:
                buckets['85-90%']['correct'] += 1
        elif pred_pct >= 80:
            buckets['80-85%']['total'] += 1
            if hit:
                buckets['80-85%']['correct'] += 1
        elif pred_pct >= 75:
            buckets['75-80%']['total'] += 1
            if hit:
                buckets['75-80%']['correct'] += 1
        elif pred_pct >= 70:
            buckets['70-75%']['total'] += 1
            if hit:
                buckets['70-75%']['correct'] += 1
    
    # Calculate metrics
    accuracy = correct / total * 100 if total > 0 else 0
    avg_brier = statistics.mean(brier_scores) if brier_scores else 0
    total_staked = total * stake_per_bet
    roi_pct = (roi_total / total_staked) * 100 if total_staked > 0 else 0
    
    return {
        'total_predictions': total,
        'correct_predictions': correct,
        'accuracy_pct': round(accuracy, 1),
        'avg_brier_score': round(avg_brier, 3),
        'total_roi_pct': round(roi_pct, 1),
        'net_profit': round(roi_total, 2),
        'total_staked': total_staked,
        'buckets': {
            k: {
                'accuracy': round(v['correct'] / v['total'] * 100, 1) if v['total'] > 0 else 0,
                'total': v['total'],
                'correct': v['correct']
            }
            for k, v in buckets.items()
        }
    }


def generate_backtest_report(accuracy_metrics: Dict) -> str:
    """Generate a readable backtest report."""
    report = []
    report.append("=" * 60)
    report.append("📊 BACKTEST RESULTS - Model Accuracy Validation")
    report.append("=" * 60)
    report.append("")
    report.append(f"Total Predictions: {accuracy_metrics['total_predictions']}")
    report.append(f"Correct: {accuracy_metrics['correct_predictions']}")
    report.append(f"**Accuracy: {accuracy_metrics['accuracy_pct']}%**")
    report.append("")
    report.append("### Probability Calibration (Brier Score)")
    report.append(f"Brier Score: {accuracy_metrics['avg_brier_score']} (lower is better, 0.0 = perfect)")
    report.append("")
    report.append("### Betting Performance")
    report.append(f"Total Staked: ${accuracy_metrics['total_staked']:,}")
    report.append(f"Net Profit: ${accuracy_metrics['net_profit']:,}")
    report.append(f"**ROI: {accuracy_metrics['total_roi_pct']}%**")
    report.append("")
    report.append("### Accuracy by Confidence Bucket")
    report.append("")
    
    for bucket, data in accuracy_metrics['buckets'].items():
        report.append(f"- **{bucket}**: {data['accuracy']}% ({data['correct']}/{data['total']})")
    
    report.append("")
    report.append("### Interpretation")
    report.append("")
    
    if accuracy_metrics['accuracy_pct'] >= 70:
        report.append("✅ Model is performing WELL - accuracy above 70%")
    elif accuracy_metrics['accuracy_pct'] >= 60:
        report.append("⚠️ Model is performing OKAY - accuracy 60-70%")
    else:
        report.append("❌ Model needs IMPROVEMENT - accuracy below 60%")
    
    if accuracy_metrics['total_roi_pct'] > 0:
        report.append("✅ Betting strategy is PROFITABLE")
    else:
        report.append("⚠️ Betting strategy is LOSING money")
    
    return "\n".join(report)


def run_backtest(cache_dir: str) -> Dict:
    """Run full backtest and return results."""
    print("🔍 Running backtest...")
    
    # Load historical predictions
    predictions = load_historical_predictions(cache_dir)
    
    if not predictions:
        print("⚠️ No historical predictions found")
        return {'error': 'No data'}
    
    print(f"  Loaded {len(predictions)} historical predictions")
    
    # For each prediction date, fetch actual results
    # (This would need to be implemented with real API calls)
    actual_results = {}  # Would fetch from NBA API
    
    # Calculate accuracy
    accuracy = calculate_prediction_accuracy(predictions, actual_results)
    
    # Generate report
    report = generate_backtest_report(accuracy)
    print("\n" + report)
    
    return accuracy


def main():
    """Run backtest on historical data."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = script_dir
    
    results = run_backtest(cache_dir)
    
    # Save results
    results_path = os.path.join(script_dir, 'backtest_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to {results_path}")


if __name__ == '__main__':
    main()
