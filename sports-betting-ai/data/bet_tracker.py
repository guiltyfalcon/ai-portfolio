"""
Bet Tracker - Track picks, stakes, results, ROI
Uses Streamlit session state for persistence (works on Streamlit Cloud)
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

class BetTracker:
    """Track all bets using Streamlit session state."""
    
    def __init__(self, storage_key: str = "bet_tracker_data"):
        self.storage_key = storage_key
        self._init_storage()
    
    def _init_storage(self):
        """Initialize session state storage."""
        if self.storage_key not in st.session_state:
            st.session_state[self.storage_key] = {
                'bets': [],
                'bankroll': 100.0  # Default starting bankroll
            }
        if f"{self.storage_key}_bets" not in st.session_state:
            st.session_state[f"{self.storage_key}_bets"] = pd.DataFrame(columns=[
                'id', 'date', 'sport', 'home_team', 'away_team', 
                'pick', 'odds', 'stake', 'result', 'profit', 'status'
            ])
    
    def load_bets(self) -> pd.DataFrame:
        """Load all bets from session state."""
        return st.session_state.get(f"{self.storage_key}_bets", pd.DataFrame())
    
    def save_bets(self, df: pd.DataFrame):
        """Save bets to session state."""
        st.session_state[f"{self.storage_key}_bets"] = df
    
    def add_bet(self, sport: str, home_team: str, away_team: str,
                pick: str, odds: float, stake: float) -> Dict:
        """Add a new pending bet."""
        bets = self.load_bets()
        
        new_bet = {
            'id': len(bets) + 1 if len(bets) > 0 else 1,
            'date': datetime.now().isoformat(),
            'sport': sport,
            'home_team': home_team,
            'away_team': away_team,
            'pick': pick,
            'odds': float(odds),
            'stake': float(stake),
            'result': None,
            'profit': 0.0,
            'status': 'pending'
        }
        
        # Convert to DataFrame and concat
        if bets.empty:
            bets = pd.DataFrame([new_bet])
        else:
            bets = pd.concat([bets, pd.DataFrame([new_bet])], ignore_index=True)
        
        self.save_bets(bets)
        return new_bet
    
    def update_result(self, bet_id: int, result: str):
        """Update bet result (win/loss/push)."""
        bets = self.load_bets()
        
        if bet_id in bets['id'].values:
            idx = bets[bets['id'] == bet_id].index[0]
            bet = bets.loc[idx]
            
            # Calculate profit
            odds = float(bet['odds'])
            stake = float(bet['stake'])
            
            if result == 'win':
                if odds > 0:
                    profit = stake * (odds / 100)
                else:
                    profit = stake * (100 / abs(odds))
            elif result == 'loss':
                profit = -stake
            else:  # push
                profit = 0.0
            
            bets.at[idx, 'result'] = result
            bets.at[idx, 'profit'] = profit
            bets.at[idx, 'status'] = 'settled'
            
            self.save_bets(bets)
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get betting statistics."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled'] if 'status' in bets.columns else pd.DataFrame()
        
        if settled.empty or len(settled) == 0:
            return {
                'total_bets': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'total_staked': 0.0,
                'total_profit': 0.0,
                'roi': 0.0,
                'avg_odds': 0.0
            }
        
        wins = len(settled[settled['result'] == 'win'])
        losses = len(settled[settled['result'] == 'loss'])
        total = len(settled)
        
        total_staked = settled['stake'].sum() if 'stake' in settled.columns else 0
        total_profit = settled['profit'].sum() if 'profit' in settled.columns else 0
        
        return {
            'total_bets': total,
            'wins': wins,
            'losses': losses,
            'win_rate': wins / total if total > 0 else 0.0,
            'total_staked': float(total_staked),
            'total_profit': float(total_profit),
            'roi': (total_profit / total_staked) if total_staked > 0 else 0.0,
            'avg_odds': settled['odds'].mean() if 'odds' in settled.columns else 0.0
        }
    
    def get_pending_bets(self) -> pd.DataFrame:
        """Get all pending bets."""
        bets = self.load_bets()
        if bets.empty or 'status' not in bets.columns:
            return pd.DataFrame(columns=['id', 'date', 'sport', 'home_team', 'away_team', 
                                       'pick', 'odds', 'stake', 'result', 'profit', 'status'])
        return bets[bets['status'] == 'pending']
    
    def calculate_kelly_criterion(self, model_prob: float, odds: float, 
                                  fraction: float = 0.25) -> float:
        """Calculate Kelly Criterion bet size."""
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        kelly = ((decimal_odds - 1) * model_prob - (1 - model_prob)) / (decimal_odds - 1)
        return max(0.0, kelly * fraction)
    
    def get_performance_by_sport(self) -> pd.DataFrame:
        """Get ROI breakdown by sport."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled'] if 'status' in bets.columns else pd.DataFrame()
        
        if settled.empty:
            return pd.DataFrame()
        
        return settled.groupby('sport').agg({
            'profit': 'sum',
            'stake': 'sum',
            'result': lambda x: (x == 'win').sum() / len(x) if len(x) > 0 else 0
        }).reset_index()
    
    def export_to_csv(self):
        """Export bets to CSV for download."""
        bets = self.load_bets()
        if not bets.empty:
            return bets.to_csv(index=False)
        return None
    
    def clear_all(self):
        """Clear all bets."""
        st.session_state[f"{self.storage_key}_bets"] = pd.DataFrame(columns=[
            'id', 'date', 'sport', 'home_team', 'away_team', 
            'pick', 'odds', 'stake', 'result', 'profit', 'status'
        ])

if __name__ == "__main__":
    tracker = BetTracker()
    print("Bet Tracker ready")
