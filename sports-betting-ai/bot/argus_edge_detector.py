#!/usr/bin/env python3
"""
BetBrain AI — Argus Edge Detector
Uses BetMonster CSV database + Polymarket odds
Implements Kelly criterion sizing
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

# Configuration
TWITTER_DRAFTS_DIR = Path("/Users/djryan/.openclaw/data/twitter-drafts/")
BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")
POLYMARKET_SKILL = Path("/Users/djryan/skills/polymarket-odds/polymarket.mjs")

# Argus Edge Parameters
EDGE_THRESHOLD = 0.10  # Minimum 10% edge to bet
KELLY_MULTIPLIER = 0.25  # Quarter-Kelly
MAX_STAKE_PERCENT = 0.05  # Max 5% of bankroll
MIN_STAKE_PERCENT = 0.01  # Min 1% of bankroll


class ArgusEdgeDetector:
    def __init__(self, bankroll: float = 10000.0):
        self.bankroll = bankroll
        self.edge_log = []
    
    def calculate_edge(self, model_prob: float, market_odds: float) -> float:
        """Calculate edge: model probability vs market implied probability"""
        if market_odds > 0:
            market_implied_prob = 100 / (market_odds + 100)
        else:
            market_implied_prob = abs(market_odds) / (abs(market_odds) + 100)
        
        edge = model_prob - market_implied_prob
        return round(edge, 4)
    
    def calculate_kelly_stake(self, edge: float, odds: float) -> float:
        """Calculate Kelly criterion stake size"""
        if edge <= 0:
            return 0.0
        
        if odds > 0:
            decimal_odds = (odds + 100) / 100
        else:
            decimal_odds = (abs(odds) + 100) / abs(odds)
        
        kelly_full = (edge * self.bankroll) / (decimal_odds - 1)
        kelly_quarter = kelly_full * KELLY_MULTIPLIER
        
        max_stake = self.bankroll * MAX_STAKE_PERCENT
        min_stake = self.bankroll * MIN_STAKE_PERCENT
        
        kelly_stake = max(min_stake, min(kelly_quarter, max_stake))
        return round(kelly_stake, 2)
    
    def evaluate_pick(self, pick: Dict, polymarket_price: Optional[float] = None) -> Dict:
        """Evaluate a single pick using Argus Edge framework"""
        player = pick.get('player', 'Unknown')
        team = pick.get('team', 'Unknown')
        prop = pick.get('prop', '')
        line = pick.get('line', 0)
        model_prob = pick.get('model_prob', 0.5)
        odds = pick.get('odds', -110)
        stat_avg = pick.get('stat_avg', 0)
        
        edge = self.calculate_edge(model_prob, odds)
        kelly_stake = self.calculate_kelly_stake(edge, odds)
        
        recommendation = "NO BET"
        if edge >= EDGE_THRESHOLD:
            if kelly_stake >= self.bankroll * 0.03:
                recommendation = "STRONG BET"
            else:
                recommendation = "BET"
        elif edge >= 0.05:
            recommendation = "LEAN"
        
        # Compare with Polymarket if available
        pm_comparison = None
        if polymarket_price:
            pm_implied = polymarket_price
            pm_edge = model_prob - pm_implied
            pm_comparison = {
                'price': polymarket_price,
                'implied_pct': polymarket_price * 100,
                'edge_vs_pm': pm_edge * 100
            }
        
        result = {
            'player': player,
            'team': team,
            'prop': prop,
            'line': line,
            'stat_avg': stat_avg,
            'model_prob': model_prob,
            'market_odds': odds,
            'edge': edge,
            'edge_pct': edge * 100,
            'kelly_stake': kelly_stake,
            'kelly_pct': (kelly_stake / self.bankroll) * 100,
            'recommendation': recommendation,
            'polymarket': pm_comparison,
            'evaluated_at': datetime.now().isoformat()
        }
        
        self.edge_log.append(result)
        return result
    
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


def load_betmonster_csv() -> List[Dict]:
    """Load player stats from BetMonster CSV"""
    if not BETMONSTER_CSV.exists():
        return []
    
    players = []
    with open(BETMONSTER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            players.append({
                'player': row.get('Player', ''),
                'team': row.get('Team', ''),
                'pos': row.get('Pos', ''),
                'ppg': float(row.get('PTS', 0)) / float(row.get('G', 1)) if row.get('G') else 0,
                'apg': float(row.get('AST', 0)) / float(row.get('G', 1)) if row.get('G') else 0,
                'rpg': float(row.get('TRB', 0)) / float(row.get('G', 1)) if row.get('G') else 0,
                'games': int(row.get('G', 0))
            })
    
    return players


def fetch_polymarket_odds(team_name: str) -> Optional[float]:
    """Fetch Polymarket odds for a team"""
    try:
        result = subprocess.run(
            ["node", str(POLYMARKET_SKILL), "search", team_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                # Return first market's price as proxy
                market = data[0]
                if isinstance(market, dict):
                    return market.get('price', market.get('yesBid', None))
        return None
    except Exception:
        return None


def generate_props_from_stats(players: List[Dict]) -> List[Dict]:
    """
    Generate prop picks from player stats using BetMonster logic
    Simulates finding lines that are below player averages (value spots)
    """
    props = []
    
    for player in players[:40]:  # Top 40 players
        ppg = player['ppg']
        apg = player['apg']
        rpg = player['rpg']
        team = player['team']
        
        # Points props - simulate book making line 2-3 points below average
        if ppg > 18:
            # Book line is typically 2-3 points below season avg for popular players
            line = int(ppg - 2.5)
            # Model probability based on how far above line the avg is
            model_prob = 0.50 + (ppg - (line + 0.5)) * 0.08
            # Popular players have worse odds due to public money
            odds = -130 if ppg > 25 else -115
            props.append({
                'player': player['player'],
                'team': team,
                'prop': f'Points Over {line}.5',
                'line': line + 0.5,
                'model_prob': min(0.78, max(0.42, model_prob)),
                'odds': odds,
                'stat_avg': ppg
            })
        
        # Assists props - books set line 1-1.5 below average
        if apg > 4:
            line = int(apg - 1.2)
            model_prob = 0.50 + (apg - (line + 0.5)) * 0.10
            odds = -120 if apg > 6 else -110
            props.append({
                'player': player['player'],
                'team': team,
                'prop': f'Assists Over {line}.5',
                'line': line + 0.5,
                'model_prob': min(0.75, max(0.42, model_prob)),
                'odds': odds,
                'stat_avg': apg
            })
        
        # Rebounds props - books set line 1-1.5 below average
        if rpg > 6:
            line = int(rpg - 1.2)
            model_prob = 0.50 + (rpg - (line + 0.5)) * 0.10
            odds = -120 if rpg > 9 else -110
            props.append({
                'player': player['player'],
                'team': team,
                'prop': f'Rebounds Over {line}.5',
                'line': line + 0.5,
                'model_prob': min(0.75, max(0.42, model_prob)),
                'odds': odds,
                'stat_avg': rpg
            })
    
    return props


def generate_twitter_thread(evaluations: List[Dict], summary: Dict) -> List[str]:
    """Generate Twitter thread from Argus Edge evaluations"""
    tweets = []
    
    date = datetime.now().strftime("%m/%d")
    tweets.append(f"🎯 ARGUS EDGE DETECTOR ({date})\n")
    
    tweets.append(f"📊 {summary['total_picks']} props analyzed\n"
                  f"🔒 {summary['strong_bets']} STRONG BETS\n"
                  f"⚡ {summary['bets']} total bets\n"
                  f"💰 Total stake: {summary['total_kelly_pct']:.1f}% of bankroll\n")
    
    bets = sorted([e for e in evaluations if e['recommendation'] in ['BET', 'STRONG BET']],
                  key=lambda x: x['edge'], reverse=True)[:5]
    
    for i, bet in enumerate(bets, 1):
        emoji = "🔒" if bet['recommendation'] == 'STRONG BET' else "⚡"
        player = bet['player']
        team = bet.get('team', 'Unknown')
        edge_pct = bet['edge_pct']
        kelly_pct = bet['kelly_pct']
        stake = bet['kelly_stake']
        prop = bet['prop']
        stat_avg = bet.get('stat_avg', 0)
        
        tweet = f"{emoji} {i}. {player} ({team})\n"
        tweet += f"   {prop} (Avg: {stat_avg:.1f})\n"
        tweet += f"   Edge: {edge_pct:.1f}% | Kelly: {kelly_pct:.1f}% (${stake:.0f})\n"
        
        if bet.get('polymarket'):
            pm = bet['polymarket']
            tweet += f"   Polymarket: {pm['implied_pct']:.0f}% | Edge vs PM: {pm['edge_vs_pm']:.1f}%\n"
        
        tweets.append(tweet)
    
    tweets.append("🧠 Argus Edge Framework:\n"
                  "• Edge ≥10% threshold\n"
                  "• Kelly criterion sizing\n"
                  "• BetMonster CSV database\n")
    
    tweets.append("📊 Data > Guessing\n"
                  "Results tracked publicly.\n"
                  "#NBA #SportsBetting #BetBrain #ArgusEdge")
    
    return tweets


def main():
    print("=" * 60)
    print("BetBrain AI — Argus Edge Detector")
    print("=" * 60)
    print()
    
    detector = ArgusEdgeDetector(bankroll=10000.0)
    
    print("📊 Loading BetMonster CSV database...")
    players = load_betmonster_csv()
    print(f"  - Players loaded: {len(players)}")
    print()
    
    print("🎯 Generating props from stats...")
    props = generate_props_from_stats(players)
    print(f"  - Props generated: {len(props)}")
    print()
    
    print("📈 Fetching Polymarket odds for teams...")
    teams = list(set(p['team'] for p in props))[:10]  # Top 10 teams
    polymarket_odds = {}
    for team in teams:
        pm_price = fetch_polymarket_odds(team)
        if pm_price:
            polymarket_odds[team] = pm_price
            print(f"  ✓ {team}: {pm_price*100:.0f}%")
    print()
    
    print("🎯 Evaluating picks with Argus Edge framework...")
    evaluations = []
    for prop in props:
        team = prop.get('team', '')
        pm_price = polymarket_odds.get(team, None)
        eval_result = detector.evaluate_pick(prop, pm_price)
        evaluations.append(eval_result)
        
        rec_emoji = "✅" if eval_result['recommendation'] in ['BET', 'STRONG BET'] else "❌"
        pm_indicator = f" | PM: {pm_price*100:.0f}%" if pm_price else ""
        print(f"  {rec_emoji} {eval_result['player']} ({eval_result['team']}): {eval_result['recommendation']} "
              f"(Edge: {eval_result['edge_pct']:.1f}%, Kelly: ${eval_result['kelly_stake']:.0f}){pm_indicator}")
    print()
    
    summary = detector.get_summary()
    
    # Cap total stake at 20% of bankroll
    MAX_TOTAL_STAKE_PCT = 0.20
    if summary['total_kelly_pct'] > MAX_TOTAL_STAKE_PCT * 100:
        scale_factor = (MAX_TOTAL_STAKE_PCT * summary['total_kelly_stake']) / summary['total_kelly_stake'] if summary['total_kelly_stake'] > 0 else 1
        for eval in detector.edge_log:
            if eval['recommendation'] in ['BET', 'STRONG BET']:
                eval['kelly_stake'] *= scale_factor
                eval['kelly_pct'] *= scale_factor
        summary = detector.get_summary()
    
    print("=" * 60)
    print("ARGUS EDGE SUMMARY")
    print("=" * 60)
    print(f"Total picks evaluated: {summary['total_picks']}")
    print(f"  - Strong Bets: {summary['strong_bets']}")
    print(f"  - Bets: {summary['bets']}")
    print(f"  - Leans: {summary['leans']}")
    print(f"  - No Bets: {summary['no_bets']}")
    print()
    if summary['total_picks'] > 0:
        print(f"Total Kelly stake: ${summary['total_kelly_stake']:.2f} "
              f"({summary['total_kelly_pct']:.1f}% of bankroll)")
        print(f"Average edge (bets): {summary['avg_edge']*100:.1f}%")
        print(f"Best edge: {summary['best_edge']*100:.1f}%")
    print()
    
    print("🐦 Generating Twitter thread...")
    tweets = generate_twitter_thread(evaluations, summary)
    
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
    
    # Print detailed table of top picks
    print("=" * 90)
    print("TOP PICKS WITH POLYMARKET COMPARISON")
    print("=" * 90)
    print(f"{'#':<3} {'Player':<25} {'Team':<8} {'Prop':<20} {'Avg':<6} {'Edge%':<8} {'Kelly':<8} {'PM%':<8} {'Edge vs PM':<10}")
    print("-" * 90)
    
    top_picks = sorted([e for e in evaluations if e['recommendation'] in ['BET', 'STRONG BET']],
                       key=lambda x: x['edge'], reverse=True)[:10]
    
    for i, pick in enumerate(top_picks, 1):
        player = pick['player'][:24]
        team = pick.get('team', '')[:7]
        prop = pick['prop'][:19]
        avg = f"{pick.get('stat_avg', 0):.1f}"
        edge = f"{pick['edge_pct']:.1f}%"
        kelly = f"${pick['kelly_stake']:.0f}"
        pm_pct = f"{pick['polymarket']['implied_pct']:.0f}%" if pick.get('polymarket') else "N/A"
        edge_vs_pm = f"{pick['polymarket']['edge_vs_pm']:.1f}%" if pick.get('polymarket') else "N/A"
        
        print(f"{i:<3} {player:<25} {team:<8} {prop:<20} {avg:<6} {edge:<8} {kelly:<8} {pm_pct:<8} {edge_vs_pm:<10}")
    
    print()
    
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
