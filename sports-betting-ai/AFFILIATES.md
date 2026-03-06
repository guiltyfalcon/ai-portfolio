# BetBrain AI - Affiliate Links & Integration

## Current Affiliate Programs

### ✅ Active

| Program | Status | Link | Commission |
|---------|--------|------|------------|
| **OddsJam** | ⏳ Pending Application | [Apply Here](https://oddsjam.com/affiliate) | 50% lifetime recurring |
| **Fanatics Sportsbook** | ⏳ Pending Application | [Apply Here](https://www.fanaticsaffiliates.com/) | $100-400 CPA |

### 📋 To Apply (Week 2)

| Program | Requirements | Link |
|---------|--------------|------|
| **DraftKings** | 500+ followers | [draftkings.com/affiliates](https://www.draftkings.com/affiliates) |
| **BetMGM** | 500+ followers | [betmgmpartners.com](https://betmgmpartners.com/) |
| **Caesars** | 300+ followers | [caesarsaffiliates.com](https://www.caesarsaffiliates.com/) |
| **PointsBet** | 200+ followers | [pointsbet.com/affiliates](https://pointsbet.com/affiliates) |

---

## Integration Points

### 1. Landing Page

**Waitlist Confirmation Page** (after email signup):
```html
<div class="mt-8 p-6 bg-darker rounded-xl border border-gray-800">
  <h3 class="text-xl font-bold mb-4">🎁 Get a Head Start</h3>
  <p class="text-gray-400 mb-4">Sign up with our partner sportsbooks for exclusive bonuses:</p>
  
  <div class="space-y-4">
    <a href="[ODDSJAM_LINK]" class="block p-4 bg-primary/10 rounded-lg hover:bg-primary/20 transition">
      <div class="flex justify-between items-center">
        <div>
          <h4 class="font-bold">OddsJam</h4>
          <p class="text-sm text-gray-400">Find +EV bets & arbitrage opportunities</p>
        </div>
        <span class="text-primary font-bold">Sign Up →</span>
      </div>
    </a>
    
    <a href="[FANATICS_LINK]" class="block p-4 bg-primary/10 rounded-lg hover:bg-primary/20 transition">
      <div class="flex justify-between items-center">
        <div>
          <h4 class="font-bold">Fanatics Sportsbook</h4>
          <p class="text-sm text-gray-400">Bet $50, Get $200 in Bonus Bets</p>
        </div>
        <span class="text-primary font-bold">Claim Bonus →</span>
      </div>
    </a>
  </div>
</div>
```

### 2. Telegram Channel

**Pinned Message**:
```
🧠 Welcome to BetBrain AI!

📊 Daily NBA picks (65-75% accuracy)
🔔 Live odds updates every 30 min
💰 Best lines from 5+ sportsbooks

🎁 SIGN-UP BONUSES:
• Fanatics: Bet $50, Get $200 → [LINK]
• DraftKings: Deposit $5, Get $200 → [LINK]
• OddsJam: Find +EV bets → [LINK]

📈 Track Record: [landing-page-url]/track-record.html
🐦 Twitter: @holikidTV

21+ | Gamble responsibly
```

**After Each Picks Post**:
```
[Pick analysis...]

🎯 Want more picks like this?
Join our premium tier (coming soon) → [LINK]

📊 Compare lines across 5 sportsbooks:
• Fanatics: [AFFILIATE_LINK]
• DraftKings: [AFFILIATE_LINK]
```

### 3. Twitter Posts

**Bio Link**: Use Linktree or similar with all affiliate links

**Periodic Posts** (2-3x/week):
```
🔥 Best Sportsbook Bonuses Right Now:

1. Fanatics: Bet $50 → Get $200 [LINK]
2. DraftKings: Deposit $5 → Get $200 [LINK]
3. BetMGM: First bet up to $150 [LINK]

Use code BETBRAIN for exclusive offers!

#sportsbetting #NBA #affiliate
```

---

## Tracking Setup

### Bit.ly Links (Free Tier)

Create trackable links for each affiliate:
```
bit.ly/betbrain-fanatics
bit.ly/betbrain-draftkings
bit.ly/betbrain-oddsjam
```

Track clicks in Bit.ly dashboard.

### UTM Parameters

Add UTM tags to all links:
```
https://fanatics.com/?utm_source=twitter&utm_medium=social&utm_campaign=betbrain&utm_content=picks-post
```

### Google Analytics

Add to landing page:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## Compliance

### Required Disclosures

**FTC Guidelines**:
- Clearly disclose affiliate relationships
- Use #ad or #affiliate on social posts
- Add disclosure to landing page footer

**Example Footer**:
```html
<p class="text-gray-500 text-sm">
  ⚠️ Affiliate Disclosure: We may earn commissions from sportsbook sign-ups. 
  This doesn't affect our recommendations. 21+ only. Gamble responsibly.
</p>
```

**State Restrictions**:
Only target legal states:
- AZ, CO, CT, DC, IA, IL, IN, KS, KY, LA, MA, MD, MI, NC, NJ, NY, OH, PA, TN, VA, WV, WY

---

## Revenue Projections

### Month 1-2 (Building)
- 1,000 Twitter followers
- 500 Telegram members
- 100 email subscribers
- **Affiliate Revenue**: $200-500/mo (5-10 signups @ $50 avg CPA)

### Month 3-4 (Traction)
- 5,000 Twitter followers
- 2,000 Telegram members
- 500 email subscribers
- **Affiliate Revenue**: $1,000-3,000/mo (20-60 signups)

### Month 5-6 (Scale)
- 25,000 Twitter followers
- 10,000 Telegram members
- 2,000 email subscribers
- **Affiliate Revenue**: $5,000-10,000/mo (100-200 signups)

### Premium Tier (Month 3+)
- 50 premium users @ $30/mo = $1,500/mo
- 200 premium users @ $30/mo = $6,000/mo
- 500 premium users @ $30/mo = $15,000/mo

---

## Next Steps

### Week 1 (Now)
- [ ] Apply to OddsJam (easiest approval)
- [ ] Apply to Fanatics Sportsbook
- [ ] Set up Bit.ly tracking links
- [ ] Add Google Analytics to landing page

### Week 2
- [ ] Add affiliate section to landing page
- [ ] Update Telegram pinned message
- [ ] Create Twitter affiliate post template
- [ ] Apply to DraftKings + BetMGM

### Week 3-4
- [ ] Track clicks/conversions
- [ ] A/B test different CTAs
- [ ] Optimize based on performance
- [ ] Launch premium tier

---

**Action Items:**
1. Create accounts at OddsJam + Fanatics affiliates
2. Get affiliate links
3. Send links to me for integration
4. I'll add to all platforms
