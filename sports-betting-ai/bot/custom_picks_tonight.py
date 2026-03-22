#!/usr/bin/env python3
"""
Custom BetMonster picks for tonight's games (from screenshot)
NYK vs BKN, GSW vs DET, POR vs MIN, BOS vs MEM
"""

import csv
from pathlib import Path

BETMONSTER_CSV = Path("/Users/djryan/.openclaw/skills/betmonster/br-stats-complete.csv")

# Tonight's teams from screenshot
TONIGHT_TEAMS = {'NYK', 'BRK', 'GSW', 'DET', 'POR', 'MIN', 'BOS', 'MEM'}

# Key players to highlight
KEY_PLAYERS = {
    'NYK': ['Jalen Brunson', 'Karl-Anthony Towns', 'Mikal Bridges', 'OG Anunoby', 'Josh Hart'],
    'BRK': ['Ziaire Williams', 'Jalen Wilson', 'Terance Mann'],
    'GSW': ['Stephen Curry', 'Brandin Podziemski', 'Draymond Green', 'Moses Moody'],
    'DET': ['Cade Cunningham', 'Jalen Duren', 'Tobias Harris', 'Caris LeVert'],
    'POR': ['Scoot Henderson', 'Shaedon Sharpe', 'Jerami Grant', 'Deni Avdija'],
    'MIN': ['Anthony Edwards', 'Julius Randle', 'Donte DiVincenzo', 'Naz Reid'],
    'BOS': ['Jaylen Brown', 'Derrick White', 'Payton Pritchard'],
    'MEM': ['Ja Morant', 'GG Jackson II', 'Jaylen Wells', 'Ty Jerome']
}

def load_player_data():
    """Load BetMonster data for tonight's teams"""
    players = []
    with open(BETMONSTER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row.get('Team', '')
            if team in TONIGHT_TEAMS:
                players.append(row)
    return players

def calculate_ppg(player):
    """Calculate points per game"""
    pts = int(player.get('PTS', 0))
    games = int(player.get('G', 1))
    return round(pts / games, 1) if games > 0 else 0

def get_form_emoji(ppg, team):
    """Get form indicator"""
    if ppg >= 25:
        return '🔥'
    elif ppg >= 18:
        return '⚡'
    elif ppg >= 12:
        return '➡️'
    else:
        return '❄️'

def generate_picks():
    players = load_player_data()
    
    print("=" * 70)
    print("🧠 BETMONSTER PICKS — TONIGHT'S GAMES (03/20)")
    print("=" * 70)
    print("\n📊 MATCHUPS:")
    print("   • NYK vs BKN (7:30pm)")
    print("   • GSW vs DET (7:30pm)")
    print("   • POR vs MIN (8:00pm)")
    print("   • BOS vs MEM (8:00pm)")
    print()
    
    # Group by team
    by_team = {team: [] for team in TONIGHT_TEAMS}
    for p in players:
        team = p.get('Team', '')
        if team in by_team:
            by_team[team].append(p)
    
    # Sort each team by PPG
    for team in by_team:
        by_team[team].sort(key=lambda x: calculate_ppg(x), reverse=True)
    
    print("=" * 70)
    print("🔒 TOP PICKS BY GAME")
    print("=" * 70)
    
    games = [
        ("NYK vs BKN", "NYK", "BRK"),
        ("GSW vs DET", "GSW", "DET"),
        ("POR vs MIN", "POR", "MIN"),
        ("BOS vs MEM", "BOS", "MEM")
    ]
    
    all_picks = []
    
    for game_name, team1, team2 in games:
        print(f"\n🏀 {game_name}")
        print("-" * 50)
        
        for team in [team1, team2]:
            print(f"\n   [{team}] Top Scorers:")
            top_3 = by_team[team][:3]
            for i, p in enumerate(top_3, 1):
                name = p.get('Player', 'Unknown')
                ppg = calculate_ppg(p)
                fg_pct = p.get('FG%', '.000').replace('.', '')[:3]
                fg_pct = f".{fg_pct}" if fg_pct else ".000"
                emoji = get_form_emoji(ppg, team)
                
                # Estimate a reasonable prop line (PPG - 1.5 for over)
                prop_line = round(ppg - 1.5) if ppg > 15 else round(ppg - 0.5)
                prop_line = max(prop_line, 10)
                
                print(f"      {i}. {name}")
                print(f"         Season: {ppg} PPG | FG%: {fg_pct}")
                print(f"         Suggested Prop: Over {prop_line}.5 pts {emoji}")
                
                all_picks.append({
                    'player': name,
                    'team': team,
                    'ppg': ppg,
                    'prop_line': prop_line,
                    'emoji': emoji,
                    'game': game_name
                })
    
    # Top overall picks
    print("\n" + "=" * 70)
    print("🎯 TOP 5 BETMONSTER PICKS (All Games)")
    print("=" * 70)
    
    # Sort by PPG
    all_picks.sort(key=lambda x: x['ppg'], reverse=True)
    
    for i, pick in enumerate(all_picks[:5], 1):
        print(f"\n{i}. {pick['player']} ({pick['team']})")
        print(f"   Game: {pick['game']}")
        print(f"   Season Avg: {pick['ppg']} PPG")
        print(f"   Suggested: Over {pick['prop_line']}.5 pts {pick['emoji']}")
        
        # Add simple analysis
        if pick['ppg'] >= 25:
            print(f"   📈 Elite scorer, high volume")
        elif pick['ppg'] >= 20:
            print(f"   📈 Primary option, consistent")
        elif pick['ppg'] >= 15:
            print(f"   📊 Solid contributor")
        else:
            print(f"   📊 Role player, lower volume")
    
    print("\n" + "=" * 70)
    print("⚠️  Note: These are data-driven suggestions based on season averages.")
    print("   Check current odds and injury reports before betting.")
    print("=" * 70)

if __name__ == "__main__":
    generate_picks()
