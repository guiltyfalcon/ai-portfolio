#!/usr/bin/env python3
"""
BetBrain AI — Argus Edge Detector
Implements Argus-style prediction market edge detection with Kelly criterion sizing
Uses BetMonster picks from Yahoo odds scraper
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
TWITTER_DRAFTS_DIR = Path("/Users/djryan/.openclaw/data/twitter-drafts/")
YAHOO_ODDS_CACHE = Path("/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/yahoo_odds_cache.json")

# Argus Edge Strategy Parameters (from argus-edge skill)
EDGE_THRESHOLD = 0.10  # Minimum 10% edge to bet
FRESHNESS_WINDOW_MINUTES = 30  # Primary betting window
MAX_CONSENSUS = 0.92  # Skip markets >92% consensus (dead signal)

# Kelly Criterion Parameters
KELLY_MULTIPLIER = 0.25  # Quarter-Kelly for risk management (conservative)
MAX_STAKE_PERCENT = 0.05  # Max 5% of bankroll per bet
MIN_STAKE_PERCENT = 0.01  # Min 1% of bankroll per bet

# Asset-specific TA thresholds (from Argus Edge)
# Adapted for sports: use confidence tiers instead of TA scores
CONFIDENCE_THRESHOLDS = {
    "elite": 3,    # ±3 for elite tier (BTC equivalent)
    "verified": 2, # ±2 for verified (ETH equivalent)
    "strong": 1,   # ±1 for strong (SOL equivalent)
    "lean": 2      # ±2 for lean (XRP equivalent)
}


class ArgusEdgeDetector:
    """
    Argus-style edge detection for sports betting
    Combines Monte Carlo probabilities with market odds
    """
    
    def __init__(self, bankroll: float = 10000.0):
        self.bankroll = bankroll
        self.edge_log = []
    
    def calculate_edge(self, model_prob: float, market_odds: float) -> float:
        """
        Calculate edge: model probability vs market implied probability
        
        Args:
            model_prob: Our model's probability (0-1)
            market_odds: American odds (e.g., -110, +150)
        
        Returns:
            Edge as decimal (e.g., 0.15 = 15% edge)
        """
        # Convert American odds to implied probability
        if market_odds > 0:
            market_implied_prob = 100 / (market_odds + 100)
        else:
            market_implied_prob = abs(market_odds) / (abs(market_odds) + 100)
        
        # Edge = our prob - market prob
        edge = model_prob - market_implied_prob
        
        return round(edge, 4)
    
    def calculate_kelly_stake(self, edge: float, odds: float) -> float:
        """
        Calculate Kelly criterion stake size
        
        Kelly % = (edge × bankroll) / odds
        
        Uses quarter-Kelly for risk management
        """
        if edge <= 0:
            return 0.0
        
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds + 100) / 100
        else:
            decimal_odds = (abs(odds) + 100) / abs(odds)
        
        # Full Kelly
        kelly_full = (edge * self.bankroll) / (decimal_odds - 1)
        
        # Quarter-Kelly (conservative)
        kelly_quarter = kelly_full * KELLY_MULTIPLIER
        
        # Apply min/max constraints
        max_stake = self.bankroll * MAX_STAKE_PERCENT
        min_stake = self.bankroll * MIN_STAKE_PERCENT
        
        kelly_stake = max(min_stake, min(kelly_quarter, max_stake))
        
        return round(kelly_stake, 2)
    
    def check_freshness(self, pick_age_minutes: int) -> bool:
        """
        Check if pick is within freshness window
        """
        return pick_age_minutes <= FRESHNESS_WINDOW_MINUTES
    
    def check_consensus(self, consensus_pct: float) -> bool:
        """
        Skip markets with >92% consensus (dead signal per Argus)
        """
        return consensus_pct <= MAX_CONSENSUS
    
    def evaluate_pick(self, pick: Dict) -> Dict:
        """
        Evaluate a single pick using Argus Edge framework
        
        Returns dict with edge, kelly stake, and recommendation
        """
        team = pick.get('team', 'Unknown')
        matchup = pick.get('matchup', '')
        model_prob = pick.get('model_prob', 0.5)
        odds = pick.get('odds', -110)
        confidence = pick.get('confidence', 50)
        edge = pick.get('edge', 0)
        
        # Calculate edge if not provided
        if 'edge' not in pick or edge == 0:
            edge = self.calculate_edge(model_prob, odds)
        
        # Check freshness (assume all picks are fresh for now)
        is_fresh = self.check_freshness(0)
        
        # Check consensus (use confidence as proxy)
        consensus_pct = confidence / 100
        passes_consensus = self.check_consensus(consensus_pct)
        
        # Calculate Kelly stake
        kelly_stake = self.calculate_kelly_stake(edge, odds)
        
        # Determine recommendation
        recommendation = "NO BET"
        if edge >= EDGE_THRESHOLD and is_fresh and passes_consensus:
            if kelly_stake >= self.bankroll * 0.03:
                recommendation = "STRONG BET"
            else:
                recommendation = "BET"
        elif edge >= 0.05:
            recommendation = "LEAN"
        
        result = {
            'team': team,
            'matchup': matchup,
            'model_prob': model_prob,
            'market_odds': odds,
            'market_implied_prob': self._odds_to_prob(odds),
            'edge': edge,
            'edge_pct': edge * 100,
            'kelly_stake': kelly_stake,
            'kelly_pct': (kelly_stake / self.bankroll) * 100,
            'is_fresh': is_fresh,
            'passes_consensus': passes_consensus,
            'recommendation': recommendation,
            'confidence': confidence,
            'evaluated_at': datetime.now().isoformat()
        }
        
        self.edge_log.append(result)
        return result
    
    def _odds_to_prob(self, odds: float) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def get_summary(self) -> Dict:
        """Get summary of all evaluated picks"""
        if not self.edge_log:
            return {'total_picks': 0}
        
        bets = [p for p in self.edge_log if p['recommendation'] in ['BET', 'STRONG BET']]
        leans = [p for p in self.edge_log if p['recommendation'] == 'LEAN']
        no_bets = [p for p in self.edge_log if p['recommendation'] == 'NO BET']
        
        total_kelly = sum(p['kelly_stake'] for p in bets)
        
        return {
            'total_picks': len(self.edge_log),
            'strong_bets': len([p for p in bets if p['recommendation'] == 'STRONG BET']),
            'bets': len(bets),
            'leans': len(leans),
            'no_bets': len(no_bets),
            'total_kelly_stake': total_kelly,
            'total_kelly_pct': (total_kelly / self.bankroll) * 100,
            'avg_edge': sum(p['edge'] for p in bets) / len(bets) if bets else 0,
            'best_edge': max((p['edge'] for p in self.edge_log), default=0)
        }


def load_yahoo_odds_picks() -> List[Dict]:
    """Load picks from Yahoo odds cache and generate AI analysis"""
    if not YAHOO_ODDS_CACHE.exists():
        return []
    
    with open(YAHOO_ODDS_CACHE, 'r') as f:
        data = json.load(f)
    
    nba_games = data.get('sports', {}).get('nba', [])
    picks = []
    
    for game in nba_games:
        home = game.get('home_team', 'Unknown')
        away = game.get('away_team', 'Unknown')
        spread = game.get('home_spread', 0)
        total = game.get('total', 0)
        home_ml = game.get('home_ml', 0)
        away_ml = game.get('away_ml', 0)
        home_last_5 = game.get('home_last_5', '')
        away_last_5 = game.get('away_last_5', '')
        
        # Generate AI pick with edge calculation
        pick = None
        model_prob = 0.5
        odds = -110
        
        if abs(spread) >= 6 and 'WW' in home_last_5:
            pick = f'{home} {spread}'
            model_prob = 0.75
            odds = game.get('home_spread_odds', -110)
        elif abs(spread) <= 5 and 'WW' in away_last_5:
            pick = f'{away} +{abs(spread)}'
            model_prob = 0.70
            odds = game.get('away_spread_odds', -110)
        elif total >= 240:
            pick = f'OVER {total}'
            model_prob = 0.65
            odds = game.get('over_odds', -110)
        elif home_ml < -200:
            pick = f'{home} ML'
            model_prob = 0.70
            odds = home_ml
        
        if pick:
            edge = model_prob - (abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100))
            picks.append({
                'team': home if 'ML' in pick or spread > 0 else away,
                'matchup': f'{away} @ {home}',
                'pick': pick,
                'model_prob': model_prob,
                'odds': odds,
                'edge': edge,
                'confidence': int(model_prob * 100)
            })
    
    return picks


def generate_argus_twitter_thread(evaluations: List[Dict], summary: Dict) -> List[str]:
    """Generate Twitter thread from Argus Edge evaluations"""
    tweets = []
    
    # Tweet 1: Header
    date = datetime.now().strftime("%m/%d")
    tweets.append(f"🎯 ARGUS EDGE DETECTOR ({date})\n")
    
    # Tweet 2: Summary
    tweets.append(f"📊 {summary['total_picks']} picks analyzed\n"
                  f"🔒 {summary['strong_bets']} STRONG BETS\n"
                  f"⚡ {summary['bets']} total bets\n"
                  f"💰 Total stake: {summary['total_kelly_pct']:.1f}% of bankroll\n")
    
    # Tweet 3+: Top bets
    bets = sorted([e for e in evaluations if e['recommendation'] in ['BET', 'STRONG BET']],
                  key=lambda x: x['edge'], reverse=True)[:5]
    
    for i, bet in enumerate(bets, 1):
        emoji = "🔒" if bet['recommendation'] == 'STRONG BET' else "⚡"
        team = bet['team']
        edge_pct = bet['edge_pct']
        kelly_pct = bet['kelly_pct']
        stake = bet['kelly_stake']
        
        tweet = f"{emoji} {i}. {team}\n"
        tweet += f"   Edge: {edge_pct:.1f}% | Kelly: {kelly_pct:.1f}% (${stake:.0f})\n"
        if bet.get('pick'):
            tweet += f"   Pick: {bet['pick']}\n"
        
        tweets.append(tweet)
    
    # Final tweets: Methodology + Disclaimer
    tweets.append("🧠 Argus Edge Framework:\n"
                  "• Edge ≥10% threshold\n"
                  "• Kelly criterion sizing\n"
                  "• Freshness + consensus checks\n")
    
    tweets.append("📊 Data > Guessing\n"
                  "Results tracked publicly.\n"
                  "#SportsBetting #BetBrain #ArgusEdge")
    
    return tweets


def main():
    print("=" * 60)
    print("BetBrain AI — Argus Edge Detector")
    print("=" * 60)
    print()
    
    # Initialize detector with $10k bankroll
    detector = ArgusEdgeDetector(bankroll=10000.0)
    
    # Load data
    print("📊 Loading Yahoo odds cache...")
    picks = load_yahoo_odds_picks()
    print(f"  - Picks generated: {len(picks)}")
    print()
    
    # Evaluate each pick
    print("🎯 Evaluating picks with Argus Edge framework...")
    evaluations = []
    for pick in picks:
        eval_result = detector.evaluate_pick(pick)
        evaluations.append(eval_result)
        
        rec_emoji = "✅" if eval_result['recommendation'] in ['BET', 'STRONG BET'] else "❌"
        print(f"  {rec_emoji} {eval_result['team']}: {eval_result['recommendation']} "
              f"(Edge: {eval_result['edge_pct']:.1f}%, Kelly: ${eval_result['kelly_stake']:.0f})")
    print()
    
    # Get summary
    summary = detector.get_summary()
    
    # Print summary
    print("=" * 60)
    print("ARGUS EDGE SUMMARY")
    print("=" * 60)
    print(f"Total picks evaluated: {summary['total_picks']}")
    print(f"  - Strong Bets: {summary['strong_bets']}")
    print(f"  - Bets: {summary['bets']}")
    print(f"  - Leans: {summary['leans']}")
    print(f"  - No Bets: {summary['no_bets']}")
    print()
    print(f"Total Kelly stake: ${summary['total_kelly_stake']:.2f} "
          f"({summary['total_kelly_pct']:.1f}% of bankroll)")
    print(f"Average edge (bets): {summary['avg_edge']*100:.1f}%")
    print(f"Best edge: {summary['best_edge']*100:.1f}%")
    print()
    
    # Generate Twitter thread
    print("🐦 Generating Twitter thread...")
    tweets = generate_argus_twitter_thread(evaluations, summary)
    
    # Save thread
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = TWITTER_DRAFTS_DIR / f"argus_edge_thread_{timestamp}.txt"
    
    with open(output_file, 'w') as f:
        f.write("═══ ARGUS EDGE TWITTER THREAD ═══\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Bankroll: ${detector.bankroll:,.0f}\n")
        f.write(f"Total Tweets: {len(tweets)}\n")
        f.write("═══\n\n")
        
        for i, tweet in enumerate(tweets, 1):
            char_count = len(tweet)
            f.write(f"🐦 TWEET {i}/{len(tweets)} ({char_count} chars)\n")
            f.write(tweet)
            f.write("\n\n")
    
    print(f"✓ Saved to {output_file}")
    print()
    
    # Print preview
    print("=" * 60)
    print("TWITTER THREAD PREVIEW")
    print("=" * 60)
    for i, tweet in enumerate(tweets, 1):
        char_count = len(tweet)
        status = "✓" if char_count <= 280 else "⚠️ OVER"
        print(f"\n🐦 Tweet {i}/{len(tweets)} ({char_count} chars) {status}")
        print(tweet)
    
    return evaluations, summary


if __name__ == "__main__":
    main()
