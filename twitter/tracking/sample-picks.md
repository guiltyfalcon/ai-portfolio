# BetBrain AI - Sample Pick Data

## Overview
This file contains 10 sample picks demonstrating how the tracking spreadsheet should look when populated. Use this as a reference for data entry format and to test your formulas.

---

## Sample Data (10 Picks)

| Row | Date | Sport | Game/Matchup | Pick (Team/Player + Prop) | Odds | Units | Result | P/L | Confidence | Notes |
|-----|------|-------|--------------|---------------------------|------|-------|--------|-----|------------|-------|
| 2 | 2026-03-01 | NBA | Lakers vs Celtics | Lakers -5.5 | -110 | 2.0 | Win | +1.82 | 72 | Strong home court data |
| 3 | 2026-03-01 | NFL | Chiefs vs Bills | Over 52.5 | -105 | 1.5 | Loss | -1.50 | 65 | Weather factor ignored |
| 4 | 2026-03-02 | NBA | Warriors vs Suns | Curry Over 28.5 pts | -115 | 2.5 | Win | +2.17 | 78 | Hot streak continues |
| 5 | 2026-03-02 | MLB | Yankees vs Red Sox | Yankees ML | -140 | 3.0 | Win | +2.14 | 68 | Pitching matchup edge |
| 6 | 2026-03-03 | NHL | Bruins vs Rangers | Under 6.5 | -110 | 1.5 | Win | +1.36 | 71 | Both goalies hot |
| 7 | 2026-03-03 | NBA | Nuggets vs Heat | Jokic Over 11.5 reb | -120 | 2.0 | Loss | -2.00 | 69 | Rest day concern |
| 8 | 2026-03-04 | NFL | 49ers vs Cowboys | 49ers -3.5 | -108 | 2.5 | Push | 0.00 | 74 | Line moved to -3 |
| 9 | 2026-03-04 | Soccer | Man City vs Arsenal | Man City ML | +125 | 1.5 | Win | +1.88 | 66 | Value play |
| 10 | 2026-03-05 | NBA | Bucks vs 76ers | Giannis Over 31.5 pts | -112 | 2.0 | Win | +1.79 | 81 | Elite matchup |
| 11 | 2026-03-05 | MLB | Dodgers vs Padres | Under 8.5 | -105 | 2.0 | Loss | -2.00 | 63 | Bullpen fatigue |

---

## Calculated Metrics (From Sample Data)

### Dashboard Summary

| Metric | Value | Formula Used |
|--------|-------|--------------|
| **Total Picks** | 10 | `=COUNTA(A:A)-1` |
| **Wins** | 6 | `=COUNTIF(G:G,"Win")` |
| **Losses** | 3 | `=COUNTIF(G:G,"Loss")` |
| **Pushes** | 1 | `=COUNTIF(G:G,"Push")` |
| **Win Rate %** | 66.7% | `=6/(6+3)` |
| **Total Units Wagered** | 20.5 | `=SUM(F:F)` |
| **Total P/L** | +5.66 | `=SUM(H:H)` |
| **ROI %** | +27.6% | `=5.66/20.5` |
| **Average Odds** | -108 | `=AVERAGE(E:E)` |
| **Average Confidence** | 70.7% | `=AVERAGE(I:I)` |
| **Current Streak** | +2 | Last 2 results: Win-Win |

---

## Breakdown by Sport

| Sport | Picks | Wins | Losses | Pushes | Win Rate | Units | P/L | ROI |
|-------|-------|------|--------|--------|----------|-------|-----|-----|
| **NBA** | 5 | 4 | 1 | 0 | 80.0% | 10.5 | +3.78 | +36.0% |
| **NFL** | 2 | 0 | 1 | 1 | 0.0% | 4.0 | -1.50 | -37.5% |
| **MLB** | 2 | 1 | 1 | 0 | 50.0% | 5.0 | +0.14 | +2.8% |
| **NHL** | 1 | 1 | 0 | 0 | 100.0% | 1.5 | +1.36 | +90.7% |
| **Soccer** | 1 | 1 | 0 | 0 | 100.0% | 1.5 | +1.88 | +125.3% |

**Best Sport by ROI:** Soccer (+125.3%)
**Best Sport by Volume:** NBA (5 picks, +36.0% ROI)

---

## Breakdown by Prop Type

| Prop Type | Picks | Wins | Losses | Win Rate | P/L | ROI |
|-----------|-------|------|--------|----------|-----|-----|
| **Spread** | 3 | 1 | 1 | 50.0% | +1.82 | +25.3% |
| **Moneyline** | 2 | 2 | 0 | 100.0% | +4.02 | +89.3% |
| **Player Props** | 3 | 2 | 1 | 66.7% | +1.96 | +28.4% |
| **Totals (Over/Under)** | 2 | 1 | 1 | 50.0% | -0.64 | -15.4% |

**Best Prop Type by ROI:** Moneyline (+89.3%)

---

## Monthly Breakdown

| Month | Picks | Wins | Losses | Win Rate | P/L | ROI |
|-------|-------|------|--------|----------|-----|-----|
| **2026-03** | 10 | 6 | 3 | 66.7% | +5.66 | +27.6% |

*All sample picks are from March 2026*

---

## Streak Analysis

| Streak Type | Count | Dates |
|-------------|-------|-------|
| **Current Streak** | +2 (Win) | 2026-03-05 (2 picks) |
| **Longest Win Streak** | 3 | 2026-03-01 to 2026-03-03 |
| **Longest Loss Streak** | 1 | Multiple single losses |
| **Best Month** | March 2026 | +5.66 units |

---

## Confidence vs Performance

| Confidence Range | Picks | Wins | Win Rate | P/L | ROI |
|------------------|-------|------|----------|-----|-----|
| **80-100%** | 1 | 1 | 100.0% | +1.79 | +89.5% |
| **70-79%** | 5 | 4 | 80.0% | +5.35 | +51.4% |
| **60-69%** | 4 | 1 | 25.0% | -1.48 | -18.7% |
| **50-59%** | 0 | 0 | N/A | 0.00 | N/A |

**Insight:** Higher confidence picks (70%+) show significantly better performance (+51.4% ROI vs -18.7% ROI)

---

## Profit/Loss Calculation Examples

### Pick #2 (Lakers -5.5, -110, 2 units, Win)
```
P/L = 2.0 × (100/110) = 2.0 × 0.909 = +1.82
```

### Pick #3 (Over 52.5, -105, 1.5 units, Loss)
```
P/L = -1.50 (loss of full stake)
```

### Pick #4 (Curry Over 28.5, -115, 2.5 units, Win)
```
P/L = 2.5 × (100/115) = 2.5 × 0.870 = +2.17
```

### Pick #8 (49ers -3.5, -108, 2.5 units, Push)
```
P/L = 0.00 (stake returned)
```

### Pick #9 (Man City ML, +125, 1.5 units, Win)
```
P/L = 1.5 × (125/100) = 1.5 × 1.25 = +1.88
```

---

## Data Entry Tips

### Odds Format
- **Negative odds (favorites):** -110, -115, -140
- **Positive odds (underdogs):** +125, +150, +200
- **Enter as numbers only** (no quotes or special characters)

### Units Standardization
- **Standard unit:** 1.0 = 1% of bankroll
- **Range:** 0.5 to 5.0 units typical
- **Be consistent** with your unit sizing

### Result Entry
- Enter **immediately after game completes**
- Double-check score before marking Win/Loss
- Mark **Push** when applicable (spread lands exactly on number)

### Notes Best Practices
- Keep notes **concise but informative**
- Include **key factors** (injuries, weather, line movement)
- Note **AI reasoning** for future analysis
- Flag **unusual outcomes** for review

---

## Formula Testing Checklist

Use this sample data to verify your formulas:

- [ ] Total Picks = 10
- [ ] Win Rate = 66.7% (or 60% if excluding pushes)
- [ ] Total P/L = +5.66
- [ ] ROI = 27.6%
- [ ] Current Streak = +2
- [ ] Best Sport ROI = Soccer (125.3%)
- [ ] NBA P/L = +3.78
- [ ] Average Confidence = 70.7%
- [ ] High Confidence (70%+) ROI = 51.4%
- [ ] Low Confidence (<70%) ROI = -18.7%

---

## Visual Chart Data

### Win/Loss by Sport (for Column Chart)
```
Sport       | Wins | Losses
NBA         |   4  |   1
NFL         |   0  |   1
MLB         |   1  |   1
NHL         |   1  |   0
Soccer      |   1  |   0
```

### ROI Trend (Cumulative)
```
Pick # | Cumulative P/L | Cumulative Units | ROI
   1   |     +1.82      |       2.0        | 91.0%
   2   |     +0.32      |       3.5        |  9.1%
   3   |     +2.49      |       6.0        | 41.5%
   4   |     +4.63      |       9.0        | 51.4%
   5   |     +2.63      |      11.0        | 23.9%
   6   |     +2.63      |      13.5        | 19.5%
   7   |     +4.51      |      15.0        | 30.1%
   8   |     +6.30      |      17.0        | 37.1%
   9   |     +4.30      |      19.0        | 22.6%
  10   |     +5.66      |      20.5        | 27.6%
```

### Monthly P/L
```
Month    | P/L
2026-03  | +5.66
```

---

## Copy/Paste Ready Data

### CSV Format (for import)
```csv
Date,Sport,Game/Matchup,Pick,Odds,Units,Result,P/L,Confidence,Notes
2026-03-01,NBA,Lakers vs Celtics,Lakers -5.5,-110,2.0,Win,1.82,72,Strong home court data
2026-03-01,NFL,Chiefs vs Bills,Over 52.5,-105,1.5,Loss,-1.50,65,Weather factor ignored
2026-03-02,NBA,Warriors vs Suns,Curry Over 28.5 pts,-115,2.5,Win,2.17,78,Hot streak continues
2026-03-02,MLB,Yankees vs Red Sox,Yankees ML,-140,3.0,Win,2.14,68,Pitching matchup edge
2026-03-03,NHL,Bruins vs Rangers,Under 6.5,-110,1.5,Win,1.36,71,Both goalies hot
2026-03-03,NBA,Nuggets vs Heat,Jokic Over 11.5 reb,-120,2.0,Loss,-2.00,69,Rest day concern
2026-03-04,NFL,49ers vs Cowboys,49ers -3.5,-108,2.5,Push,0.00,74,Line moved to -3
2026-03-04,Soccer,Man City vs Arsenal,Man City ML,+125,1.5,Win,1.88,66,Value play
2026-03-05,NBA,Bucks vs 76ers,Giannis Over 31.5 pts,-112,2.0,Win,1.79,81,Elite matchup
2026-03-05,MLB,Dodgers vs Padres,Under 8.5,-105,2.0,Loss,-2.00,63,Bullpen fatigue
```

---

## Next Steps

1. **Import this sample data** into your spreadsheet to test formulas
2. **Verify all calculations** match the metrics above
3. **Create charts** using the visual chart data
4. **Delete sample data** when ready to go live (or keep for reference)
5. **Begin entering real picks** using the same format

---

## Performance Insights from Sample

### Key Takeaways

1. **NBA is the strongest sport** - 80% win rate, +36% ROI
2. **High confidence pays off** - 70%+ confidence shows 51.4% ROI
3. **Moneyline bets profitable** - 2-0 record, +89% ROI
4. **Totals struggling** - Only 50% win rate, negative ROI
5. **Current momentum positive** - 2-game win streak

### Areas for Improvement

1. **NFL picks need review** - 0-1-1 record, -37.5% ROI
2. **Low confidence picks** - Consider skipping <60% confidence
3. **Totals betting** - May need model adjustment for over/under

---

*Sample Data Created: 2026-03-05*
*For Testing & Demonstration Purposes*
