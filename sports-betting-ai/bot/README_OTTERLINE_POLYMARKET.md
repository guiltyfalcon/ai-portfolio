# Otterline + Polymarket Fetcher

**Purpose:** Combines Otterline AI consensus picks with Polymarket real-money prediction market odds for enhanced BetBrain analysis.

---

## What It Does

1. **Fetches Otterline Picks** — NBA & NHL AI consensus picks with confidence tiers
2. **Searches Polymarket** — Real-money probabilities for referenced teams
3. **Calculates Combined Confidence** — Merges Otterline tier + Polymarket alignment
4. **Generates Twitter Thread** — Ready-to-post draft with enhanced data

---

## Usage

### Manual Run
```bash
cd /Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/bot
python3 otterline_polymarket_fetcher.py
```

### Output Files
- **Location:** `/Users/djryan/.openclaw/data/betbrain-external-data/`
- **Format:** `otterline_polymarket_YYYYMMDD_HHMMSS.json`

---

## Data Sources

| Source | Type | API Key Required |
|--------|------|------------------|
| **Otterline** | AI consensus picks | ❌ No |
| **Polymarket** | Real-money odds | ❌ No |

### Otterline Tiers
| Tier | Display | Base Confidence |
|------|---------|-----------------|
| `elite` | 🔥 Elite | 0.90 |
| `verified` | ✅ Verified | 0.75 |
| `strong` | 💪 Strong | 0.60 |
| `lean` | 📊 Lean (NHL) | 0.50 |
| `pass` | ⛔ Pass (NBA) | 0.30 |

### Polymarket Adjustment
- Price ≥ 65% → +10% confidence
- Price ≤ 35% → -10% confidence

---

## Output Structure

```json
{
  "fetched_at": "2026-03-20T05:30:04",
  "otterline": {
    "nba": { ... },
    "nhl": { ... }
  },
  "polymarket": { ... },
  "combined_picks": [
    {
      "league": "NBA",
      "matchup": "Knicks @ Nets",
      "pick": "New York Knicks",
      "otterline_tier": "elite",
      "combined_confidence": 0.95,
      "polymarket_match": true,
      "polymarket_price": 0.72
    }
  ],
  "twitter_thread": "🧠 BETBRAIN AI PICKS..."
}
```

---

## Cron Integration

Add to HEARTBEAT.md for automated runs:

```markdown
### 🧠 Otterline + Polymarket Fetch (8:30 AM ET)
- Run: `python3 bot/otterline_polymarket_fetcher.py`
- Output: `~/.openclaw/data/betbrain-external-data/`
- Use: Enhanced picks for Twitter thread
```

---

## Limitations

- **Free Sample Only** — Otterline returns 1-3 picks (premium has full slate)
- **Polymarket CLI** — Requires Node.js, may timeout on slow networks
- **No Auto-Posting** — Generates draft, manual review required

---

## Upgrade Path

1. **Otterline Premium** — Full daily pick slates (~$50/mo)
2. **Polymarket API** — Direct API access (no CLI needed)
3. **Auto-Tweet** — Integrate with Twitter API for automated posting

---

*Created: 2026-03-20 | Version: 1.0*
