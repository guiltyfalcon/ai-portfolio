#!/usr/bin/env python3
"""
BetBrain AI — Otterline + Polymarket Data Fetcher
Combines AI consensus picks with real-money prediction market odds
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

# Configuration
OTTERLINE_NBA_URL = "https://gvwawacjgghesljfzbph.supabase.co/functions/v1/free-nba-picks"
OTTERLINE_NHL_URL = "https://gvwawacjgghesljfzbph.supabase.co/functions/v1/free-nhl-picks"
POLYMARKET_SKILL_PATH = "/Users/djryan/skills/polymarket-odds/polymarket.mjs"
OUTPUT_DIR = Path("/Users/djryan/.openclaw/data/betbrain-external-data/")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_otterline_picks(league="nba", date=None):
    """Fetch picks from Otterline API"""
    url = OTTERLINE_NBA_URL if league == "nba" else OTTERLINE_NHL_URL
    params = {}
    if date:
        params["date"] = date
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Fetched {league.upper()} picks from Otterline")
        print(f"  - Type: {data.get('type', 'N/A')}")
        print(f"  - Notice: {data.get('notice', 'N/A')}")
        print(f"  - Picks count: {len(data.get('picks', []))}")
        
        return data
    except Exception as e:
        print(f"✗ Error fetching Otterline {league.upper()}: {e}")
        return None


def fetch_polymarket_markets(search_terms):
    """Fetch Polymarket markets using the installed skill CLI"""
    markets = {}
    
    for term in search_terms:
        try:
            result = subprocess.run(
                ["node", POLYMARKET_SKILL_PATH, "search", term],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                # Parse JSON output from CLI
                try:
                    markets[term] = json.loads(result.stdout)
                    print(f"✓ Fetched Polymarket markets for '{term}'")
                    if isinstance(markets[term], list):
                        print(f"  - Found {len(markets[term])} markets")
                except json.JSONDecodeError:
                    markets[term] = {"raw_output": result.stdout}
                    print(f"✓ Fetched Polymarket for '{term}' (raw output)")
            else:
                print(f"✗ Polymarket CLI error for '{term}': {result.stderr}")
                markets[term] = {"error": result.stderr}
                
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout fetching Polymarket for '{term}'")
            markets[term] = {"error": "timeout"}
        except Exception as e:
            print(f"✗ Error fetching Polymarket for '{term}': {e}")
            markets[term] = {"error": str(e)}
    
    return markets


def calculate_confidence_score(otterline_tier, polymarket_price=None):
    """
    Calculate combined confidence score from Otterline tier + Polymarket probability
    """
    # Otterline tier weights
    tier_weights = {
        "elite": 0.9,
        "verified": 0.75,
        "strong": 0.6,
        "lean": 0.5,
        "pass": 0.3
    }
    
    base_score = tier_weights.get(otterline_tier.lower(), 0.5)
    
    # Adjust based on Polymarket alignment (if available)
    if polymarket_price:
        # Polymarket price = implied probability
        # Higher alignment = higher confidence
        if polymarket_price >= 0.65:
            base_score = min(1.0, base_score + 0.1)
        elif polymarket_price <= 0.35:
            base_score = max(0.0, base_score - 0.1)
    
    return round(base_score, 2)


def format_picks_for_betbrain(otterline_data, polymarket_data, league):
    """Format combined data for BetBrain consumption"""
    formatted_picks = []
    
    if not otterline_data or "picks" not in otterline_data:
        return formatted_picks
    
    picks = otterline_data.get("picks", [])
    date = otterline_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    for pick in picks:
        matchup = pick.get("matchup", "Unknown")
        team = pick.get("pick", "Unknown")
        tier = pick.get("tier", "unknown")
        
        # Search Polymarket for this team/matchup
        team_name = team.split("@")[-1].strip() if "@" in team else team
        polymarket_match = None
        polymarket_price = None
        
        for search_term, markets in polymarket_data.items():
            if isinstance(markets, list):
                for market in markets:
                    if team_name.lower() in str(market).lower():
                        polymarket_match = market
                        # Extract price if available
                        if isinstance(market, dict):
                            polymarket_price = market.get("price", market.get("yesBid", None))
                        break
            if polymarket_match:
                break
        
        # Calculate combined confidence
        confidence = calculate_confidence_score(tier, polymarket_price)
        
        formatted_pick = {
            "league": league.upper(),
            "date": date,
            "matchup": matchup,
            "pick": team,
            "otterline_tier": tier,
            "otterline_confidence": confidence,
            "polymarket_match": polymarket_match is not None,
            "polymarket_price": polymarket_price,
            "combined_confidence": confidence,
            "fetched_at": datetime.now().isoformat()
        }
        
        # Add NBA-specific fields
        if league == "nba":
            formatted_pick["consensus_count"] = pick.get("consensus_count", 0)
            formatted_pick["combo_win_rate"] = pick.get("combo_win_rate", 0)
        
        # Add NHL-specific fields
        if league == "nhl":
            formatted_pick["score"] = pick.get("score", 0)
            formatted_pick["moneyPuckWinProb"] = pick.get("moneyPuckWinProb", 0)
        
        formatted_picks.append(formatted_pick)
    
    return formatted_picks


def generate_twitter_thread(picks):
    """Generate Twitter thread text from combined picks"""
    if not picks:
        return "No picks available today."
    
    date = datetime.now().strftime("%m/%d")
    lines = [f"🧠 BETBRAIN AI PICKS ({date}) — Enhanced with Otterline + Polymarket\n"]
    
    # Group by confidence
    elite_picks = [p for p in picks if p["otterline_tier"].lower() in ["elite", "verified"]]
    strong_picks = [p for p in picks if p["otterline_tier"].lower() == "strong"]
    
    for i, pick in enumerate(elite_picks[:3], 1):
        team = pick["pick"].split("@")[-1].strip() if "@" in pick["pick"] else pick["pick"]
        confidence = pick["combined_confidence"]
        pm_indicator = "📊" if pick["polymarket_match"] else ""
        
        lines.append(f"{i}. {team} {pm_indicator}")
        lines.append(f"   Tier: {pick['otterline_tier'].upper()} | Confidence: {confidence:.0%}")
        if pick.get("polymarket_price"):
            lines.append(f"   Polymarket: {pick['polymarket_price']:.0%}")
        lines.append("")
    
    if strong_picks:
        lines.append(f"💪 Strong: {len(strong_picks)} additional picks")
    
    lines.append("\n📊 Data > Guessing")
    lines.append("#NBA #SportsBetting #BetBrain")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("BetBrain AI — Otterline + Polymarket Fetcher")
    print("=" * 60)
    print()
    
    # Fetch Otterline picks
    print("🦦 Fetching Otterline picks...")
    nba_picks = fetch_otterline_picks("nba")
    nhl_picks = fetch_otterline_picks("nhl")
    print()
    
    # Build search terms for Polymarket
    search_terms = []
    if nba_picks and "picks" in nba_picks:
        for pick in nba_picks["picks"]:
            team = pick.get("pick", "")
            if "@" in team:
                teams = team.split("@")
                search_terms.extend([t.strip() for t in teams])
    
    if nhl_picks and "picks" in nhl_picks:
        for pick in nhl_picks["picks"]:
            team = pick.get("pick", "")
            if "@" in team:
                teams = team.split("@")
                search_terms.extend([t.strip() for t in teams])
    
    # Remove duplicates and limit to top 5
    search_terms = list(dict.fromkeys(search_terms))[:5]
    
    # Fetch Polymarket markets
    print("📊 Fetching Polymarket markets...")
    polymarket_data = fetch_polymarket_markets(search_terms) if search_terms else {}
    print()
    
    # Format combined data
    print("🔄 Combining data sources...")
    all_picks = []
    
    if nba_picks:
        nba_formatted = format_picks_for_betbrain(nba_picks, polymarket_data, "nba")
        all_picks.extend(nba_formatted)
    
    if nhl_picks:
        nhl_formatted = format_picks_for_betbrain(nhl_picks, polymarket_data, "nhl")
        all_picks.extend(nhl_formatted)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"otterline_polymarket_{timestamp}.json"
    
    output_data = {
        "fetched_at": datetime.now().isoformat(),
        "otterline": {
            "nba": nba_picks,
            "nhl": nhl_picks
        },
        "polymarket": polymarket_data,
        "combined_picks": all_picks,
        "twitter_thread": generate_twitter_thread(all_picks)
    }
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Saved to {output_file}")
    print()
    
    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total picks: {len(all_picks)}")
    print(f"  - NBA: {len([p for p in all_picks if p['league'] == 'NBA'])}")
    print(f"  - NHL: {len([p for p in all_picks if p['league'] == 'NHL'])}")
    print(f"Polymarket matches: {sum(1 for p in all_picks if p['polymarket_match'])}")
    print()
    
    # Print Twitter thread
    print("=" * 60)
    print("TWITTER THREAD DRAFT")
    print("=" * 60)
    print(output_data["twitter_thread"])
    print()
    
    return output_data


if __name__ == "__main__":
    main()
