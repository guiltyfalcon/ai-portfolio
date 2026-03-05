#!/usr/bin/env python3
"""
Auto-Tweet Daily Picks - Posts AI's top bets to Twitter/X
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Try to import tweepy, handle if not installed
try:
    import tweepy
    TWEETY_INSTALLED = True
except ImportError:
    TWEETY_INSTALLED = False

CACHE_FILE = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/player_props_cache.json')
HIT_THRESHOLD = 60.0  # Only tweet props with 60%+ hit probability

def load_cache():
    """Load player props cache."""
    if not CACHE_FILE.exists():
        print(f"❌ Cache file not found: {CACHE_FILE}")
        return None
    
    with open(CACHE_FILE, 'r') as f:
        return json.load(f)

def find_top_picks(cache_data, limit=3):
    """Find top picks for tweeting."""
    picks = []
    
    sports = cache_data.get('sports', {})
    nba_players = sports.get('nba', [])
    
    for game in nba_players:
        game_info = f"{game.get('away_team', 'Unknown')} @ {game.get('home_team', 'Unknown')}"
        
        for player in game.get('players', []):
            player_name = player.get('player', 'Unknown')
            team = player.get('team_abbr', '')
            
            for prop in player.get('props', []):
                hit_prob = prop.get('hit_probability', 0)
                weighted_prob = prop.get('weighted_probability', hit_prob)
                recommendation = prop.get('recommendation', 'EVEN')
                prop_type = prop.get('type', 'unknown').upper()
                line = prop.get('line', 0)
                odds_over = prop.get('odds_over', '-110')
                
                # Score this pick
                score = weighted_prob
                if recommendation == 'LEAN':
                    score += 10
                
                if weighted_prob >= HIT_THRESHOLD:
                    picks.append({
                        'player': player_name,
                        'team': team,
                        'prop': f"{prop_type} O{line}",
                        'hit_prob': weighted_prob,
                        'odds': odds_over,
                        'game': game_info,
                        'score': score
                    })
    
    # Sort by score and return top picks
    picks.sort(key=lambda x: x['score'], reverse=True)
    return picks[:limit]

def format_tweet(picks):
    """Format picks as tweet."""
    if not picks:
        return None
    
    today = datetime.now().strftime('%m/%d')
    
    tweet = f"🧠 BetBrain AI Daily Picks - {today}\n\n"
    
    for i, pick in enumerate(picks, 1):
        emoji = "🔥" if pick['hit_prob'] >= 65 else "⚡"
        tweet += f"{emoji} #{i}: {pick['player']} ({pick['team']})\n"
        tweet += f"   {pick['prop']} ({pick['odds']})\n"
        tweet += f"   AI Confidence: {pick['hit_prob']:.0f}%\n\n"
    
    tweet += "📊 Data-driven picks from @holikidTV\n"
    tweet += "⚠️ For entertainment only. Bet responsibly.\n\n"
    tweet += "#SportsBetting #NBA #BettingTips #AI"
    
    return tweet

def post_to_twitter(tweet):
    """Post tweet using Twitter API v2."""
    if not TWEETY_INSTALLED:
        print("⚠️  tweepy not installed. Printing tweet instead:")
        print("\n" + "=" * 60)
        print(tweet)
        print("=" * 60 + "\n")
        return False
    
    # Check for API credentials
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("⚠️  Twitter API credentials not set. Printing tweet instead:")
        print("\n" + "=" * 60)
        print(tweet)
        print("=" * 60 + "\n")
        return False
    
    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        response = client.create_tweet(text=tweet)
        tweet_id = response.data['id']
        print(f"✅ Tweet posted: https://twitter.com/holikidTV/status/{tweet_id}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to post tweet: {e}")
        return False

def main():
    print(f"🧠 BetBrain AI Auto-Tweet - {datetime.now()}")
    print(f"   Cache: {CACHE_FILE}\n")
    
    # Load cache
    cache_data = load_cache()
    if not cache_data:
        return
    
    # Find top picks
    picks = find_top_picks(cache_data)
    print(f"📊 Found {len(picks)} top picks")
    
    if not picks:
        print("✅ No high-confidence picks found. Standing by.")
        return
    
    # Format tweet
    tweet = format_tweet(picks)
    if not tweet:
        return
    
    print(f"📝 Tweet length: {len(tweet)} chars\n")
    
    # Post to Twitter
    posted = post_to_twitter(tweet)
    
    if posted:
        print("✅ Auto-tweet complete")
    else:
        print("ℹ️  Tweet not posted (missing credentials or tweepy)")

if __name__ == '__main__':
    main()
