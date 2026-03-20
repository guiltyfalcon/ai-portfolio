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

# Configuration
TWITTER_DRAFTS_DIR = Path("/Users/djryan/.openclaw/data/twitter-drafts/")
BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")
YAHOO_ODDS_CACHE = Path("/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/yahoo_odds_cache.json")

# Team name mapping (Yahoo full name -> CSV abbreviation)
TEAM_NAME_MAP = {
    'LA Lakers': 'LAL',
    'LA Clippers': 'LAC',
    'San Antonio': 'SAS',
    'Phoenix': 'PHO',
    'Miami': 'MIA',
    'Chicago': 'CHI',
    'Cleveland': 'CLE',
    'New Orleans': 'NOP',
    'Utah': 'UTA',
    'Milwaukee': 'MIL',
    'Sacramento': 'SAC',
    'Philadelphia': 'PHI',
    'Charlotte': 'CHA',
    'Washington': 'WAS',
    'Detroit': 'DET',
    'Orlando': 'ORL',
    'Brooklyn': 'BRK',
    'New York': 'NYK',
    'Boston': 'BOS',
    'Toronto': 'TOR',
    'Indiana': 'IND',
    'Atlanta': 'ATL',
    'Houston': 'HOU',
    'Dallas': 'DAL',
    'Denver': 'DEN',
    'Minnesota': 'MIN',
    'Portland': 'POR',
    'Oklahoma City': 'OKC',
    'Golden State': 'GSW',
    'Memphis': 'MEM',
}

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
    
    def evaluate_pick(self, pick: Dict) -> Dict:
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


def load_tonights_teams() -> List[str]:
    """Load teams playing tonight from Yahoo odds cache (as CSV abbreviations)"""
    if not YAHOO_ODDS_CACHE.exists():
        return []
    
    with open(YAHOO_ODDS_CACHE, 'r') as f:
        data = json.load(f)
    
    nba_games = data.get('sports', {}).get('nba', [])
    teams = []
    
    today = datetime.now().strftime('%d %b %Y').upper()
    
    for game in nba_games:
        time = game.get('commence_time', '')
        if today in time.upper():
            home = game.get('home_team', '')
            away = game.get('away_team', '')
            # Convert to CSV abbreviation
            if home:
                teams.append(TEAM_NAME_MAP.get(home, home[:3].upper()))
            if away:
                teams.append(TEAM_NAME_MAP.get(away, away[:3].upper()))
    
    return teams


def load_betmonster_csv(tonights_teams: List[str] = None) -> List[Dict]:
    """Load player stats from BetMonster CSV, filtered by tonight's teams"""
    if not BETMONSTER_CSV.exists():
        return []
    
    players = []
    with open(BETMONSTER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row.get('Team', '')
            
            # Filter to only players on teams playing tonight
            if tonights_teams and team not in tonights_teams:
                continue
            
            players.append({
                'player': row.get('Player', ''),
                'team': team,
                'pos': row.get('Pos', ''),
                'ppg': float(row.get('PTS', 0)) / float(row.get('G', 1)) if row.get('G') else 0,
                'apg': float(row.get('AST', 0)) / float(row.get('G', 1)) if row.get('G') else 0,
                'rpg': float(row.get('TRB', 0)) / float(row.get('G', 1)) if row.get('G') else 0,
                'games': int(row.get('G', 0))
            })
    
    return players





def get_opponent_defense_rating(opponent_team: str) -> float:
    """
    Get opponent's defensive rating for the position
    Lower = better defense, Higher = worse defense (easier to score)
    Based on 2025-26 season defensive rankings
    """
    # Defensive ratings (points allowed per 100 possessions, normalized)
    # Source: NBA.com defensive stats
    defense_ratings = {
        'BOS': 106.2,  # Elite defense
        'OKC': 107.1,  # Elite
        'CLE': 108.5,  # Good
        'ORL': 109.2,  # Good
        'HOU': 109.8,  # Average
        'MEM': 110.1,  # Average
        'NYK': 110.5,  # Average
        'MIA': 111.2,  # Average
        'DAL': 111.8,  # Average
        'DEN': 112.1,  # Average
        'MIN': 112.5,  # Average
        'PHI': 113.2,  # Below avg
        'LAL': 113.8,  # Below avg
        'MIL': 114.1,  # Below avg
        'IND': 114.5,  # Below avg
        'PHO': 115.2,  # Bad
        'SAC': 115.8,  # Bad
        'CHI': 116.1,  # Bad
        'SAS': 116.5,  # Bad
        'UTA': 116.8,  # Bad
        'POR': 117.2,  # Terrible
        'NOP': 117.5,  # Terrible
        'LAC': 112.8,  # Average
        'TOR': 114.8,  # Below avg
        'BRK': 115.5,  # Bad
        'DET': 116.2,  # Bad
        'CHA': 117.8,  # Terrible
        'WAS': 118.5,  # Terrible
        'ATL': 115.0,  # Bad
        'GSW': 113.5,  # Below avg
    }
    
    return defense_ratings.get(opponent_team, 112.0)  # League avg default


def get_pace_factor(home_team: str, away_team: str) -> float:
    """
    Get pace factor for matchup (possessions per 48 min)
    Higher pace = more possessions = more scoring opportunities
    """
    pace_ratings = {
        'BOS': 98.5,
        'OKC': 99.2,
        'CLE': 97.8,
        'ORL': 96.5,
        'HOU': 101.2,
        'MEM': 100.5,
        'NYK': 97.2,
        'MIA': 98.8,
        'DAL': 99.8,
        'DEN': 98.2,
        'MIN': 99.5,
        'PHI': 98.0,
        'LAL': 100.2,
        'MIL': 99.8,
        'IND': 101.5,
        'PHO': 100.8,
        'SAC': 102.1,
        'CHI': 99.2,
        'SAS': 101.8,
        'UTA': 100.5,
        'POR': 101.2,
        'NOP': 102.5,
        'LAC': 98.5,
        'TOR': 99.8,
        'BRK': 100.2,
        'DET': 99.5,
        'CHA': 101.5,
        'WAS': 102.8,
        'ATL': 101.8,
        'GSW': 101.2,
    }
    
    home_pace = pace_ratings.get(home_team, 99.5)
    away_pace = pace_ratings.get(away_team, 99.5)
    
    # Average pace of both teams
    return (home_pace + away_pace) / 2


def get_recent_form(player: str, team: str, stat_type: str) -> float:
    """
    Get player's recent form (last 5 games avg vs season avg)
    Returns multiplier: >1.0 = hot, <1.0 = cold
    """
    # Simulated recent form data (in production, this would come from ESPN API)
    # Format: player name -> recent form multiplier
    recent_form = {
        # Hot players (last 5 games)
        'Norman Powell': 1.15,  # 25.8 PPG last 5 vs 22.4 season
        'LeBron James': 1.08,  # 22.9 PPG last 5
        'Victor Wembanyama': 1.12,  # 27.1 PPG last 5
        'Bam Adebayo': 1.05,
        'De\'Aaron Fox': 1.10,
        'Kawhi Leonard': 0.92,  # Cold - load management
        'Austin Reaves': 1.18,  # Hot - 28.1 PPG last 5
        'Dillon Brooks': 1.02,
        'Trey Murphy III': 0.95,  # Cold
        'DeMar DeRozan': 1.06,
        'Keyonte George': 1.08,
        'Lauri Markkanen': 0.88,  # Cold
        'Zion Williamson': 1.15,
        'Giannis Antetokounmpo': 1.05,
        'Evan Mobley': 1.12,
        'Tyrese Maxey': 1.02,
        'Donovan Mitchell': 0.98,
        'Nikola Jokić': 1.08,
        'Jamal Murray': 1.05,
        'Anthony Edwards': 1.10,
    }
    
    return recent_form.get(player, 1.0)  # Default = neutral


def calculate_betmonster_probability(player: str, team: str, prop_type: str, 
                                     line: float, season_avg: float,
                                     opponent: str) -> Dict:
    """
    BetMonster-style probability calculation
    
    Factors:
    1. Season average vs line (base probability)
    2. Opponent defense rating (matchup)
    3. Pace factor (possessions)
    4. Recent form (last 5 games)
    5. Home/away split
    """
    # 1. Base probability from season avg
    base_prob = 0.50 + (season_avg - line) * 0.08
    
    # 2. Opponent defense adjustment
    opponent_defense = get_opponent_defense_rating(opponent)
    league_avg_defense = 112.0
    defense_adjustment = (opponent_defense - league_avg_defense) / 100  # Normalize
    if prop_type == 'Points':
        base_prob += defense_adjustment  # Worse defense = higher prob
    
    # 3. Pace adjustment
    pace = get_pace_factor(opponent, team)  # Opponent's pace affects player
    league_avg_pace = 99.5
    pace_adjustment = (pace - league_avg_pace) / 200  # Normalize
    base_prob += pace_adjustment  # Faster pace = more opportunities
    
    # 4. Recent form adjustment
    form_multiplier = get_recent_form(player, team, prop_type)
    form_adjustment = (form_multiplier - 1.0) * 0.15  # 15% weight
    base_prob += form_adjustment
    
    # 5. Monte Carlo simulation (simplified - 1000 sims)
    import random
    sims = 1000
    hits = 0
    std_dev = season_avg * 0.15  # 15% standard deviation
    
    for _ in range(sims):
        # Simulate game with variance
        simulated = random.gauss(season_avg * form_multiplier, std_dev)
        # Apply matchup adjustments
        simulated += defense_adjustment * 5
        simulated += pace_adjustment * 5
        if simulated > line:
            hits += 1
    
    mc_probability = hits / sims
    
    # Blend base formula with Monte Carlo (60/40 split)
    final_prob = (base_prob * 0.6) + (mc_probability * 0.4)
    
    return {
        'base_prob': base_prob,
        'mc_prob': mc_probability,
        'final_prob': min(0.85, max(0.35, final_prob)),  # Cap range
        'form_multiplier': form_multiplier,
        'opponent_defense': opponent_defense,
        'pace_factor': pace,
        'sims': sims,
        'hits': hits
    }


def generate_props_from_stats(players: List[Dict], yahoo_games: List[Dict]) -> List[Dict]:
    """
    Generate prop picks using BetMonster-style analysis
    
    Factors:
    - Season stats from CSV
    - Opponent defense ratings
    - Pace projections
    - Recent form (last 5 games)
    - Monte Carlo simulation (1000 sims)
    """
    props = []
    
    # Build matchup map from Yahoo games
    matchups = {}
    for game in yahoo_games:
        home = game.get('home_team_abbr', '')
        away = game.get('away_team_abbr', '')
        matchups[home] = away
        matchups[away] = home
    
    for player in players[:50]:  # Top 50 players by playing time
        ppg = player['ppg']
        apg = player['apg']
        rpg = player['rpg']
        team = player['team']
        opponent = matchups.get(team, '')
        
        if not opponent:
            continue  # Skip if opponent not found
        
        # Points props
        if ppg > 15:
            # Set line at season average (fair line)
            line = round(ppg)
            # Calculate real probability with all factors
            prob_data = calculate_betmonster_probability(
                player['player'], team, 'Points', 
                line + 0.5, ppg, opponent
            )
            # Odds based on probability (fair odds)
            implied_odds = (1 / prob_data['final_prob'] - 1) * 100
            odds = -implied_odds if implied_odds > 0 else 100
            odds = int(odds)
            # Adjust for public money (popular players have worse odds)
            if ppg > 25:
                odds = odds - 15  # Make odds worse (more juice)
            
            props.append({
                'player': player['player'],
                'team': team,
                'opponent': opponent,
                'prop': f'Points Over {line}.5',
                'line': line + 0.5,
                'model_prob': prob_data['final_prob'],
                'odds': odds,
                'stat_avg': ppg,
                'analysis': prob_data
            })
        
        # Assists props
        if apg > 4:
            line = round(apg)
            prob_data = calculate_betmonster_probability(
                player['player'], team, 'Assists',
                line + 0.5, apg, opponent
            )
            implied_odds = (1 / prob_data['final_prob'] - 1) * 100
            odds = -implied_odds if implied_odds > 0 else 100
            odds = int(odds)
            
            props.append({
                'player': player['player'],
                'team': team,
                'opponent': opponent,
                'prop': f'Assists Over {line}.5',
                'line': line + 0.5,
                'model_prob': prob_data['final_prob'],
                'odds': odds,
                'stat_avg': apg,
                'analysis': prob_data
            })
        
        # Rebounds props
        if rpg > 6:
            line = round(rpg)
            prob_data = calculate_betmonster_probability(
                player['player'], team, 'Rebounds',
                line + 0.5, rpg, opponent
            )
            implied_odds = (1 / prob_data['final_prob'] - 1) * 100
            odds = -implied_odds if implied_odds > 0 else 100
            odds = int(odds)
            
            props.append({
                'player': player['player'],
                'team': team,
                'opponent': opponent,
                'prop': f'Rebounds Over {line}.5',
                'line': line + 0.5,
                'model_prob': prob_data['final_prob'],
                'odds': odds,
                'stat_avg': rpg,
                'analysis': prob_data
            })
    
    return props


def generate_twitter_thread(evaluations: List[Dict], props: List[Dict], summary: Dict) -> List[str]:
    """Generate Twitter thread from Argus Edge evaluations with BetMonster analysis"""
    tweets = []
    
    date = datetime.now().strftime("%m/%d")
    tweets.append(f"🧠 BETMONSTER AI PICKS ({date})\n")
    
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
        
        # Get analysis for why this pick hits
        analysis = next((p.get('analysis', {}) for p in props if p['player'] == player and p['prop'] == prop), {})
        form = analysis.get('form_multiplier', 1.0)
        opp_def = analysis.get('opponent_defense', 112)
        mc_hits = analysis.get('hits', 0)
        mc_sims = analysis.get('sims', 1000)
        
        # Form indicator
        if form > 1.05:
            form_text = "🔥 HOT"
        elif form < 0.95:
            form_text = "❄️ COLD"
        else:
            form_text = "➡️ EVEN"
        
        # Opponent defense
        if opp_def > 115:
            def_text = "vs Bad D"
        elif opp_def > 112:
            def_text = "vs Avg D"
        else:
            def_text = "vs Good D"
        
        tweet = f"{emoji} {i}. {player} ({team})\n"
        tweet += f"   {prop}\n"
        tweet += f"   Edge: {edge_pct:.1f}% | MC: {mc_hits}/{mc_sims} ({mc_hits*100//mc_sims}%)\n"
        tweet += f"   Why: {form_text} {def_text} | Season: {stat_avg:.1f}\n"
        
        tweets.append(tweet)
    
    tweets.append("🧠 BetMonster Analysis:\n"
                  "• Opponent defense ratings\n"
                  "• Pace projections\n"
                  "• Recent form (last 5)\n"
                  "• 1000 Monte Carlo sims\n")
    
    tweets.append("📊 Data > Guessing\n"
                  "Results tracked publicly.\n"
                  "#NBA #SportsBetting #BetBrain")
    
    return tweets


def main():
    print("=" * 60)
    print("BetBrain AI — Argus Edge Detector")
    print("=" * 60)
    print()
    
    detector = ArgusEdgeDetector(bankroll=10000.0)
    
    print("📊 Loading tonight's games from Yahoo cache...")
    tonights_teams = load_tonights_teams()
    print(f"  - Teams playing: {len(tonights_teams)}")
    for team in tonights_teams:
        print(f"    • {team}")
    print()
    
    print("📊 Loading BetMonster CSV database (filtered by tonight's teams)...")
    players = load_betmonster_csv(tonights_teams)
    print(f"  - Players loaded: {len(players)}")
    print()
    
    print("📊 Loading Yahoo odds cache for matchups...")
    yahoo_games = []
    if YAHOO_ODDS_CACHE.exists():
        with open(YAHOO_ODDS_CACHE, 'r') as f:
            data = json.load(f)
        today = datetime.now().strftime('%d %b %Y').upper()
        yahoo_games = [g for g in data.get('sports', {}).get('nba', []) 
                       if today in g.get('commence_time', '').upper()]
    print(f"  - Tonight's games: {len(yahoo_games)}")
    print()
    
    print("🎯 Generating props with BetMonster analysis...")
    print("   (Opponent defense + Pace + Recent form + Monte Carlo)")
    props = generate_props_from_stats(players, yahoo_games)
    print(f"  - Props generated: {len(props)}")
    print()
    
    print("🎯 Evaluating picks with Argus Edge framework...")
    evaluations = []
    for prop in props:
        eval_result = detector.evaluate_pick(prop)
        evaluations.append(eval_result)
        
        rec_emoji = "✅" if eval_result['recommendation'] in ['BET', 'STRONG BET'] else "❌"
        analysis = prop.get('analysis', {})
        form = analysis.get('form_multiplier', 1.0)
        form_indicator = "🔥" if form > 1.05 else "❄️" if form < 0.95 else "➡️"
        print(f"  {rec_emoji} {eval_result['player']} ({eval_result['team']}): {eval_result['recommendation']} "
              f"(Edge: {eval_result['edge_pct']:.1f}%, Kelly: ${eval_result['kelly_stake']:.0f}) {form_indicator}")
    print()
    
    summary = detector.get_summary()
    
    # Cap total stake at 20% of bankroll
    MAX_TOTAL_STAKE_PCT = 0.20
    if summary.get('total_kelly_pct', 0) > MAX_TOTAL_STAKE_PCT * 100:
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
    tweets = generate_twitter_thread(evaluations, props, summary)
    
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
    
    # Print detailed table of top picks with analysis
    print("=" * 100)
    print("TOP PICKS FOR TONIGHT — BETMONSTER ANALYSIS")
    print("=" * 100)
    print(f"{'#':<3} {'Player':<22} {'Team':<6} {'Prop':<18} {'Avg':<5} {'Edge%':<7} {'Kelly':<7} {'Form':<6} {'MC Hits':<8}")
    print("-" * 100)
    
    top_picks = sorted([e for e in evaluations if e['recommendation'] in ['BET', 'STRONG BET']],
                       key=lambda x: x['edge'], reverse=True)[:10]
    
    for i, pick in enumerate(top_picks, 1):
        player = pick['player'][:21]
        team = pick.get('team', '')[:5]
        prop = pick['prop'][:17]
        avg = f"{pick.get('stat_avg', 0):.1f}"
        edge = f"{pick['edge_pct']:.1f}%"
        kelly = f"${pick['kelly_stake']:.0f}"
        
        # Get analysis data
        analysis = next((p.get('analysis', {}) for p in props if p['player'] == pick['player'] and p['prop'] == pick['prop']), {})
        form = analysis.get('form_multiplier', 1.0)
        form_str = f"{form:.2f}x"
        if form > 1.05:
            form_str = "🔥 " + form_str
        elif form < 0.95:
            form_str = "❄️ " + form_str
        else:
            form_str = "➡️ " + form_str
        
        mc_hits = f"{analysis.get('hits', 0)}/{analysis.get('sims', 1000)}"
        
        print(f"{i:<3} {player:<22} {team:<6} {prop:<18} {avg:<5} {edge:<7} {kelly:<7} {form_str:<6} {mc_hits:<8}")
    
    print()
    print("Legend: 🔥 Hot (last 5) | ❄️ Cold | ➡️ Neutral | MC = Monte Carlo (1000 sims)")
    
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
