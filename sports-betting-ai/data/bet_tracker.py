"""
Bet Tracker - Track picks, stakes, results, ROI
Uses Streamlit session state for persistence (works on Streamlit Cloud)
Includes input validation and error handling
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

class BetTracker:
    """Track all bets using Streamlit session state with validation."""
    
    def __init__(self, storage_key: str = "bet_tracker_data"):
        self.storage_key = storage_key
        self._init_storage()
    
    def _init_storage(self):
        """Initialize session state storage."""
        if self.storage_key not in st.session_state:
            st.session_state[self.storage_key] = {
                'bets': [],
                'bankroll': 100.0
            }
        if f"{self.storage_key}_bets" not in st.session_state:
            st.session_state[f"{self.storage_key}_bets"] = pd.DataFrame(columns=[
                'id', 'date', 'sport', 'home_team', 'away_team', 
                'pick', 'odds', 'stake', 'result', 'profit', 'status'
            ])
    
    def _validate_odds(self, odds: float) -> tuple[bool, str]:
        """Validate odds value."""
        try:
            odds = float(odds)
            if odds == 0:
                return False, "Odds cannot be zero"
            if abs(odds) > 10000:
                return False, "Odds value too extreme"
            return True, ""
        except (ValueError, TypeError):
            return False, "Invalid odds format"
    
    def _validate_stake(self, stake: float) -> tuple[bool, str]:
        """Validate stake amount."""
        try:
            stake = float(stake)
            if stake <= 0:
                return False, "Stake must be positive"
            if stake > 100000:
                return False, "Stake exceeds maximum ($100k)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Invalid stake amount"
    
    def _validate_result(self, result: str) -> tuple[bool, str]:
        """Validate result string."""
        valid_results = ['win', 'loss', 'push']
        if result.lower() not in valid_results:
            return False, f"Result must be one of: {', '.join(valid_results)}"
        return True, ""
    
    def load_bets(self) -> pd.DataFrame:
        """Load all bets from session state."""
        return st.session_state.get(f"{self.storage_key}_bets", pd.DataFrame())
    
    def save_bets(self, df: pd.DataFrame):
        """Save bets to session state."""
        st.session_state[f"{self.storage_key}_bets"] = df
    
    def add_bet(self, sport: str, home_team: str, away_team: str,
                pick: str, odds: float, stake: float) -> tuple[Dict, str]:
        """Add a new pending bet with validation."""
        # Validate inputs
        odds_valid, odds_error = self._validate_odds(odds)
        if not odds_valid:
            return None, f"Invalid odds: {odds_error}"
        
        stake_valid, stake_error = self._validate_stake(stake)
        if not stake_valid:
            return None, f"Invalid stake: {stake_error}"
        
        # Validate team names
        if not home_team or not away_team or not pick:
            return None, "Team names and pick cannot be empty"
        
        if len(home_team) > 100 or len(away_team) > 100 or len(pick) > 200:
            return None, "Team/pick names too long"
        
        bets = self.load_bets()
        
        # Generate unique ID (max existing + 1)
        if bets.empty:
            new_id = 1
        else:
            new_id = int(bets['id'].max()) + 1
        
        new_bet = {
            'id': new_id,
            'date': datetime.now().isoformat(),
            'sport': sport.upper(),
            'home_team': str(home_team).strip(),
            'away_team': str(away_team).strip(),
            'pick': str(pick).strip(),
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
        return new_bet, ""
    
    def update_result(self, bet_id: int, result: str) -> tuple[bool, str]:
        """Update bet result with validation."""
        # Validate result
        result_valid, result_error = self._validate_result(result)
        if not result_valid:
            return False, result_error
        
        bets = self.load_bets()
        
        if bet_id not in bets['id'].values:
            return False, f"Bet #{bet_id} not found"
        
        idx = bets[bets['id'] == bet_id].index[0]
        
        try:
            odds = float(bets.at[idx, 'odds'])
            stake = float(bets.at[idx, 'stake'])
        except (ValueError, TypeError):
            return False, "Invalid odds or stake value in bet"
        
        # Calculate profit with bounds checking
        if result.lower() == 'win':
            if odds > 0:
                profit = stake * (odds / 100)
            else:
                profit = stake * (100 / abs(odds))
        elif result.lower() == 'loss':
            profit = -stake
        else:  # push
            profit = 0.0
        
        # Sanity check on profit
        if abs(profit) > stake * 100:
            return False, "Calculated profit exceeds reasonable bounds"
        
        bets.at[idx, 'result'] = result.lower()
        bets.at[idx, 'profit'] = profit
        bets.at[idx, 'status'] = 'settled'
        
        self.save_bets(bets)
        return True, ""
    
    def get_stats(self) -> Dict:
        """Get betting statistics with safe division."""
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
        
        # Safe division
        win_rate = wins / total if total > 0 else 0.0
        roi = (total_profit / total_staked) if total_staked > 0 else 0.0
        avg_odds = settled['odds'].mean() if 'odds' in settled.columns else 0.0
        
        return {
            'total_bets': int(total),
            'wins': int(wins),
            'losses': int(losses),
            'win_rate': float(win_rate),
            'total_staked': float(total_staked),
            'total_profit': float(total_profit),
            'roi': float(roi),
            'avg_odds': float(avg_odds)
        }
    
    def get_pending_bets(self) -> pd.DataFrame:
        """Get all pending bets."""
        bets = self.load_bets()
        if bets.empty or 'status' not in bets.columns:
            return pd.DataFrame(columns=[
                'id', 'date', 'sport', 'home_team', 'away_team', 
                'pick', 'odds', 'stake', 'result', 'profit', 'status'
            ])
        return bets[bets['status'] == 'pending']
    
    def calculate_kelly_criterion(self, model_prob: float, odds: float, 
                                  fraction: float = 0.25) -> float:
        """Calculate Kelly Criterion bet size with validation."""
        # Validate inputs
        if not (0 < model_prob < 1):
            return 0.0
        
        valid, _ = self._validate_odds(odds)
        if not valid:
            return 0.0
        
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        if decimal_odds <= 1:
            return 0.0
        
        kelly = ((decimal_odds - 1) * model_prob - (1 - model_prob)) / (decimal_odds - 1)
        return max(0.0, min(kelly * fraction, 1.0))  # Cap at 100% bankroll
    
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
        """Clear all bets with confirmation."""
        st.session_state[f"{self.storage_key}_bets"] = pd.DataFrame(columns=[
            'id', 'date', 'sport', 'home_team', 'away_team', 
            'pick', 'odds', 'stake', 'result', 'profit', 'status'
        ])
    
    def delete_bet(self, bet_id: int) -> tuple[bool, str]:
        """Delete a specific bet."""
        bets = self.load_bets()
        
        if bet_id not in bets['id'].values:
            return False, f"Bet #{bet_id} not found"
        
        bets = bets[bets['id'] != bet_id].reset_index(drop=True)
        self.save_bets(bets)
        return True, ""

if __name__ == "__main__":
    tracker = BetTracker()
    print("Bet Tracker ready with validation")
