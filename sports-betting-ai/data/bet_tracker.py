"""
Bet Tracker - Track picks, stakes, results, ROI
Stores bets persistently using Streamlit session state + CSV backup
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

class BetTracker:
    """Track all bets with persistence."""
    
    def __init__(self, data_dir: str = "/mount/data"):
        self.data_dir = data_dir
        self.bets_file = os.path.join(data_dir, "bets.json")
        self.bankroll_file = os.path.join(data_dir, "bankroll.json")
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """Create data directory if needed."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_bets(self) -> pd.DataFrame:
        """Load all bets from storage."""
        if os.path.exists(self.bets_file):
            with open(self.bets_file, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        return pd.DataFrame(columns=[
            'id', 'date', 'sport', 'home_team', 'away_team', 
            'pick', 'odds', 'stake', 'result', 'profit', 'status'
        ])
    
    def save_bets(self, df: pd.DataFrame):
        """Save bets to storage."""
        df.to_json(self.bets_file, orient='records')
    
    def add_bet(self, sport: str, home_team: str, away_team: str,
                pick: str, odds: float, stake: float) -> Dict:
        """Add a new pending bet."""
        bets = self.load_bets()
        
        new_bet = {
            'id': len(bets) + 1,
            'date': datetime.now().isoformat(),
            'sport': sport,
            'home_team': home_team,
            'away_team': away_team,
            'pick': pick,
            'odds': odds,
            'stake': stake,
            'result': None,
            'profit': 0,
            'status': 'pending'
        }
        
        bets = pd.concat([bets, pd.DataFrame([new_bet])], ignore_index=True)
        self.save_bets(bets)
        return new_bet
    
    def update_result(self, bet_id: int, result: str):
        """Update bet result (win/loss/push)."""
        bets = self.load_bets()
        
        if bet_id in bets['id'].values:
            idx = bets[bets['id'] == bet_id].index[0]
            bet = bets.loc[idx]
            
            if result == 'win':
                profit = bet['stake'] * (abs(bet['odds']) / 100 if bet['odds'] > 0 else 100 / abs(bet['odds']))
                if bet['odds'] < 0:
                    profit = bet['stake'] * (100 / abs(bet['odds']))
            elif result == 'loss':
                profit = -bet['stake']
            else:
                profit = 0
            
            bets.at[idx, 'result'] = result
            bets.at[idx, 'profit'] = profit
            bets.at[idx, 'status'] = 'settled'
            
            self.save_bets(bets)
    
    def get_stats(self) -> Dict:
        """Get betting statistics."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled']
        
        if settled.empty:
            return {
                'total_bets': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_staked': 0,
                'total_profit': 0,
                'roi': 0,
                'avg_odds': 0
            }
        
        wins = len(settled[settled['result'] == 'win'])
        losses = len(settled[settled['result'] == 'loss'])
        total = len(settled)
        
        return {
            'total_bets': total,
            'wins': wins,
            'losses': losses,
            'win_rate': wins / total if total > 0 else 0,
            'total_staked': settled['stake'].sum(),
            'total_profit': settled['profit'].sum(),
            'roi': settled['profit'].sum() / settled['stake'].sum() if settled['stake'].sum() > 0 else 0,
            'avg_odds': settled['odds'].mean()
        }
    
    def get_pending_bets(self) -> pd.DataFrame:
        """Get all pending bets."""
        bets = self.load_bets()
        return bets[bets['status'] == 'pending']
    
    def calculate_kelly_criterion(self, model_prob: float, odds: float, 
                                  fraction: float = 0.25) -> float:
        """Calculate Kelly Criterion bet size."""
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        kelly = ((decimal_odds - 1) * model_prob - (1 - model_prob)) / (decimal_odds - 1)
        return max(0, kelly * fraction)
    
    def get_performance_by_sport(self) -> pd.DataFrame:
        """Get ROI breakdown by sport."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled']
        
        if settled.empty:
            return pd.DataFrame()
        
        return settled.groupby('sport').agg({
            'profit': 'sum',
            'stake': 'sum',
            'result': lambda x: (x == 'win').sum() / len(x) if len(x) > 0 else 0
        }).reset_index()
    
    def export_to_csv(self, filepath: str):
        """Export bets to CSV."""
        bets = self.load_bets()
        bets.to_csv(filepath, index=False)

if __name__ == "__main__":
    tracker = BetTracker("./data")
    print("Bet Tracker ready")
