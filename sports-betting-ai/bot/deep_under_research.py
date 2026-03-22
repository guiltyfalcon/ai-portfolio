#!/usr/bin/env python3
"""
Deep UNDER Research for Tonight's Games
Analyzes matchups, recent form, and situational spots
"""

import csv
from pathlib import Path

BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")

# Tonight's matchups with defensive context
MATCHUPS = {
    'NYK': {'opponent': 'BRK', 'def_rating': 'poor', 'pace': 'slow'},
    'BRK': {'opponent': 'NYK', 'def_rating': 'elite', 'pace': 'slow'},
    'GSW': {'opponent': 'DET', 'def_rating': 'below_avg', 'pace': 'fast'},
    'DET': {'opponent': 'GSW', 'def_rating': 'below_avg', 'pace': 'fast'},
    'POR': {'opponent': 'MIN', 'def_rating': 'elite', 'pace': 'slow'},
    'MIN': {'opponent': 'POR', 'def_rating': 'poor', 'pace': 'slow'},
    'BOS': {'opponent': 'MEM', 'def_rating': 'above_avg', 'pace': 'medium'},
    'MEM': {'opponent': 'BOS', 'def_rating': 'elite', 'pace': 'medium'}
}

# Key players to analyze for UNDER
RESEARCH_TARGETS = [
    # High usage, tough matchup
    {'name': 'Jaylen Brown', 'team': 'BOS', 'prop_type': 'points', 'line': 27.5},
    {'name': 'Stephen Curry', 'team': 'GSW', 'prop_type': 'points', 'line': 26.5},
    {'name': 'Anthony Edwards', 'team': 'MIN', 'prop_type': 'points', 'line': 28.5},
    
    # Secondary options, inconsistent
    {'name': 'Derrick White', 'team': 'BOS', 'prop_type': 'points', 'line': 16.5},
    {'name': 'Jaden McDaniels', 'team': 'MIN', 'prop_type': 'points', 'line': 14.5},
    {'name': 'Brandin Podziemski', 'team': 'GSW', 'prop_type': 'assists', 'line': 4.5},
    
    # Rebound props
    {'name': 'Karl-Anthony Towns', 'team': 'NYK', 'prop_type': 'rebounds', 'line': 11.5},
    {'name': 'Rudy Gobert', 'team': 'MIN', 'prop_type': 'rebounds', 'line': 12.5},
]

def load_player(name):
    """Load specific player from database"""
    with open(BETMONSTER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Player') == name:
                return row
    return None

def calc_avg(player, stat):
    """Calculate per-game average"""
    total = int(player.get(stat, 0))
    games = int(player.get('G', 1))
    return round(total / games, 1) if games > 0 else 0

def analyze_under_opportunity(target):
    """Deep analysis for UNDER opportunity"""
    player = load_player(target['name'])
    if not player:
        return None
    
    team = target['team']
    matchup = MATCHUPS.get(team, {})
    opp = matchup.get('opponent', 'Unknown')
    def_rating = matchup.get('def_rating', 'avg')
    
    ppg = calc_avg(player, 'PTS')
    apg = calc_avg(player, 'AST')
    rpg = calc_avg(player, 'TRB')
    games = int(player.get('G', 0))
    fg_pct = float(player.get('FG%', '.000').replace('.', '0.')) if player.get('FG%') else 0
    
    prop_type = target['prop_type']
    line = target['line']
    
    # Get relevant stat
    if prop_type == 'points':
        season_avg = ppg
    elif prop_type == 'assists':
        season_avg = apg
    elif prop_type == 'rebounds':
        season_avg = rpg
    else:
        season_avg = ppg
    
    # UNDER analysis
    under_reasons = []
    confidence = 50  # Base confidence
    
    # 1. Line vs season average
    if line > season_avg + 1.5:
        under_reasons.append(f"Line ({line}) > {season_avg} season avg by {line - season_avg:.1f}")
        confidence += 10
    elif line > season_avg:
        under_reasons.append(f"Line ({line}) slightly above {season_avg} season avg")
        confidence += 5
    
    # 2. Defensive matchup
    if def_rating == 'elite':
        under_reasons.append(f"Tough matchup vs {opp} (elite defense)")
        confidence += 15
    elif def_rating == 'above_avg':
        under_reasons.append(f"Difficult matchup vs {opp} (above avg defense)")
        confidence += 8
    
    # 3. Efficiency concerns
    if prop_type == 'points' and fg_pct < 0.45 and ppg > 18:
        under_reasons.append(f"Low efficiency ({fg_pct:.3f} FG%) on volume")
        confidence += 5
    
    # 4. High line relative to role
    if prop_type == 'points' and ppg < 18 and line > 15:
        under_reasons.append("Secondary option, high variance")
        confidence += 5
    
    # 5. Rebound specific - check if it's a high line
    if prop_type == 'rebounds':
        if line >= 12:
            under_reasons.append(f"High rebound line ({line}) — needs elite board work")
            confidence += 5
        if def_rating == 'elite':
            under_reasons.append("Elite defense = fewer missed shots = fewer rebound opportunities")
            confidence += 8
    
    # 6. Assist specific
    if prop_type == 'assists':
        if line > apg + 1:
            under_reasons.append(f"Line ({line}) well above {apg} apg average")
            confidence += 10
    
    return {
        'name': target['name'],
        'team': team,
        'opp': opp,
        'prop_type': prop_type,
        'line': line,
        'season_avg': season_avg,
        'games': games,
        'fg_pct': fg_pct,
        'def_rating': def_rating,
        'reasons': under_reasons,
        'confidence': min(confidence, 95)
    }

def main():
    print("=" * 75)
    print("🔍 DEEP UNDER RESEARCH — Tonight's Games (03/20)")
    print("=" * 75)
    print("\nAnalyzing matchups, defensive ratings, and situational spots...\n")
    
    results = []
    for target in RESEARCH_TARGETS:
        result = analyze_under_opportunity(target)
        if result:
            results.append(result)
    
    # Sort by confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("📊 ANALYSIS RESULTS:\n")
    
    strong_unders = []
    lean_unders = []
    
    for r in results:
        if r['confidence'] >= 70:
            strong_unders.append(r)
        elif r['confidence'] >= 60:
            lean_unders.append(r)
    
    if strong_unders:
        print("🔒 STRONG UNDER PLAYS (70%+ confidence):\n")
        for i, r in enumerate(strong_unders, 1):
            print(f"{i}. {r['name']} ({r['team']} vs {r['opp']})")
            print(f"   Prop: {r['prop_type'].title()} UNDER {r['line']}")
            print(f"   Season: {r['season_avg']} {r['prop_type']}/game | Confidence: {r['confidence']}%")
            print(f"   Why:")
            for reason in r['reasons']:
                print(f"      • {reason}")
            print()
    
    if lean_unders:
        print("⚡ LEAN UNDER PLAYS (60-69% confidence):\n")
        for i, r in enumerate(lean_unders, 1):
            print(f"{i}. {r['name']} ({r['team']} vs {r['opp']})")
            print(f"   Prop: {r['prop_type'].title()} UNDER {r['line']}")
            print(f"   Season: {r['season_avg']} {r['prop_type']}/game | Confidence: {r['confidence']}%")
            print(f"   Why:")
            for reason in r['reasons']:
                print(f"      • {reason}")
            print()
    
    if not strong_unders and not lean_unders:
        print("No strong UNDER signals found with current data.")
        print("\nThis could mean:")
        print("  • Lines are well-calibrated to season averages")
        print("  • Matchups are neutral or favorable for offenses")
        print("  • Need injury/rest data for better edges")
    
    print("=" * 75)
    print("💡 BETMONSTER VERDICT:")
    print("=" * 75)
    
    if strong_unders:
        best = strong_unders[0]
        print(f"\n🎯 BEST UNDER BET: {best['name']} {best['prop_type'].title()} UNDER {best['line']}")
        print(f"   Confidence: {best['confidence']}%")
        print(f"   Key factor: {best['reasons'][0] if best['reasons'] else 'Matchup analysis'}")
    
    print("\n⚠️  Always verify current odds and check for late injury news!")
    print("=" * 75)

if __name__ == "__main__":
    main()