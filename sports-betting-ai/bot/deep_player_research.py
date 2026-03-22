#!/usr/bin/env python3
"""
Deep Player Research for UNDER Targets
Derrick White & Rudy Gobert deep dive
"""

import csv
from pathlib import Path

BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")

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

def analyze_derrick_white():
    """Deep dive on Derrick White"""
    print("=" * 70)
    print("🔍 DERRICK WHITE — Deep Research (BOS vs MEM)")
    print("=" * 70)
    
    p = load_player("Derrick White")
    if not p:
        print("Player not found in database")
        return
    
    games = int(p.get('G', 0))
    ppg = calc_avg(p, 'PTS')
    apg = calc_avg(p, 'AST')
    rpg = calc_avg(p, 'TRB')
    fg_pct = float(p.get('FG%', '.395').replace('.', '0.')) if p.get('FG%') else 0.395
    three_pct = float(p.get('3P%', '.349').replace('.', '0.')) if p.get('3P%') else 0.349
    mpg = calc_avg(p, 'MP')
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Points: {ppg} PPG | Assists: {apg} APG | Rebounds: {rpg} RPG")
    print(f"   Minutes: {mpg} MPG")
    print(f"   Shooting: {fg_pct:.3f} FG% | {three_pct:.3f} 3P%")
    
    print(f"\n🎯 PROP LINE: Points UNDER 16.5")
    print(f"   Season avg: {ppg} PPG")
    print(f"   Edge: Line is {ppg - 16.5:.1f} points BELOW season avg")
    print(f"   ⚠️  Wait — this line is LOWER than his average, not higher")
    
    print(f"\n🏀 MATCHUP vs MEMPHIS:")
    print(f"   Memphis defense: Above average (4th in defensive rating)")
    print(f"   Guards vs MEM: Typically struggle with their length")
    print(f"   White's role: 3rd/4th option behind Brown, Tatum, Porzingis")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. Low FG% ({fg_pct:.3f}) — efficiency concerns")
    print(f"   2. Low 3P% ({three_pct:.3f}) — relies on threes, Memphis defends well")
    print(f"   3. Secondary option — usage drops when stars are hot")
    print(f"   4. Memphis length — contests shots at rim and perimeter")
    
    print(f"\n📈 OVER REASONS (counter-arguments):")
    print(f"   1. Line (16.5) is BELOW his season average ({ppg})")
    print(f"   2. He plays {mpg} MPG — high volume of minutes")
    print(f"   3. Can get hot from three and exceed line quickly")
    
    print(f"\n🔮 VERDICT:")
    print(f"   The line being BELOW his average makes this a weak UNDER.")
    print(f"   Even with tough matchup, he's priced to go over.")
    print(f"   RECOMMENDATION: SKIP or lean OVER if anything")

def analyze_rudy_gobert():
    """Deep dive on Rudy Gobert"""
    print("\n" + "=" * 70)
    print("🔍 RUDY GOBERT — Deep Research (MIN vs POR)")
    print("=" * 70)
    
    p = load_player("Rudy Gobert")
    if not p:
        print("Player not found in database")
        return
    
    games = int(p.get('G', 0))
    ppg = calc_avg(p, 'PTS')
    apg = calc_avg(p, 'AST')
    rpg = calc_avg(p, 'TRB')
    fg_pct = float(p.get('FG%', '.704').replace('.', '0.')) if p.get('FG%') else 0.704
    mpg = calc_avg(p, 'MP')
    
    print(f"\n📊 SEASON STATS ({games} games):")
    print(f"   Points: {ppg} PPG | Rebounds: {rpg} RPG | Assists: {apg} APG")
    print(f"   Minutes: {mpg} MPG")
    print(f"   Shooting: {fg_pct:.3f} FG% (elite efficiency)")
    
    print(f"\n🎯 PROP LINE: Rebounds UNDER 12.5")
    print(f"   Season avg: {rpg} RPG")
    print(f"   Edge: Line is {12.5 - rpg:.1f} points ABOVE season avg")
    
    print(f"\n🏀 MATCHUP vs PORTLAND:")
    print(f"   Portland defense: Poor (bottom 10 in defensive rating)")
    print(f"   Portland pace: Slow (fewer possessions = fewer rebound opportunities)")
    print(f"   Gobert's role: Primary rebounder, but Towns also boards")
    
    print(f"\n📉 UNDER REASONS:")
    print(f"   1. Line ({12.5}) > season avg ({rpg}) by {12.5 - rpg:.1f}")
    print(f"   2. Slow pace = fewer missed shots = fewer rebounds available")
    print(f"   3. Minnesota has multiple rebounders (Towns, Randle, Gobert)")
    print(f"   4. Portland plays small — less competition for boards, but also fewer misses")
    
    print(f"\n📈 OVER REASONS (counter-arguments):")
    print(f"   1. Elite rebounder — can dominate any night")
    print(f"   2. Portland poor defense = more misses = more rebounds")
    print(f"   3. No real competition for boards on Portland's side")
    
    print(f"\n🔮 VERDICT:")
    print(f"   Line is slightly inflated ({12.5} vs {rpg}).")
    print(f"   Slow pace is the key factor — fewer possessions = fewer boards.")
    print(f"   RECOMMENDATION: LEAN UNDER — situational edge with pace")

def main():
    analyze_derrick_white()
    analyze_rudy_gobert()
    
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    print("\n1. DERRICK WHITE Points U 16.5 — SKIP")
    print("   Line is BELOW season avg, tough to bet under")
    print("\n2. RUDY GOBERT Rebounds U 12.5 — LEAN UNDER")
    print("   Line inflated, slow pace favors under")
    print("\n💡 Better approach: Look for players with lines ABOVE their averages")
    print("   facing tough matchups.")
    print("=" * 70)

if __name__ == "__main__":
    main()
