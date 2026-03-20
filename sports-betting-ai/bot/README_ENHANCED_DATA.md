# BetBrain Enhanced Data Pipeline

**Created:** 2026-03-20  
**Skills Installed:** Otterline, Polymarket Odds, Argus Edge

---

## Overview

Three new scripts that enhance BetBrain AI picks with external data sources:

| Script | Purpose | Output |
|--------|---------|--------|
| **otterline_polymarket_fetcher.py** | Fetch Otterline AI picks + Polymarket odds | `~/.openclaw/data/betbrain-external-data/` |
| **enhanced_twitter_generator.py** | Combine all 3 sources for Twitter threads | `~/.openclaw/data/twitter-drafts/` |
| **argus_edge_detector.py** | Kelly criterion + edge detection | `~/.openclaw/data/twitter-drafts/` |

---

## Data Sources

### 1. BetMonster (Existing)
- Monte Carlo simulation (10k runs)
- 95% confidence intervals
- Edge calculation vs market odds

### 2. Otterline (NEW)
- AI consensus model (Chorus Engine)
- Confidence tiers: Elite, Verified, Strong, Lean, Pass
- Free sample API (1-3 picks/day)
- **Website:** otterline.club

### 3. Polymarket (NEW)
- Real-money prediction markets
- Prices = implied probabilities
- No API key required
- **Coverage:** NBA, NFL, soccer, politics, crypto

### 4. Argus Edge Framework (NEW)
- Edge detection formula
- Kelly criterion sizing
- Consensus + freshness checks
- **Threshold:** ≥10% edge for BET, ≥5% for LEAN

---

## Morning Automation Schedule

| Time | Script | Purpose |
|------|--------|---------|
| **8:30 AM ET** | `otterline_polymarket_fetcher.py` | Fetch external data |
| **8:45 AM ET** | `enhanced_twitter_generator.py` | Generate combined Twitter thread |
| **8:50 AM ET** | `argus_edge_detector.py` | Kelly criterion analysis |
| **9:00 AM ET** | Post to Twitter | Manual review + post |

---

## Enhanced Confidence Calculation

```python
enhanced_confidence = base_confidence + tier_bonus + pm_alignment

# Tier bonuses
elite: +15%
verified: +10%
strong: +5%
lean: 0%
pass: -10%

# Polymarket alignment
≥65%: +10%
55-64%: +5%
≤35%: -10%
```

**Cap:** 95% maximum confidence

---

## Kelly Criterion Sizing

```python
# Quarter-Kelly (conservative)
kelly_stake = (edge × bankroll) / (odds - 1) × 0.25

# Constraints
max_stake = 5% of bankroll
min_stake = 1% of bankroll
```

**Default bankroll:** $10,000

---

## Output Files

### Otterline + Polymarket
```
~/.openclaw/data/betbrain-external-data/
└── otterline_polymarket_20260320_053004.json
```

### Enhanced Twitter Thread
```
~/.openclaw/data/twitter-drafts/
└── enhanced_twitter_thread_20260320_053506.txt
```

### Argus Edge Thread
```
~/.openclaw/data/twitter-drafts/
└── argus_edge_thread_20260320_053821.txt
```

---

## Twitter Thread Format

### Enhanced Thread (3 sources)
```
🧠 BETBRAIN AI PICKS (03/20) — Enhanced Edition

Combining 3 data sources:
• BetMonster Monte Carlo
• Otterline AI Consensus
• Polymarket Real-Money Odds

🔒 1. Boston Celtics [BM+Otter]
   Confidence: 80% | Edge: 9.1%
   Otterline: STRONG

📊 Data > Guessing
#NBA #SportsBetting #BetBrain #AI
```

### Argus Edge Thread
```
🎯 ARGUS EDGE DETECTOR (03/20)

📊 3 picks analyzed
🔒 1 STRONG BETS
⚡ 1 total bets
💰 Total stake: 3.4% of bankroll

🔒 1. Los Angeles Lakers
   Edge: 12.5% | Kelly: 3.4% ($344)

🧠 Argus Edge Framework:
• Edge ≥10% threshold
• Kelly criterion sizing
• Freshness + consensus checks
```

---

## Manual Testing

```bash
cd /Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/bot

# Fetch Otterline + Polymarket
python3 otterline_polymarket_fetcher.py

# Generate enhanced Twitter thread
python3 enhanced_twitter_generator.py

# Run Argus Edge Detector
python3 argus_edge_detector.py
```

---

## Data Source Badges

| Badge | Meaning |
|-------|---------|
| `[BM]` | BetMonster Monte Carlo |
| `[Otter]` | Otterline AI Consensus |
| `[Poly]` | Polymarket Real-Money Odds |
| `[BM+Otter]` | Combined BetMonster + Otterline |
| `[BM+Otter+Poly]` | All 3 sources aligned |

---

## Confidence Indicators

| Emoji | Confidence | Meaning |
|-------|------------|---------|
| 🔒 | ≥80% | Lock (high confidence) |
| ⚡ | 65-79% | Strong play |
| 📊 | <65% | Standard play |

---

## Argus Edge Recommendations

| Recommendation | Edge | Kelly Stake |
|----------------|------|-------------|
| **STRONG BET** | ≥10% | ≥3% bankroll |
| **BET** | ≥10% | <3% bankroll |
| **LEAN** | 5-9.9% | — |
| **NO BET** | <5% | — |

---

## Limitations

1. **Otterline Free Sample** — Only 1-3 picks/day (premium has full slate)
2. **Polymarket Coverage** — Not all NBA games have markets
3. **Argus Threshold** — 10% edge is rare; most picks will be LEANs
4. **No Auto-Posting** — Drafts require manual review before posting

---

## Upgrade Path

1. **Otterline Premium** (~$50/mo) — Full daily pick slates
2. **Polymarket API** — Direct access (no CLI dependency)
3. **Twitter API** — Automated posting from drafts
4. **Custom Bankroll** — Adjust Kelly sizing per risk tolerance

---

*All scripts are committed to `sports-betting-ai/bot/` and scheduled in `HEARTBEAT.md`*
