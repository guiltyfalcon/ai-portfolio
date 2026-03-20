#!/usr/bin/env python3
"""
BetBrain AI — Enhanced Twitter Thread Generator
Combines BetBrain picks + Otterline consensus + Polymarket odds
"""

import json
import os
from datetime import datetime
from pathlib import Path
import glob

# Configuration
OUTPUT_DIR = Path("/Users/djryan/.openclaw/data/betbrain-external-data/")
TWITTER_DRAFTS_DIR = Path("/Users/djryan/.openclaw/data/twitter-drafts/")
BETMONSTER_PICKS_DIR = Path("/Users/djryan/.openclaw/data/betmonster-picks/")

# Ensure directories exist
TWITTER_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


def load_latest_otterline_polymarket():
    """Load the most recent Otterline + Polymarket fetch"""
    files = sorted(OUTPUT_DIR.glob("otterline_polymarket_*.json"))
    if not files:
        print("⚠️ No Otterline + Polymarket data found")
        return None
    
    latest = files[-1]
    print(f"✓ Loaded: {latest.name}")
    
    with open(latest, 'r') as f:
        return json.load(f)


def load_latest_betmonster():
    """Load the most recent BetMonster picks"""
    files = sorted(BETMONSTER_PICKS_DIR.glob("*.json"))
    if not files:
        print("⚠️ No BetMonster data found")
        return None
    
    latest = files[-1]
    print(f"✓ Loaded: {latest.name}")
    
    with open(latest, 'r') as f:
        return json.load(f)


def calculate_enhanced_confidence(betmonster_confidence, otterline_tier, polymarket_price=None):
    """
    Combine BetMonster confidence with Otterline tier + Polymarket alignment
    """
    # BetMonster base confidence (0-100)
    base = betmonster_confidence if betmonster_confidence else 50
    
    # Otterline tier adjustment
    tier_bonus = {
        "elite": 15,
        "verified": 10,
        "strong": 5,
        "lean": 0,
        "pass": -10
    }
    
    # Polymarket alignment bonus
    pm_bonus = 0
    if polymarket_price:
        if polymarket_price >= 0.65:
            pm_bonus = 10  # Strong market alignment
        elif polymarket_price >= 0.55:
            pm_bonus = 5   # Moderate alignment
        elif polymarket_price <= 0.35:
            pm_bonus = -10 # Market disagrees
    
    # Calculate final confidence (cap at 95%)
    final = min(95, base + tier_bonus.get(otterline_tier.lower(), 0) + pm_bonus)
    final = max(5, final)  # Floor at 5%
    
    return round(final)


def generate_enhanced_twitter_thread(picks):
    """
    Generate Twitter thread with enhanced data from all 3 sources
    """
    if not picks:
        return None
    
    date = datetime.now().strftime("%m/%d")
    
    # Tweet 1: Header
    tweets = []
    tweets.append(f"🧠 BETBRAIN AI PICKS ({date}) — Enhanced Edition\n")
    tweets.append("Combining 3 data sources:\n• BetMonster Monte Carlo\n• Otterline AI Consensus\n• Polymarket Real-Money Odds\n")
    
    # Tweet 2-4: Top Picks (3 picks max per tweet for readability)
    top_picks = sorted(picks, key=lambda x: x.get('enhanced_confidence', 0), reverse=True)[:5]
    
    for i, pick in enumerate(top_picks, 1):
        team = pick.get('team', 'Unknown')
        matchup = pick.get('matchup', '')
        confidence = pick.get('enhanced_confidence', 50)
        edge = pick.get('edge', 0)
        
        # Confidence emoji
        if confidence >= 80:
            conf_emoji = "🔒"
        elif confidence >= 65:
            conf_emoji = "⚡"
        else:
            conf_emoji = "📊"
        
        # Data source indicators
        sources = []
        if pick.get('betmonster_data'):
            sources.append("BM")
        if pick.get('otterline_tier') and pick['otterline_tier'].lower() != 'pass':
            sources.append("Otter")
        if pick.get('polymarket_price'):
            sources.append("Poly")
        
        source_badge = f"[{'+'.join(sources)}]" if sources else ""
        
        tweet_line = f"{conf_emoji} {i}. {team} {source_badge}\n"
        tweet_line += f"   Confidence: {confidence}% | Edge: {edge:.1f}%\n"
        
        if pick.get('otterline_tier'):
            tier = pick['otterline_tier'].upper()
            if tier != "PASS":
                tweet_line += f"   Otterline: {tier}\n"
        
        if pick.get('polymarket_price'):
            pm_pct = pick['polymarket_price'] * 100
            tweet_line += f"   Polymarket: {pm_pct:.0f}%\n"
        
        tweets.append(tweet_line)
    
    # Final Tweet: Disclaimer + Hashtags
    tweets.append("📊 Data > Guessing\n")
    tweets.append("Results tracked publicly. Follow for daily AI picks.\n")
    tweets.append("#NBA #SportsBetting #BetBrain #AI")
    
    return tweets


def merge_data_sources(otterline_data, betmonster_data):
    """
    Merge picks from Otterline + BetMonster + Polymarket
    Match by team name to combine data
    """
    merged_picks = []
    
    # Process BetMonster picks (primary source)
    if betmonster_data and 'picks' in betmonster_data:
        for bm_pick in betmonster_data.get('picks', []):
            team = bm_pick.get('team', '')
            matchup = bm_pick.get('matchup', '')
            confidence = bm_pick.get('confidence', 50)
            edge = bm_pick.get('edge', 0)
            
            # Find matching Otterline pick
            otterline_match = None
            polymarket_price = None
            
            if otterline_data:
                for ol_pick in otterline_data.get('combined_picks', []):
                    ol_team = ol_pick.get('pick', '')
                    if team.lower() in ol_team.lower() or ol_team.lower() in team.lower():
                        otterline_match = ol_pick
                        polymarket_price = ol_pick.get('polymarket_price')
                        break
            
            # Calculate enhanced confidence
            otterline_tier = otterline_match.get('otterline_tier', 'strong') if otterline_match else 'strong'
            enhanced_conf = calculate_enhanced_confidence(confidence, otterline_tier, polymarket_price)
            
            merged_pick = {
                'team': team,
                'matchup': matchup,
                'betmonster_data': True,
                'betmonster_confidence': confidence,
                'betmonster_edge': edge,
                'otterline_tier': otterline_tier,
                'polymarket_price': polymarket_price,
                'enhanced_confidence': enhanced_conf,
                'edge': edge,
                'data_sources': ['betmonster']
            }
            
            if otterline_match:
                merged_pick['data_sources'].append('otterline')
            if polymarket_price:
                merged_pick['data_sources'].append('polymarket')
            
            merged_picks.append(merged_pick)
    
    # Add Otterline-only picks (if BetMonster didn't cover them)
    if otterline_data:
        for ol_pick in otterline_data.get('combined_picks', []):
            team = ol_pick.get('pick', '')
            
            # Skip if already in merged picks
            if any(team.lower() in p['team'].lower() for p in merged_picks):
                continue
            
            # Skip "pass" tier picks
            if ol_pick.get('otterline_tier', '').lower() == 'pass':
                continue
            
            polymarket_price = ol_pick.get('polymarket_price')
            otterline_tier = ol_pick.get('otterline_tier', 'strong')
            
            # Estimate confidence for Otterline-only picks
            tier_confidence = {
                'elite': 75,
                'verified': 70,
                'strong': 60,
                'lean': 55
            }
            base_conf = tier_confidence.get(otterline_tier.lower(), 55)
            enhanced_conf = calculate_enhanced_confidence(base_conf, otterline_tier, polymarket_price)
            
            merged_pick = {
                'team': team,
                'matchup': ol_pick.get('matchup', ''),
                'betmonster_data': False,
                'betmonster_confidence': None,
                'betmonster_edge': None,
                'otterline_tier': otterline_tier,
                'polymarket_price': polymarket_price,
                'enhanced_confidence': enhanced_conf,
                'edge': 0,
                'data_sources': ['otterline']
            }
            
            if polymarket_price:
                merged_pick['data_sources'].append('polymarket')
            
            merged_picks.append(merged_pick)
    
    return merged_picks


def save_twitter_thread(tweets, filename=None):
    """Save Twitter thread to file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_twitter_thread_{timestamp}.txt"
    
    output_path = TWITTER_DRAFTS_DIR / filename
    
    with open(output_path, 'w') as f:
        f.write("═══ ENHANCED TWITTER THREAD ═══\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tweets: {len(tweets)}\n")
        f.write("═══\n\n")
        
        for i, tweet in enumerate(tweets, 1):
            char_count = len(tweet)
            f.write(f"🐦 TWEET {i}/{len(tweets)} ({char_count} chars)\n")
            f.write(tweet)
            f.write("\n\n")
    
    print(f"✓ Saved Twitter thread to {output_path}")
    return output_path


def main():
    print("=" * 60)
    print("BetBrain AI — Enhanced Twitter Thread Generator")
    print("=" * 60)
    print()
    
    # Load data sources
    print("📊 Loading data sources...")
    otterline_data = load_latest_otterline_polymarket()
    betmonster_data = load_latest_betmonster()
    print()
    
    if not otterline_data and not betmonster_data:
        print("❌ No data available from any source")
        return None
    
    # Merge data
    print("🔄 Merging data sources...")
    merged_picks = merge_data_sources(otterline_data, betmonster_data)
    print(f"✓ Merged {len(merged_picks)} total picks")
    print()
    
    # Generate Twitter thread
    print("🐦 Generating enhanced Twitter thread...")
    tweets = generate_enhanced_twitter_thread(merged_picks)
    
    if tweets:
        save_twitter_thread(tweets)
        print()
        
        # Print preview
        print("=" * 60)
        print("TWITTER THREAD PREVIEW")
        print("=" * 60)
        for i, tweet in enumerate(tweets, 1):
            char_count = len(tweet)
            status = "✓" if char_count <= 280 else "⚠️ OVER LIMIT"
            print(f"\n🐦 Tweet {i}/{len(tweets)} ({char_count} chars) {status}")
            print(tweet)
    else:
        print("❌ No picks to generate thread")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"BetMonster picks: {sum(1 for p in merged_picks if p.get('betmonster_data'))}")
    print(f"Otterline picks: {sum(1 for p in merged_picks if p.get('otterline_tier'))}")
    print(f"Polymarket matches: {sum(1 for p in merged_picks if p.get('polymarket_price'))}")
    
    if merged_picks:
        confidences = [p.get('enhanced_confidence', 50) for p in merged_picks]
        print(f"Enhanced confidence range: {min(confidences)}% - {max(confidences)}%")
    
    return tweets


if __name__ == "__main__":
    main()
