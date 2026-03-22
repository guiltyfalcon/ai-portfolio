#!/usr/bin/env python3
"""
Deep Research on Top 5 Inflated UNDER Lines
"""

import csv
from pathlib import Path

BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")

# Matchup context
MATCHUPS = {
    'DET': {'opp': 'GSW', 'def_rating': 'below_avg', 'pace': 'fast'},
    'BRK': {'opp': 'NYK', 'def_rating': 'elite', 'pace': 'slow'},
    'NYK': {'opp': 'BRK', 'def_rating': 'poor', 'pace': 'slow'},
}

RESEARCH_TARGETS = [
    {'name': 'Caris LeVert', 'team': 'DET', 'prop': 'points', 'line': 13.5, 'season': 7.3, 'inflation': 6.2},
    {'name': 'Jalen Wilson', 'team': 'BRK', 'prop': 'points', 'line': 10.5, 'season': 5.2, 'inflation': 5.3},
    {'name': 'Mikal Bridges', 'team': 'NYK', 'prop': 'points', 'line': 18.5, 'season': 14.8, 'inflation': 3.7},
    {'name': 'Jalen Wilson', 'team': 'BRK', 'prop': 'rebounds', 'line': 4.5, 'season': 1.6, 'inflation': 2.9},
    {'name': 'Caris LeVert', 'team': 'DET', 'prop': 'rebounds', 'line': 4.5, 'season': 1.8, 'inflation': 2.7},
]

def load_player(name):
    with open(BETMONSTER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Player') == name:
                return row
    return None

def calc_avg(player, stat):
    total = int(player.get(stat, 0))
    games = int(player.get('G', 1))
    return round(total / games, 1) if games > 0 else 0

def analyze_caris_levert_points():
    print("=" * 75)
    print("🔍 #1: CARIS LEVERT (DET) — Points UNDER 13.5")
    print("=" * 75)
    
    p = load_player("Caris LeVert")
    if not p:
        print("Player not found")
        return
    
    games = int(p.get('G', 0))
    ppg = calc_avg(p, 'PTS')
    apg = calc_avg(p, 'AST')
    rpg = calc_avg(p, 'TRB')
    mpg = calc_avg(p, 'MP')
    fg_pct = float(p.get('FG%', '.420').replace('.', '0.')) if p.get('FG%') else 0.420
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Points: {ppg} PPG | Assists: {apg} APG | Rebounds: {rpg} RPG")
    print(f"   Minutes: {mpg} MPG | FG%: {fg_pct:.3f}")
    
    print(f"\n🎯 PROP LINE: Points UNDER 13.5")
    print(f"   Season avg: {ppg} PPG")
    print(f"   INFLATION: Line is {13.5 - ppg:.1f} points ABOVE season avg!")
    
    print(f"\n🏀 MATCHUP vs GOLDEN STATE:")
    print(f"   GSW defense: Below average (good for offense)")
    print(f"   GSW pace: FAST (more possessions)")
    print(f"   LeVert's role: 3rd/4th option behind Cade, Duren, Harris")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. MASSIVE line inflation (+{13.5 - ppg:.1f}) — priced like a starter")
    print(f"   2. Only {mpg} MPG — limited opportunity")
    print(f"   3. Low efficiency ({fg_pct:.3f} FG%) — needs volume to hit")
    print(f"   4. 4th scoring option — usage inconsistent")
    
    print(f"\n📈 OVER REASONS:")
    print(f"   1. Fast pace = more possessions")
    print(f"   2. GSW below avg defense")
    print(f"   3. Can get hot from midrange")
    
    print(f"\n🔮 VERDICT: STRONG UNDER")
    print(f"   The inflation is extreme. Even with good matchup,")
    print(f"   he's not a 13.5 PPG player. Line is mispriced.")
    print(f"   CONFIDENCE: 75%")

def analyze_jalen_wilson_points():
    print("\n" + "=" * 75)
    print("🔍 #2: JALEN WILSON (BRK) — Points UNDER 10.5")
    print("=" * 75)
    
    p = load_player("Jalen Wilson")
    if not p:
        print("Player not found")
        return
    
    games = int(p.get('G', 0))
    ppg = calc_avg(p, 'PTS')
    mpg = calc_avg(p, 'MP')
    fg_pct = float(p.get('FG%', '.419').replace('.', '0.')) if p.get('FG%') else 0.419
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Points: {ppg} PPG | Minutes: {mpg} MPG | FG%: {fg_pct:.3f}")
    
    print(f"\n🎯 PROP LINE: Points UNDER 10.5")
    print(f"   Season avg: {ppg} PPG")
    print(f"   INFLATION: Line is {10.5 - ppg:.1f} points ABOVE season avg!")
    
    print(f"\n🏀 MATCHUP vs NEW YORK:")
    print(f"   NYK defense: ELITE (top 3 in NBA)")
    print(f"   NYK pace: SLOW (fewer possessions)")
    print(f"   Wilson's role: Bench player, inconsistent minutes")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. EXTREME inflation (+{10.5 - ppg:.1f}) for a bench player")
    print(f"   2. Elite defense (NYK) — scoring will be tough")
    print(f"   3. Slow pace = fewer opportunities")
    print(f"   4. Low efficiency ({fg_pct:.3f} FG%)")
    print(f"   5. Limited minutes ({mpg} MPG)")
    
    print(f"\n📈 OVER REASONS:")
    print(f"   1. Brooklyn has injuries — might get more run")
    print(f"   2. Garbage time potential if NYK blows them out")
    
    print(f"\n🔮 VERDICT: STRONG UNDER")
    print(f"   Worst of both worlds: inflated line + tough matchup.")
    print(f"   He's a 5 PPG player priced at 10.5.")
    print(f"   CONFIDENCE: 80%")

def analyze_mikal_bridges_points():
    print("\n" + "=" * 75)
    print("🔍 #3: MIKAL BRIDGES (NYK) — Points UNDER 18.5")
    print("=" * 75)
    
    p = load_player("Mikal Bridges")
    if not p:
        print("Player not found")
        return
    
    games = int(p.get('G', 0))
    ppg = calc_avg(p, 'PTS')
    mpg = calc_avg(p, 'MP')
    fg_pct = float(p.get('FG%', '.488').replace('.', '0.')) if p.get('FG%') else 0.488
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Points: {ppg} PPG | Minutes: {mpg} MPG | FG%: {fg_pct:.3f}")
    
    print(f"\n🎯 PROP LINE: Points UNDER 18.5")
    print(f"   Season avg: {ppg} PPG")
    print(f"   INFLATION: Line is {18.5 - ppg:.1f} points ABOVE season avg")
    
    print(f"\n🏀 MATCHUP vs BROOKLYN:")
    print(f"   BRK defense: POOR (bottom 5 in NBA)")
    print(f"   BRK pace: SLOW")
    print(f"   Bridges' role: 3rd option behind Brunson, KAT")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. Line inflated (+{18.5 - ppg:.1f}) above season avg")
    print(f"   2. 3rd option — usage varies")
    print(f"   3. Slow pace = fewer possessions")
    
    print(f"\n📈 OVER REASONS:")
    print(f"   1. Brooklyn defense is terrible")
    print(f"   2. High minutes ({mpg} MPG) — opportunity is there")
    print(f"   3. Good efficiency ({fg_pct:.3f} FG%)")
    print(f"   4. Could blow up vs weak defense")
    
    print(f"\n🔮 VERDICT: MODERATE UNDER")
    print(f"   Inflated line but great matchup. Risky.")
    print(f"   CONFIDENCE: 60%")

def analyze_jalen_wilson_rebounds():
    print("\n" + "=" * 75)
    print("🔍 #4: JALEN WILSON (BRK) — Rebounds UNDER 4.5")
    print("=" * 75)
    
    p = load_player("Jalen Wilson")
    if not p:
        print("Player not found")
        return
    
    games = int(p.get('G', 0))
    rpg = calc_avg(p, 'TRB')
    mpg = calc_avg(p, 'MP')
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Rebounds: {rpg} RPG | Minutes: {mpg} MPG")
    
    print(f"\n🎯 PROP LINE: Rebounds UNDER 4.5")
    print(f"   Season avg: {rpg} RPG")
    print(f"   INFLATION: Line is {4.5 - rpg:.1f} above season avg")
    
    print(f"\n🏀 MATCHUP vs NEW YORK:")
    print(f"   NYK: Elite defense, slow pace")
    print(f"   Wilson: Bench player, limited minutes")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. Line nearly 3x his season average!")
    print(f"   2. Only {mpg} MPG — not on court enough")
    print(f"   3. Not a primary rebounder")
    print(f"   4. Slow pace = fewer missed shots")
    
    print(f"\n🔮 VERDICT: STRONG UNDER")
    print(f"   4.5 rebounds for a bench player getting {mpg} mins is crazy.")
    print(f"   CONFIDENCE: 85%")

def analyze_caris_levert_rebounds():
    print("\n" + "=" * 75)
    print("🔍 #5: CARIS LEVERT (DET) — Rebounds UNDER 4.5")
    print("=" * 75)
    
    p = load_player("Caris LeVert")
    if not p:
        print("Player not found")
        return
    
    games = int(p.get('G', 0))
    rpg = calc_avg(p, 'TRB')
    mpg = calc_avg(p, 'MP')
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Rebounds: {rpg} RPG | Minutes: {mpg} MPG")
    
    print(f"\n🎯 PROP LINE: Rebounds UNDER 4.5")
    print(f"   Season avg: {rpg} RPG")
    print(f"   INFLATION: Line is {4.5 - rpg:.1f} above season avg")
    
    print(f"\n🏀 MATCHUP vs GOLDEN STATE:")
    print(f"   GSW: Below avg defense, fast pace")
    print(f"   LeVert: Guard/wing, not a primary rebounder")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. Line is 2.5x his season average")
    print(f"   2. He's a guard — rebounding not his game")
    print(f"   3. Duren, Harris, Stewart eat up rebounds")
    print(f"   4. Fast pace helps scoring, not his rebounding")
    
    print(f"\n📈 OVER REASONS:")
    print(f"   1. Fast pace = more missed shots = more boards")
    print(f"   2. Could get lucky with long rebounds")
    
    print(f"\n🔮 VERDICT: MODERATE UNDER")
    print(f"   Inflated but not as extreme as others.")
    print(f"   CONFIDENCE: 65%")

def summary():
    print("\n" + "=" * 75)
    print("📋 TOP 5 UNDER SUMMARY")
    print("=" * 75)
    print("\n🔥 STRONGEST PLAYS:")
    print("   1. Jalen Wilson Reb U 4.5 — 85% confidence")
    print("   2. Jalen Wilson Pts U 10.5 — 80% confidence")
    print("   3. Caris LeVert Pts U 13.5 — 75% confidence")
    print("\n⚡ MODERATE PLAYS:")
    print("   4. Caris LeVert Reb U 4.5 — 65% confidence")
    print("   5. Mikal Bridges Pts U 18.5 — 60% confidence")
    print("\n💡 Best value: Wilson unders — extreme inflation + tough matchup")
    print("=" * 75)

def main():
    analyze_caris_levert_points()
    analyze_jalen_wilson_points()
    analyze_mikal_bridges_points()
    analyze_jalen_wilson_rebounds()
    analyze_caris_levert_rebounds()
    summary()

if __name__ == "__main__":
    main()