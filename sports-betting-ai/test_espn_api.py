"""
Test script for ESPN All Sports API
Tests NBA, NFL, MLB, NHL endpoints
"""

import sys
sys.path.append('.')

from api.espn_all_sports import ESPNSportsAPI, get_player_data_unified
import json

def test_sport(sport: str):
    """Test API for a specific sport."""
    print(f"\n{'='*50}")
    print(f"Testing {sport} API")
    print('='*50)
    
    try:
        api = ESPNSportsAPI(sport)
        
        # Test 1: Get teams
        print(f"\n1. Getting {sport} teams...")
        teams = api.get_teams()
        if teams:
            print(f"   ✅ Found {len(teams)} teams")
            print(f"   First team: {teams[0].get('name')} (ID: {teams[0].get('id')})")
        else:
            print(f"   ❌ No teams found")
            return False
        
        # Test 2: Get players for first team
        team_id = teams[0].get('id')
        team_name = teams[0].get('name')
        print(f"\n2. Getting players for {team_name}...")
        players = api.get_team_players(team_id)
        if players:
            print(f"   ✅ Found {len(players)} players")
            if len(players) > 0:
                print(f"   First player: {players[0].get('name')} (ID: {players[0].get('id')})")
        else:
            print(f"   ❌ No players found")
        
        # Test 3: Get stats for first player
        if players:
            player_id = players[0].get('id')
            player_name = players[0].get('name')
            print(f"\n3. Getting stats for {player_name}...")
            stats = api.get_player_stats(player_id)
            if stats:
                print(f"   ✅ Stats found: {json.dumps(stats, indent=2)}")
            else:
                print(f"   ⚠️ No stats available (may be off-season or new player)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("ESPN All Sports API Test Suite")
    print("Testing free ESPN APIs for NBA, NFL, MLB, NHL")
    
    results = {}
    
    # Test each sport
    for sport in ['NBA', 'NFL', 'MLB', 'NHL']:
        results[sport] = test_sport(sport)
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    for sport, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{sport}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ All tests passed!' if all_passed else '⚠️ Some tests failed'}")
    
    return results

if __name__ == "__main__":
    main()
