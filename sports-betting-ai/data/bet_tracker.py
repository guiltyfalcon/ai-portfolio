"""
Bet Tracker - Enhanced with better persistence and analytics
Uses Streamlit session state for persistence (works on Streamlit Cloud)
Also supports CSV backup/restore for data portability
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import streamlit as st
import io

class BetTracker:
    """Track all bets using Streamlit session state with CSV backup support."""
    
    def __init__(self, storage_key: str = "bet_tracker_data"):
        self.storage_key = storage_key
        self._init_storage()
    
    def _init_storage(self):
        """Initialize session state storage."""
        if self.storage_key not in st.session_state:
            st.session_state[self.storage_key] = {
                'bets': [],
                'bankroll': 1000.0  # Default starting bankroll
            }
        if f"{self.storage_key}_bets" not in st.session_state:
            st.session_state[f"{self.storage_key}_bets"] = pd.DataFrame(columns=[
                'id', 'date', 'sport', 'home_team', 'away_team', 
                'pick', 'odds', 'stake', 'result', 'profit', 'status', 'notes'
            ])
    
    def load_bets(self) -> pd.DataFrame:
        """Load all bets from session state."""
        return st.session_state.get(f"{self.storage_key}_bets", pd.DataFrame())
    
    def save_bets(self, df: pd.DataFrame):
        """Save bets to session state."""
        st.session_state[f"{self.storage_key}_bets"] = df
    
    def add_bet(self, sport: str, home_team: str, away_team: str,
                pick: str, odds: float, stake: float, notes: str = "") -> Dict:
        """Add a new pending bet."""
        bets = self.load_bets()
        
        # Generate new ID
        if bets.empty:
            new_id = 1
        else:
            new_id = int(bets['id'].max()) + 1
        
        new_bet = {
            'id': new_id,
            'date': datetime.now().isoformat(),
            'sport': sport.upper(),
            'home_team': home_team.strip(),
            'away_team': away_team.strip(),
            'pick': pick.strip(),
            'odds': float(odds),
            'stake': float(stake),
            'result': None,
            'profit': 0.0,
            'status': 'pending',
            'notes': notes
        }
        
        # Convert to DataFrame and concat
        new_bet_df = pd.DataFrame([new_bet])
        if bets.empty:
            bets = new_bet_df
        else:
            bets = pd.concat([bets, new_bet_df], ignore_index=True)
        
        self.save_bets(bets)
        return new_bet
    
    def update_result(self, bet_id: int, result: str) -> bool:
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
            bets.at[idx, 'date'] = datetime.now().isoformat()  # Update with result date
            
            self.save_bets(bets)
            return True
        return False
    
    def delete_bet(self, bet_id: int) -> bool:
        """Delete a bet by ID."""
        bets = self.load_bets()
        
        if bet_id in bets['id'].values:
            bets = bets[bets['id'] != bet_id]
            self.save_bets(bets)
            return True
        return False
    
    def edit_bet(self, bet_id: int, **kwargs) -> bool:
        """Edit a bet's properties."""
        bets = self.load_bets()
        
        if bet_id in bets['id'].values:
            idx = bets[bets['id'] == bet_id].index[0]
            for key, value in kwargs.items():
                if key in bets.columns:
                    bets.at[idx, key] = value
            self.save_bets(bets)
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get comprehensive betting statistics."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled'] if 'status' in bets.columns else pd.DataFrame()
        pending = bets[bets['status'] == 'pending'] if 'status' in bets.columns else pd.DataFrame()
        
        if settled.empty or len(settled) == 0:
            return {
                'total_bets': 0,
                'wins': 0,
                'losses': 0,
                'pushes': 0,
                'win_rate': 0.0,
                'total_staked': 0.0,
                'total_profit': 0.0,
                'roi': 0.0,
                'avg_odds': 0.0,
                'pending_bets': len(pending),
                'pending_stake': pending['stake'].sum() if not pending.empty else 0.0,
                'best_streak': 0,
                'worst_streak': 0
            }
        
        wins = len(settled[settled['result'] == 'win'])
        losses = len(settled[settled['result'] == 'loss'])
        pushes = len(settled[settled['result'] == 'push'])
        total = len(settled)
        
        total_staked = settled['stake'].sum() if 'stake' in settled.columns else 0
        total_profit = settled['profit'].sum() if 'profit' in settled.columns else 0
        
        # Calculate streaks
        settled_sorted = settled.sort_values('date')
        results = settled_sorted['result'].tolist()
        
        best_streak = 0
        worst_streak = 0
        current_best = 0
        current_worst = 0
        
        for result in results:
            if result == 'win':
                current_best += 1
                current_worst = 0
                best_streak = max(best_streak, current_best)
            elif result == 'loss':
                current_worst += 1
                current_best = 0
                worst_streak = max(worst_streak, current_worst)
            else:  # push
                current_best = 0
                current_worst = 0
        
        return {
            'total_bets': total,
            'wins': wins,
            'losses': losses,
            'pushes': pushes,
            'win_rate': wins / (wins + losses) if (wins + losses) > 0 else 0.0,
            'total_staked': float(total_staked),
            'total_profit': float(total_profit),
            'roi': (total_profit / total_staked) if total_staked > 0 else 0.0,
            'avg_odds': settled['odds'].mean() if 'odds' in settled.columns else 0.0,
            'pending_bets': len(pending),
            'pending_stake': pending['stake'].sum() if not pending.empty else 0.0,
            'best_streak': best_streak,
            'worst_streak': worst_streak
        }
    
    def get_pending_bets(self) -> pd.DataFrame:
        """Get all pending bets."""
        bets = self.load_bets()
        if bets.empty or 'status' not in bets.columns:
            return pd.DataFrame(columns=['id', 'date', 'sport', 'home_team', 'away_team', 
                                       'pick', 'odds', 'stake', 'result', 'profit', 'status'])
        return bets[bets['status'] == 'pending']
    
    def get_settled_bets(self, days: Optional[int] = None) -> pd.DataFrame:
        """Get settled bets, optionally filtered by days."""
        bets = self.load_bets()
        if bets.empty or 'status' not in bets.columns:
            return pd.DataFrame()
        
        settled = bets[bets['status'] == 'settled']
        
        if days and not settled.empty:
            cutoff = datetime.now() - timedelta(days=days)
            settled['date'] = pd.to_datetime(settled['date'])
            settled = settled[settled['date'] >= cutoff]
        
        return settled
    
    def calculate_kelly_criterion(self, model_prob: float, odds: float, 
                                  fraction: float = 0.25) -> Tuple[float, float]:
        """
        Calculate Kelly Criterion bet size.
        
        Returns:
            Tuple of (kelly_fraction, recommended_stake)
        """
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        # Full Kelly
        kelly = ((decimal_odds - 1) * model_prob - (1 - model_prob)) / (decimal_odds - 1)
        kelly = max(0.0, min(kelly, 1.0))  # Clamp between 0 and 1
        
        # Fractional Kelly
        fractional_kelly = kelly * fraction
        
        return kelly, fractional_kelly
    
    def get_performance_by_sport(self) -> pd.DataFrame:
        """Get ROI breakdown by sport."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled'] if 'status' in bets.columns else pd.DataFrame()
        
        if settled.empty:
            return pd.DataFrame()
        
        sport_stats = settled.groupby('sport').agg({
            'profit': ['sum', 'count'],
            'stake': 'sum',
            'result': lambda x: (x == 'win').sum()
        }).reset_index()
        
        # Flatten column names
        sport_stats.columns = ['sport', 'profit', 'bets', 'stake', 'wins']
        sport_stats['roi'] = (sport_stats['profit'] / sport_stats['stake'] * 100).round(2)
        sport_stats['win_rate'] = (sport_stats['wins'] / sport_stats['bets'] * 100).round(1)
        
        return sport_stats[['sport', 'profit', 'roi', 'win_rate', 'bets']]
    
    def get_performance_by_month(self) -> pd.DataFrame:
        """Get monthly performance breakdown."""
        bets = self.load_bets()
        settled = bets[bets['status'] == 'settled'] if 'status' in bets.columns else pd.DataFrame()
        
        if settled.empty:
            return pd.DataFrame()
        
        settled['date'] = pd.to_datetime(settled['date'])
        settled['month'] = settled['date'].dt.to_period('M')
        
        monthly = settled.groupby('month').agg({
            'profit': 'sum',
            'stake': 'sum',
            'result': 'count'
        }).reset_index()
        
        monthly['roi'] = (monthly['profit'] / monthly['stake'] * 100).round(2)
        monthly.columns = ['Month', 'Profit', 'Stake', 'Bets', 'ROI%']
        
        return monthly
    
    def export_to_csv(self) -> Optional[str]:
        """Export bets to CSV for download."""
        bets = self.load_bets()
        if not bets.empty:
            return bets.to_csv(index=False)
        return None
    
    def import_from_csv(self, csv_data: str) -> Tuple[int, int]:
        """
        Import bets from CSV.
        
        Returns:
            Tuple of (imported_count, skipped_count)
        """
        try:
            new_bets = pd.read_csv(io.StringIO(csv_data))
            current_bets = self.load_bets()
            
            imported = 0
            skipped = 0
            
            for _, bet in new_bets.iterrows():
                # Check for duplicates (same teams, pick, and odds)
                if not current_bets.empty:
                    duplicate = current_bets[
                        (current_bets['home_team'] == bet.get('home_team')) &
                        (current_bets['away_team'] == bet.get('away_team')) &
                        (current_bets['pick'] == bet.get('pick')) &
                        (current_bets['odds'] == bet.get('odds'))
                    ]
                    if not duplicate.empty:
                        skipped += 1
                        continue
                
                # Add the bet
                self.add_bet(
                    sport=bet.get('sport', 'Unknown'),
                    home_team=bet.get('home_team', ''),
                    away_team=bet.get('away_team', ''),
                    pick=bet.get('pick', ''),
                    odds=float(bet.get('odds', -110)),
                    stake=float(bet.get('stake', 0)),
                    notes=bet.get('notes', '')
                )
                imported += 1
            
            return imported, skipped
        except Exception as e:
            st.error(f"Error importing: {e}")
            return 0, 0
    
    def clear_all(self):
        """Clear all bets."""
        st.session_state[f"{self.storage_key}_bets"] = pd.DataFrame(columns=[
            'id', 'date', 'sport', 'home_team', 'away_team', 
            'pick', 'odds', 'stake', 'result', 'profit', 'status', 'notes'
        ])
    
    def get_clv(self, bet_id: int, closing_odds: float) -> Optional[float]:
        """
        Calculate Closing Line Value for a bet.
        
        Args:
            bet_id: The bet ID
            closing_odds: The odds at game time
            
        Returns:
            CLV percentage or None if bet not found
        """
        bets = self.load_bets()
        
        if bet_id in bets['id'].values:
            bet = bets[bets['id'] == bet_id].iloc[0]
            entry_odds = float(bet['odds'])
            
            # Convert to implied probabilities
            if entry_odds > 0:
                entry_prob = 100 / (entry_odds + 100)
            else:
                entry_prob = abs(entry_odds) / (abs(entry_odds) + 100)
            
            if closing_odds > 0:
                closing_prob = 100 / (closing_odds + 100)
            else:
                closing_prob = abs(closing_odds) / (abs(closing_odds) + 100)
            
            # CLV is the difference in implied probability
            clv = (entry_prob - closing_prob) * 100
            return clv
        
        return None

if __name__ == "__main__":
    tracker = BetTracker()
    print("Bet Tracker ready")
    print(f"Stats: {tracker.get_stats()}")
