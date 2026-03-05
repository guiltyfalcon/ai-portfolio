#!/usr/bin/env python3
"""
Line Movement Tracker - Track opening vs current lines
Identifies sharp money movement and line value
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class LineMovementTracker:
    """Track and analyze player prop line movements."""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.movements_file = os.path.join(cache_dir, 'line_movements.json')
        self.load_movements()
    
    def load_movements(self):
        """Load historical line movements."""
        if os.path.exists(self.movements_file):
            with open(self.movements_file, 'r') as f:
                self.movements = json.load(f)
        else:
            self.movements = {}
    
    def save_movements(self):
        """Save line movements to file."""
        with open(self.movements_file, 'w') as f:
            json.dump(self.movements, f, indent=2)
    
    def record_line(self, player: str, prop_type: str, line: float, odds: int, sportsbook: str, timestamp: str = None):
        """Record a new line observation."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        key = f"{player}_{prop_type}_{sportsbook}"
        
        if key not in self.movements:
            self.movements[key] = {
                'player': player,
                'prop_type': prop_type,
                'sportsbook': sportsbook,
                'observations': []
            }
        
        self.movements[key]['observations'].append({
            'timestamp': timestamp,
            'line': line,
            'odds': odds
        })
        
        # Keep only last 50 observations per prop
        self.movements[key]['observations'] = self.movements[key]['observations'][-50:]
        
        self.save_movements()
    
    def get_line_movement(self, player: str, prop_type: str, sportsbook: str = 'all') -> Optional[Dict]:
        """
        Get line movement data for a specific prop.
        
        Returns:
        - opening_line: First observed line
        - current_line: Most recent line
        - line_change: Direction and magnitude of movement
        - odds_movement: Opening vs current odds
        - sharp_indicator: Whether movement suggests sharp money
        """
        if sportsbook == 'all':
            # Aggregate across all books
            all_obs = []
            for key, data in self.movements.items():
                if data['player'] == player and data['prop_type'] == prop_type:
                    all_obs.extend(data['observations'])
            
            if not all_obs:
                return None
            
            # Sort by timestamp
            all_obs.sort(key=lambda x: x['timestamp'])
            
            opening_line = all_obs[0]['line']
            opening_odds = all_obs[0]['odds']
            current_line = all_obs[-1]['line']
            current_odds = all_obs[-1]['odds']
        else:
            key = f"{player}_{prop_type}_{sportsbook}"
            if key not in self.movements:
                return None
            
            obs = self.movements[key]['observations']
            if not obs:
                return None
            
            opening_line = obs[0]['line']
            opening_odds = obs[0]['odds']
            current_line = obs[-1]['line']
            current_odds = obs[-1]['odds']
        
        line_change = current_line - opening_line
        odds_change = current_odds - opening_odds
        
        # Determine sharp money indicator
        # If line moves DOWN but odds move UP (more juice on over) = sharp money on under
        # If line moves UP but odds move DOWN (less juice on over) = sharp money on over
        sharp_indicator = "neutral"
        if line_change > 0 and odds_change < 0:
            sharp_indicator = "sharp_on_over"
        elif line_change < 0 and odds_change > 0:
            sharp_indicator = "sharp_on_under"
        elif line_change > 0:
            sharp_indicator = "public_on_over"
        elif line_change < 0:
            sharp_indicator = "public_on_under"
        
        return {
            'player': player,
            'prop_type': prop_type,
            'opening_line': opening_line,
            'opening_odds': opening_odds,
            'current_line': current_line,
            'current_odds': current_odds,
            'line_change': round(line_change, 1),
            'odds_change': odds_change,
            'sharp_indicator': sharp_indicator,
            'observations_count': len(all_obs) if sportsbook == 'all' else len(self.movements.get(key, {}).get('observations', []))
        }
    
    def analyze_all_movements(self) -> List[Dict]:
        """Analyze line movements for all tracked props."""
        movements = []
        
        for key, data in self.movements.items():
            if len(data['observations']) < 2:
                continue  # Need at least 2 observations
            
            movement = self.get_line_movement(
                data['player'],
                data['prop_type'],
                data['sportsbook']
            )
            
            if movement:
                movements.append(movement)
        
        # Sort by line movement magnitude (biggest moves first)
        movements.sort(key=lambda x: abs(x['line_change']), reverse=True)
        
        return movements
    
    def find_value_from_movement(self) -> List[Dict]:
        """
        Find betting value based on line movements.
        
        Strategy:
        - If line moved UP significantly, book was wrong (value on current line)
        - If sharp money detected, follow the sharps
        """
        value_bets = []
        movements = self.analyze_all_movements()
        
        for movement in movements:
            # Significant line movement = 2+ points
            if abs(movement['line_change']) >= 2:
                value_bets.append({
                    **movement,
                    'value_reason': 'significant_line_movement',
                    'recommendation': 'follow_line' if movement['line_change'] > 0 else 'fade_line'
                })
            
            # Sharp money detected
            if movement['sharp_indicator'] in ['sharp_on_over', 'sharp_on_under']:
                value_bets.append({
                    **movement,
                    'value_reason': 'sharp_money',
                    'recommendation': movement['sharp_indicator'].replace('sharp_', 'bet_')
                })
        
        return value_bets
    
    def generate_movement_report(self) -> str:
        """Generate a readable line movement report."""
        movements = self.analyze_all_movements()
        value_bets = self.find_value_from_movement()
        
        report = []
        report.append("=" * 60)
        report.append("📈 LINE MOVEMENT REPORT")
        report.append("=" * 60)
        report.append("")
        
        if movements:
            report.append("### Biggest Line Movements")
            report.append("")
            
            for mov in movements[:10]:
                report.append(f"**{mov['player']} {mov['prop_type']}**")
                report.append(f"  Opening: {mov['opening_line']} ({mov['opening_odds']})")
                report.append(f"  Current: {mov['current_line']} ({mov['current_odds']})")
                report.append(f"  Movement: {mov['line_change']:+.1f} pts")
                report.append(f"  Indicator: {mov['sharp_indicator']}")
                report.append("")
        else:
            report.append("No line movements tracked yet.")
            report.append("Run scraper multiple times to build movement data.")
        
        if value_bets:
            report.append("")
            report.append("### Value Opportunities from Line Movement")
            report.append("")
            
            for bet in value_bets[:5]:
                report.append(f"**{bet['player']} {bet['prop_type']}**")
                report.append(f"  Reason: {bet['value_reason']}")
                report.append(f"  Recommendation: {bet['recommendation']}")
                report.append("")
        
        return "\n".join(report)


def main():
    """Test line movement tracker."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tracker = LineMovementTracker(script_dir)
    
    # Record some test observations
    now = datetime.now()
    tracker.record_line('Ja Morant', 'pts', 27.5, -115, 'BetMGM', (now - timedelta(hours=2)).isoformat())
    tracker.record_line('Ja Morant', 'pts', 27.0, -115, 'BetMGM', now.isoformat())
    
    # Generate report
    report = tracker.generate_movement_report()
    print(report)


if __name__ == '__main__':
    main()
