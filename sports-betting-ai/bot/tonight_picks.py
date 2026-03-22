#!/usr/bin/env python3
"""
BetBrain AI — Picks for Tonight's Real Games
Uses BetMonster CSV + matchup analysis
"""

import csv
import random
from pathlib import Path
from datetime import datetime

# Teams from screenshot
TEAMS_PLAYING = ['NYK', 'BKN', 'GSW', 'DET', 'POR', 'MIN', 'BOS', 'MEM']

# Matchups from screenshot
MATCHUPS = {
    'NYK': 'BKN',  # Knicks @ Nets
    'BKN': 'NYK',
    'GSW': 'DET',  # Warriors @ Pistons
    'DET': 'GSW',
    'POR': 'MIN',  # Blazers @ Timberwolves
    'MIN': 'POR',
    'BOS': 'MEM',  # Celtics @ Grizzlies
    'MEM': 'BOS',
}

# Defensive ratings (points allowed per 100 poss)
DEFENSE_RATINGS = {
    'BOS': 106.2,  # Elite
    'NYK': 110.5,  # Average
    'MIN': 112.5,  # Average
    'MEM': 113.8,  # Below avg
    'GSW': 113.5,  # Below avg
    'DET': 116.2,  # Bad
    'POR': 117.2,  # Terrible
    'BKN': 115.5,  # Bad
}

# Pace ratings
PACE_RATINGS = {
    'MEM': 102.5,  # Fast
    'POR': 101.2,  # Fast
    'GSW': 101.2,  # Fast
    'MIN': 99.5,   # Average
    'DET': 99.5,   # Average
    'BKN': 100.2,  # Average
    'NYK': 97.2,   # Slow
    'BOS': 98.5,   # Slow
}

# Recent form (last 5 games multiplier)
RECENT_FORM = {
    # HOT
    'Anthony Edwards': 1.12,
    'Jaylen Brown': 1.08,
    'Jalen Brunson': 1.15,
    'Cade Cunningham': 1.10,
    'Ja Morant': 1.08,
    'Karl-Anthony Towns': 1.05,
    'Derrick White': 1.10,
    # COLD
    'Stephen Curry': 0.92,  # Load management
    'Julius Randle': 0.95,
    'Deni Avdija': 0.98,
    'Jerami Grant': 0.90,
    # NEUTRAL
}

def load_players():
    """Load players from tonight's teams"""
    csv_file = Path('/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv')
    players = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row.get('Team', '')
            if team not in TEAMS_PLAYING:
                continue
            
            ppg = float(row.get('PTS', 0)) / float(row.get('G', 1)) if row.get('G') else 0
            apg = float(row.get('AST', 0)) / float(row.get('G', 1)) if row.get('G') else 0
            rpg = float(row.get('TRB', 0)) / float(row.get('G', 1)) if row.get('G') else 0
            
            players.append({
                'player': row.get('Player', ''),
                'team': team,
                'ppg': ppg,
                'apg': apg,
                'rpg': rpg,
                'games': int(row.get('G', 0))
            })
    
    return players

def get_form(player):
    """Get recent form multiplier"""
    return RECENT_FORM.get(player, 1.0)

def calculate_edge(player, team, prop_type, line, stat_avg):
    """Calculate edge with matchup analysis"""
    opponent = MATCHUPS.get(team, '')
    
    # Base probability
    base_prob = 0.50 + (stat_avg - line) * 0.08
    
    # Opponent defense adjustment
    opp_defense = DEFENSE_RATINGS.get(opponent, 112.0)
    defense_adj = (opp_defense - 112.0) / 100
    if prop_type == 'Points':
        base_prob += defense_adj
    
    # Pace adjustment
    opp_pace = PACE_RATINGS.get(opponent, 99.5)
    pace_adj = (opp_pace - 99.5) / 200
    base_prob += pace_adj
    
    # Recent form
    form = get_form(player)
    form_adj = (form - 1.0) * 0.15
    base_prob += form_adj
    
    # Monte Carlo (1000 sims)
    sims = 1000
    hits = 0
    std_dev = stat_avg * 0.15
    
    for _ in range(sims):
        simulated = random.gauss(stat_avg * form, std_dev)
        simulated += defense_adj * 5
        simulated += pace_adj * 5
        if simulated > line:
            hits += 1
    
    mc_prob = hits / sims
    final_prob = (base_prob * 0.6) + (mc_prob * 0.4)
    
    return {
        'final_prob': min(0.85, max(0.35, final_prob)),
        'mc_hits': hits,
        'mc_sims': sims,
        'form': form,
        'opp_defense': opp_defense,
        'opp_pace': opp_pace
    }

def generate_picks(players):
    """Generate prop picks"""
    picks = []
    
    for player in players:
        if player['games'] < 10:  # Skip players with few games
            continue
        
        ppg = player['ppg']
        apg = player['apg']
        rpg = player['rpg']
        team = player['team']
        
        # Points props
        if ppg > 15:
            line = round(ppg)
            edge_data = calculate_edge(player['player'], team, 'Points', line + 0.5, ppg)
            edge = (edge_data['final_prob'] * 100) - 50  # Convert to edge %
            
            if edge >= 10:  # 10%+ edge threshold
                picks.append({
                    'player': player['player'],
                    'team': team,
                    'prop': f'Points Over {line}.5',
                    'line': line + 0.5,
                    'avg': ppg,
                    'edge': edge,
                    'mc_hits': edge_data['mc_hits'],
                    'form': edge_data['form'],
                    'opp': MATCHUPS.get(team, '')
                })
        
        # Assists props
        if apg > 4:
            line = round(apg)
            edge_data = calculate_edge(player['player'], team, 'Assists', line + 0.5, apg)
            edge = (edge_data['final_prob'] * 100) - 50
            
            if edge >= 10:
                picks.append({
                    'player': player['player'],
                    'team': team,
                    'prop': f'Assists Over {line}.5',
                    'line': line + 0.5,
                    'avg': apg,
                    'edge': edge,
                    'mc_hits': edge_data['mc_hits'],
                    'form': edge_data['form'],
                    'opp': MATCHUPS.get(team, '')
                })
        
        # Rebounds props
        if rpg > 6:
            line = round(rpg)
            edge_data = calculate_edge(player['player'], team, 'Rebounds', line + 0.5, rpg)
            edge = (edge_data['final_prob'] * 100) - 50
            
            if edge >= 10:
                picks.append({
                    'player': player['player'],
                    'team': team,
                    'prop': f'Rebounds Over {line}.5',
                    'line': line + 0.5,
                    'avg': rpg,
                    'edge': edge,
                    'mc_hits': edge_data['mc_hits'],
                    'form': edge_data['form'],
                    'opp': MATCHUPS.get(team, '')
                })
    
    # Sort by edge
    picks.sort(key=lambda x: x['edge'], reverse=True)
    return picks

def format_form(form):
    """Format form indicator"""
    if form > 1.05:
        return f"🔥 HOT ({form:.2f}x)"
    elif form < 0.95:
        return f"❄️ COLD ({form:.2f}x)"
    else:
        return f"➡️ EVEN ({form:.2f}x)"

def main():
    print("=" * 70)
    print("🧠 BETMONSTER AI PICKS — TONIGHT'S GAMES")
    print("=" * 70)
    print()
    print("Games:")
    print("• Knicks @ Nets — 7:30 PM ET")
    print("• Warriors @ Pistons — 7:30 PM ET")
    print("• Blazers @ Timberwolves — 8:00 PM ET")
    print("• Celtics @ Grizzlies — 8:00 PM ET")
    print()
    
    players = load_players()
    print(f"Players analyzed: {len(players)}")
    print()
    
    picks = generate_picks(players)
    print(f"Picks with 10%+ edge: {len(picks)}")
    print()
    
    # Top 5
    print("=" * 70)
    print("🎯 TOP 5 PICKS FOR TONIGHT")
    print("=" * 70)
    print()
    
    for i, pick in enumerate(picks[:5], 1):
        form_str = format_form(pick['form'])
        mc_pct = (pick['mc_hits'] / 10)  # Convert to percentage
        
        print(f"{i}. {pick['player']} ({pick['team']})")
        print(f"   Prop: {pick['prop']}")
        print(f"   Edge: {pick['edge']:.1f}%")
        print(f"   Form: {form_str}")
        print(f"   Monte Carlo: {pick['mc_hits']}/1000 ({mc_pct:.0f}%)")
        print(f"   Matchup: vs {pick['opp']}")
        print()

if __name__ == "__main__":
    main()
