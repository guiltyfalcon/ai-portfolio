#!/usr/bin/env python3
"""
BetMonster UNDER Analyzer for tonight's games
Uses season stats to identify potential UNDER opportunities
"""

import csv
from pathlib import Path
from datetime import datetime

BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")

# Tonight's teams from screenshot
TONIGHT_TEAMS = {'NYK', 'BRK', 'GSW', 'DET', 'POR', 'MIN', 'BOS', 'MEM'}

def load_players():
    """Load all players from BetMonster database"""
    players = []
    with open(BETMONSTER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Team') in TONIGHT_TEAMS:
                players.append(row)
    return players

def calc_ppg(player):
    """Calculate points per game"""
    pts = int(player.get('PTS', 0))
    games = int(player.get('G', 1))
    return round(pts / games, 1) if games > 0 else 0

def calc_apg(player):
    """Calculate assists per game"""
    ast = int(player.get('AST', 0))
    games = int(player.get('G', 1))
    return round(ast / games, 1) if games > 0 else 0

def calc_rpg(player):
    """Calculate rebounds per game"""
    trb = int(player.get('TRB', 0))
    games = int(player.get('G', 1))
    return round(trb / games, 1) if games > 0 else 0

def analyze_unders():
    players = load_players()
    
    print("=" * 70)
    print("🎯 BETMONSTER UNDER ANALYZER — Tonight's Games (03/20)")
    print("=" * 70)
    print("\n📊 Looking for UNDER opportunities based on season averages...")
    print("   (Players who may be overvalued by sportsbooks)\n")
    
    under_candidates = []
    
    for p in players:
        name = p.get('Player', '')
        team = p.get('Team', '')
        games = int(p.get('G', 0))
        
        if games < 10:  # Skip players with few games
            continue
            
        ppg = calc_ppg(p)
        apg = calc_apg(p)
        rpg = calc_rpg(p)
        
        # Estimate typical prop lines (based on season averages)
        # Sportsbooks usually set lines at season avg + 0.5 to 1.5
        est_pts_line = round(ppg + 0.5)
        est_ast_line = round(apg + 0.5) if apg > 3 else round(apg)
        est_reb_line = round(rpg + 0.5) if rpg > 5 else round(rpg)
        
        # UNDER opportunities: players trending DOWN or facing tough matchups
        # For now, flag players where line might be too high
        
        # Check for low efficiency or declining trends
        fg_pct = float(p.get('FG%', '.000').replace('.', '0.')) if p.get('FG%') else 0
        
        # Potential UNDER candidates
        reasons = []
        
        # High volume but low efficiency = variance risk
        if ppg > 20 and fg_pct < 0.45:
            reasons.append(f"Low FG% ({fg_pct:.3f}) for volume scorer")
        
        # Very high line relative to production
        if ppg > 0 and est_pts_line > ppg + 2:
            reasons.append(f"Line likely inflated ({est_pts_line} vs {ppg} avg)")
        
        # Role players with sporadic production
        if ppg < 12 and games > 30:
            reasons.append("Low-volume role player, inconsistent")
        
        if reasons:
            under_candidates.append({
                'name': name,
                'team': team,
                'ppg': ppg,
                'apg': apg,
                'rpg': rpg,
                'est_pts_line': est_pts_line,
                'est_ast_line': est_ast_line,
                'est_reb_line': est_reb_line,
                'fg_pct': fg_pct,
                'games': games,
                'reasons': reasons
            })
    
    # Sort by PPG descending
    under_candidates.sort(key=lambda x: x['ppg'], reverse=True)
    
    print(f"Found {len(under_candidates)} potential UNDER candidates:\n")
    
    for i, c in enumerate(under_candidates[:10], 1):
        print(f"{i}. {c['name']} ({c['team']})")
        print(f"   Season: {c['ppg']} PPG, {c['apg']} APG, {c['rpg']} RPG | FG%: {c['fg_pct']:.3f}")
        print(f"   Est. Lines: Pts O/U {c['est_pts_line']}.5, Ast O/U {c['est_ast_line']}.5, Reb O/U {c['est_reb_line']}.5")
        print(f"   ⚠️  UNDER reasons:")
        for r in c['reasons']:
            print(f"      • {r}")
        print()
    
    # Specific UNDER recommendations
    print("=" * 70)
    print("🔒 TOP UNDER PICKS (Based on Data)")
    print("=" * 70)
    
    # Filter for best under candidates
    best_unders = [c for c in under_candidates if c['fg_pct'] < 0.44 and c['ppg'] > 15]
    
    if best_unders:
        for i, c in enumerate(best_unders[:5], 1):
            print(f"\n{i}. {c['name']} ({c['team']}) — Points UNDER {c['est_pts_line']}.5")
            print(f"   Why: Low efficiency ({c['fg_pct']:.3f} FG%) on high volume")
            print(f"   Season avg: {c['ppg']} PPG — line may be inflated")
    else:
        print("\nNo strong UNDER signals found in current data.")
        print("Consider: Injury situations, rest days, or matchup-specific factors")
    
    print("\n" + "=" * 70)
    print("💡 Note: This is based on season averages. Check current odds and")
    print("   recent form (last 5 games) before placing bets.")
    print("=" * 70)
    
    return under_candidates

if __name__ == "__main__":
    analyze_unders()
