#!/usr/bin/env python3
"""
Find Inflated Lines for Tonight's Games
Scans BetMonster database for lines that may be set too high
"""

import csv
from pathlib import Path

BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")

# Tonight's teams
TONIGHT_TEAMS = {'NYK', 'BRK', 'GSW', 'DET', 'POR', 'MIN', 'BOS', 'MEM'}

# Estimated prop lines based on typical sportsbook pricing
# Format: player_name: {team, est_pts_line, est_ast_line, est_reb_line}
ESTIMATED_LINES = {
    # NYK
    'Jalen Brunson': {'team': 'NYK', 'pts': 25.5, 'ast': 7.5, 'reb': 3.5},
    'Karl-Anthony Towns': {'team': 'NYK', 'pts': 20.5, 'ast': 3.5, 'reb': 11.5},
    'Mikal Bridges': {'team': 'NYK', 'pts': 18.5, 'ast': 3.5, 'reb': 4.5},
    'OG Anunoby': {'team': 'NYK', 'pts': 16.5, 'ast': 2.5, 'reb': 5.5},
    'Josh Hart': {'team': 'NYK', 'pts': 12.5, 'ast': 6.5, 'reb': 8.5},
    
    # BRK
    'Ziaire Williams': {'team': 'BRK', 'pts': 11.5, 'ast': 2.5, 'reb': 4.5},
    'Jalen Wilson': {'team': 'BRK', 'pts': 10.5, 'ast': 2.5, 'reb': 4.5},
    
    # GSW
    'Stephen Curry': {'team': 'GSW', 'pts': 26.5, 'ast': 6.5, 'reb': 4.5},
    'Brandin Podziemski': {'team': 'GSW', 'pts': 13.5, 'ast': 4.5, 'reb': 4.5},
    'Draymond Green': {'team': 'GSW', 'pts': 10.5, 'ast': 6.5, 'reb': 7.5},
    'Moses Moody': {'team': 'GSW', 'pts': 12.5, 'ast': 2.5, 'reb': 3.5},
    
    # DET
    'Cade Cunningham': {'team': 'DET', 'pts': 24.5, 'ast': 9.5, 'reb': 6.5},
    'Jalen Duren': {'team': 'DET', 'pts': 19.5, 'ast': 2.5, 'reb': 11.5},
    'Tobias Harris': {'team': 'DET', 'pts': 14.5, 'ast': 2.5, 'reb': 6.5},
    'Caris LeVert': {'team': 'DET', 'pts': 13.5, 'ast': 4.5, 'reb': 4.5},
    
    # POR
    'Scoot Henderson': {'team': 'POR', 'pts': 21.5, 'ast': 6.5, 'reb': 4.5},
    'Shaedon Sharpe': {'team': 'POR', 'pts': 20.5, 'ast': 3.5, 'reb': 4.5},
    'Jerami Grant': {'team': 'POR', 'pts': 18.5, 'ast': 2.5, 'reb': 4.5},
    'Deni Avdija': {'team': 'POR', 'pts': 23.5, 'ast': 4.5, 'reb': 7.5},
    
    # MIN
    'Anthony Edwards': {'team': 'MIN', 'pts': 28.5, 'ast': 5.5, 'reb': 6.5},
    'Julius Randle': {'team': 'MIN', 'pts': 21.5, 'ast': 5.5, 'reb': 7.5},
    'Donte DiVincenzo': {'team': 'MIN', 'pts': 14.5, 'ast': 3.5, 'reb': 4.5},
    'Jaden McDaniels': {'team': 'MIN', 'pts': 14.5, 'ast': 2.5, 'reb': 5.5},
    'Rudy Gobert': {'team': 'MIN', 'pts': 11.5, 'ast': 2.5, 'reb': 12.5},
    
    # BOS
    'Jaylen Brown': {'team': 'BOS', 'pts': 27.5, 'ast': 4.5, 'reb': 6.5},
    'Derrick White': {'team': 'BOS', 'pts': 16.5, 'ast': 5.5, 'reb': 4.5},
    'Payton Pritchard': {'team': 'BOS', 'pts': 15.5, 'ast': 3.5, 'reb': 3.5},
    
    # MEM
    'Ja Morant': {'team': 'MEM', 'pts': 19.5, 'ast': 8.5, 'reb': 4.5},
    'GG Jackson II': {'team': 'MEM', 'pts': 12.5, 'ast': 1.5, 'reb': 4.5},
    'Jaylen Wells': {'team': 'MEM', 'pts': 11.5, 'ast': 2.5, 'reb': 3.5},
    'Ty Jerome': {'team': 'MEM', 'pts': 20.5, 'ast': 4.5, 'reb': 3.5},
}

def load_player(name):
    """Load player from database"""
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

def analyze_inflated_lines():
    print("=" * 75)
    print("🔍 FINDING INFLATED LINES — Tonight's Games (03/20)")
    print("=" * 75)
    print("\nLooking for lines set ABOVE season averages...\n")
    
    inflated_picks = []
    
    for name, lines in ESTIMATED_LINES.items():
        player = load_player(name)
        if not player:
            continue
        
        games = int(player.get('G', 0))
        if games < 20:  # Need enough sample size
            continue
        
        ppg = calc_avg(player, 'PTS')
        apg = calc_avg(player, 'AST')
        rpg = calc_avg(player, 'TRB')
        fg_pct = float(player.get('FG%', '.450').replace('.', '0.')) if player.get('FG%') else 0.450
        
        team = lines['team']
        
        # Check each prop type for inflation
        # Points
        if lines['pts'] > ppg + 0.5:  # Line is 0.5+ above season avg
            inflated_picks.append({
                'name': name,
                'team': team,
                'prop_type': 'points',
                'line': lines['pts'],
                'season_avg': ppg,
                'diff': round(lines['pts'] - ppg, 1),
                'fg_pct': fg_pct,
                'games': games
            })
        
        # Assists
        if lines['ast'] > apg + 0.5:
            inflated_picks.append({
                'name': name,
                'team': team,
                'prop_type': 'assists',
                'line': lines['ast'],
                'season_avg': apg,
                'diff': round(lines['ast'] - apg, 1),
                'fg_pct': fg_pct,
                'games': games
            })
        
        # Rebounds
        if lines['reb'] > rpg + 0.5:
            inflated_picks.append({
                'name': name,
                'team': team,
                'prop_type': 'rebounds',
                'line': lines['reb'],
                'season_avg': rpg,
                'diff': round(lines['reb'] - rpg, 1),
                'fg_pct': fg_pct,
                'games': games
            })
    
    # Sort by inflation amount (descending)
    inflated_picks.sort(key=lambda x: x['diff'], reverse=True)
    
    print(f"Found {len(inflated_picks)} potentially inflated lines:\n")
    
    # Categorize by inflation severity
    strong_inflated = [p for p in inflated_picks if p['diff'] >= 1.5]
    moderate_inflated = [p for p in inflated_picks if 0.5 <= p['diff'] < 1.5]
    
    if strong_inflated:
        print("🔥 STRONGLY INFLATED (1.5+ above avg):\n")
        for i, p in enumerate(strong_inflated[:5], 1):
            print(f"{i}. {p['name']} ({p['team']}) — {p['prop_type'].title()} {p['line']}")
            print(f"   Season: {p['season_avg']} | Inflated by: +{p['diff']}")
            print(f"   Suggested: UNDER {p['line']}")
            print()
    
    if moderate_inflated:
        print("⚡ MODERATELY INFLATED (0.5-1.4 above avg):\n")
        for i, p in enumerate(moderate_inflated[:8], 1):
            print(f"{i}. {p['name']} ({p['team']}) — {p['prop_type'].title()} {p['line']}")
            print(f"   Season: {p['season_avg']} | Inflated by: +{p['diff']}")
            print(f"   Suggested: LEAN UNDER {p['line']}")
            print()
    
    print("=" * 75)
    print("💡 ANALYSIS SUMMARY")
    print("=" * 75)
    print(f"\nTotal inflated lines found: {len(inflated_picks)}")
    print(f"Strong plays (1.5+): {len(strong_inflated)}")
    print(f"Lean plays (0.5-1.4): {len(moderate_inflated)}")
    
    if strong_inflated:
        print(f"\n🎯 BEST UNDER BET:")
        best = strong_inflated[0]
        print(f"   {best['name']} — {best['prop_type'].title()} UNDER {best['line']}")
        print(f"   Line is {best['diff']} points above {best['season_avg']} season avg")
    
    print("\n⚠️  Verify current odds — these are estimated lines!")
    print("=" * 75)
    
    return inflated_picks

if __name__ == "__main__":
    analyze_inflated_lines()
