#!/usr/bin/env python3
"""
BetBrain AI - Pick Tracking & Accuracy System
Tracks all posted picks and calculates verified accuracy.

Features:
- Log every pick with timestamp, odds, sportsbook
- Track outcomes (win/loss/push)
- Calculate hit rate by bet type, sport, confidence level
- Generate public track record for marketing
- Export to JSON for website display

Usage:
  python3 pick_tracker.py log --pick "Lakers -5.5" --odds -110 --confidence 72
  python3 pick_tracker.py update --pick_id 123 --result win
  python3 pick_tracker.py stats
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Data directory
DATA_DIR = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/data')
DATA_DIR.mkdir(parents=True, exist_ok=True)

PICKS_FILE = DATA_DIR / 'all_picks.json'
STATS_FILE = DATA_DIR / 'accuracy_stats.json'

class PickTracker:
    def __init__(self):
        self.picks = self.load_picks()
    
    def load_picks(self):
        """Load existing picks from file."""
        if PICKS_FILE.exists():
            with open(PICKS_FILE, 'r') as f:
                return json.load(f)
        return {'picks': [], 'total': 0}
    
    def save_picks(self):
        """Save picks to file."""
        with open(PICKS_FILE, 'w') as f:
            json.dump(self.picks, f, indent=2, default=str)
    
    def log_pick(self, pick_text: str, odds: str, confidence: int, 
                 sport: str = 'NBA', bet_type: str = 'spread',
                 sportsbook: str = 'multiple', game: str = '',
                 ai_reasoning: str = '') -> dict:
        """Log a new pick."""
        pick_id = len(self.picks['picks']) + 1
        
        pick = {
            'id': pick_id,
            'timestamp': datetime.now().isoformat(),
            'sport': sport,
            'bet_type': bet_type,
            'pick': pick_text,
            'game': game,
            'odds': odds,
            'confidence': confidence,
            'sportsbook': sportsbook,
            'ai_reasoning': ai_reasoning,
            'status': 'pending',  # pending, won, lost, push
            'result': None,
            'profit_loss': 0,
            'settled_at': None
        }
        
        self.picks['picks'].append(pick)
        self.picks['total'] = len(self.picks['picks'])
        self.save_picks()
        
        print(f"✅ Logged pick #{pick_id}: {pick_text}")
        print(f"   Confidence: {confidence}% | Odds: {odds} | Sport: {sport}")
        
        return pick
    
    def update_pick(self, pick_id: int, result: str, profit_loss: float = 0):
        """Update a pick with its result."""
        for pick in self.picks['picks']:
            if pick['id'] == pick_id:
                pick['status'] = result
                pick['result'] = result
                pick['profit_loss'] = profit_loss
                pick['settled_at'] = datetime.now().isoformat()
                self.save_picks()
                
                print(f"✅ Updated pick #{pick_id}: {result.upper()}")
                print(f"   P/L: ${profit_loss:.2f}")
                return pick
        
        print(f"❌ Pick #{pick_id} not found")
        return None
    
    def get_stats(self) -> dict:
        """Calculate accuracy statistics."""
        total = len(self.picks['picks'])
        settled = [p for p in self.picks['picks'] if p['status'] != 'pending']
        
        if not settled:
            return {'error': 'No settled picks yet'}
        
        won = [p for p in settled if p['status'] == 'won']
        lost = [p for p in settled if p['status'] == 'lost']
        pushed = [p for p in settled if p['status'] == 'push']
        
        # Overall accuracy (excluding pushes)
        decision_picks = won + lost
        overall_hit_rate = len(won) / len(decision_picks) * 100 if decision_picks else 0
        
        # By confidence level
        high_conf = [p for p in settled if p['confidence'] >= 70]
        med_conf = [p for p in settled if 60 <= p['confidence'] < 70]
        low_conf = [p for p in settled if p['confidence'] < 60]
        
        high_hit = len([p for p in high_conf if p['status'] == 'won']) / len(high_conf) * 100 if high_conf else 0
        med_hit = len([p for p in med_conf if p['status'] == 'won']) / len(med_conf) * 100 if med_conf else 0
        low_hit = len([p for p in low_conf if p['status'] == 'won']) / len(low_conf) * 100 if low_conf else 0
        
        # By bet type
        by_type = {}
        for pick in settled:
            bet_type = pick['bet_type']
            if bet_type not in by_type:
                by_type[bet_type] = {'won': 0, 'lost': 0, 'pushed': 0}
            by_type[bet_type][pick['status']] += 1
        
        # By sport
        by_sport = {}
        for pick in settled:
            sport = pick['sport']
            if sport not in by_sport:
                by_sport[sport] = {'won': 0, 'lost': 0, 'pushed': 0}
            by_sport[sport][pick['status']] += 1
        
        # Total P/L
        total_pl = sum(p['profit_loss'] for p in settled)
        
        stats = {
            'generated_at': datetime.now().isoformat(),
            'overall': {
                'total_picks': total,
                'settled': len(settled),
                'pending': total - len(settled),
                'won': len(won),
                'lost': len(lost),
                'pushed': len(pushed),
                'hit_rate': round(overall_hit_rate, 2),
                'total_pl': round(total_pl, 2)
            },
            'by_confidence': {
                'high_70+': {'count': len(high_conf), 'hit_rate': round(high_hit, 2)},
                'medium_60-69': {'count': len(med_conf), 'hit_rate': round(med_hit, 2)},
                'low_<60': {'count': len(low_conf), 'hit_rate': round(low_hit, 2)}
            },
            'by_bet_type': {},
            'by_sport': {}
        }
        
        # Format by type stats
        for bet_type, counts in by_type.items():
            decisions = counts['won'] + counts['lost']
            hit_rate = counts['won'] / decisions * 100 if decisions else 0
            stats['by_bet_type'][bet_type] = {
                'count': decisions,
                'hit_rate': round(hit_rate, 2)
            }
        
        # Format by sport stats
        for sport, counts in by_sport.items():
            decisions = counts['won'] + counts['lost']
            hit_rate = counts['won'] / decisions * 100 if decisions else 0
            stats['by_sport'][sport] = {
                'count': decisions,
                'hit_rate': round(hit_rate, 2)
            }
        
        # Save stats
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()
        
        if 'error' in stats:
            print(stats['error'])
            return
        
        print("\n" + "=" * 50)
        print("🧠 BetBrain AI - Pick Tracking Stats")
        print("=" * 50)
        
        overall = stats['overall']
        print(f"\n📊 Overall Record: {overall['won']}-{overall['lost']} ({overall['hit_rate']}%)")
        print(f"💰 Total P/L: ${overall['total_pl']:+.2f}")
        print(f"⏳ Pending: {overall['pending']} picks")
        
        print("\n📈 By Confidence Level:")
        for level, data in stats['by_confidence'].items():
            print(f"   {level}: {data['hit_rate']}% ({data['count']} picks)")
        
        print("\n🎯 By Bet Type:")
        for bet_type, data in stats['by_bet_type'].items():
            print(f"   {bet_type}: {data['hit_rate']}% ({data['count']} picks)")
        
        print("\n🏀 By Sport:")
        for sport, data in stats['by_sport'].items():
            print(f"   {sport}: {data['hit_rate']}% ({data['count']} picks)")
        
        print("\n" + "=" * 50)
    
    def export_public_record(self):
        """Export public-facing track record (no sensitive data)."""
        public_picks = []
        for pick in self.picks['picks']:
            public_picks.append({
                'id': pick['id'],
                'date': pick['timestamp'][:10],
                'sport': pick['sport'],
                'bet_type': pick['bet_type'],
                'pick': pick['pick'],
                'game': pick['game'],
                'odds': pick['odds'],
                'confidence': pick['confidence'],
                'result': pick['result'],
                'status': pick['status']
            })
        
        stats = self.get_stats()
        
        public_data = {
            'generated_at': datetime.now().isoformat(),
            'total_picks': len(public_picks),
            'overall_record': stats['overall'],
            'picks': public_picks[-100:]  # Last 100 picks only
        }
        
        output_file = DATA_DIR / 'public_track_record.json'
        with open(output_file, 'w') as f:
            json.dump(public_data, f, indent=2)
        
        print(f"✅ Exported public record to {output_file}")
        return public_data

def main():
    parser = argparse.ArgumentParser(description='BetBrain AI Pick Tracker')
    subparsers = parser.add_subparsers(dest='command')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Log a new pick')
    log_parser.add_argument('--pick', required=True, help='The pick (e.g., "Lakers -5.5")')
    log_parser.add_argument('--odds', required=True, help='Odds (e.g., "-110")')
    log_parser.add_argument('--confidence', type=int, required=True, help='Confidence % (e.g., 72)')
    log_parser.add_argument('--sport', default='NBA', help='Sport')
    log_parser.add_argument('--bet-type', default='spread', help='Bet type')
    log_parser.add_argument('--game', default='', help='Game matchup')
    log_parser.add_argument('--reasoning', default='', help='AI reasoning')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update pick result')
    update_parser.add_argument('--pick-id', type=int, required=True, help='Pick ID')
    update_parser.add_argument('--result', required=True, choices=['won', 'lost', 'push'], help='Result')
    update_parser.add_argument('--pl', type=float, default=0, help='Profit/Loss')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Export command
    subparsers.add_parser('export', help='Export public track record')
    
    args = parser.parse_args()
    tracker = PickTracker()
    
    if args.command == 'log':
        tracker.log_pick(
            pick_text=args.pick,
            odds=args.odds,
            confidence=args.confidence,
            sport=args.sport,
            bet_type=args.bet_type,
            game=args.game,
            ai_reasoning=args.reasoning
        )
    elif args.command == 'update':
        tracker.update_pick(args.pick_id, args.result, args.pl)
    elif args.command == 'stats':
        tracker.print_stats()
    elif args.command == 'export':
        tracker.export_public_record()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
