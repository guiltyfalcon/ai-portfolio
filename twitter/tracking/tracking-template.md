# BetBrain AI - Public Pick Tracking Spreadsheet Template

## Overview
This template provides a comprehensive structure for tracking AI-generated sports betting picks with full transparency and performance metrics.

---

## Sheet Structure

### Sheet 1: "Picks Log" (Main Data Entry)

#### Column Headers (A-J)

| Column | Header | Data Type | Example |
|--------|--------|-----------|---------|
| A | Date | Date | 2026-03-05 |
| B | Sport | Dropdown | NBA |
| C | Game/Matchup | Text | Lakers vs Celtics |
| D | Pick (Team/Player + Prop) | Text | Lakers -5.5 |
| E | Odds | Decimal | -110 |
| F | Units Wagered | Number | 2.0 |
| G | Result | Dropdown | Win |
| H | Profit/Loss | Formula (Auto) | +1.82 |
| I | AI Confidence % | Number | 72 |
| J | Notes/Analysis | Text | Strong matchup data |

#### Data Validation Rules

**Column B - Sport (Dropdown):**
```
NBA, NFL, MLB, NHL, Soccer, Tennis, Golf, Boxing, MMA, College Basketball, College Football, Other
```

**Column G - Result (Dropdown):**
```
Win, Loss, Push
```

**Column I - AI Confidence %:**
```
Range: 50-100
Step: 1
```

---

### Sheet 2: "Dashboard" (Summary & Visualizations)

#### Key Metrics Display (Row 2-10)

| Cell | Metric | Formula Reference |
|------|--------|-------------------|
| B2 | Total Picks | `=COUNTA('Picks Log'!A:A)-1` |
| B3 | Win Rate % | See dashboard-formulas.md |
| B4 | Total Units P/L | See dashboard-formulas.md |
| B5 | ROI % | See dashboard-formulas.md |
| B6 | Average Odds | See dashboard-formulas.md |
| B7 | Current Streak | See dashboard-formulas.md |
| B8 | Best Sport by ROI | See dashboard-formulas.md |
| B9 | Best Prop Type by ROI | See dashboard-formulas.md |
| B10 | Last Updated | `=NOW()` |

#### Chart Placement

- **Win/Loss Chart:** Cells D2:F15 (Column chart showing W/L by sport)
- **ROI Trend Line:** Cells D18:F30 (Line chart showing ROI over time)
- **Monthly Breakdown:** Cells H2:J15 (Bar chart by month)

---

### Sheet 3: "Monthly Summary" (Optional Detailed Breakdown)

| Column | Header | Formula |
|--------|--------|---------|
| A | Month | `=TEXT('Picks Log'!A:A,"YYYY-MM")` |
| B | Picks | `=COUNTIF(...)` |
| C | Wins | `=COUNTIFS(...)` |
| D | Losses | `=COUNTIFS(...)` |
| E | Win Rate | `=C/B` |
| F | Units P/L | `=SUMIFS(...)` |
| G | ROI | `=F/(B*avg_units)` |

---

## Formatting Guidelines

### Conditional Formatting

**Profit/Loss Column (H):**
- Green fill: Value > 0
- Red fill: Value < 0
- Yellow fill: Value = 0 (Push)

**AI Confidence Column (I):**
- Green: >= 70%
- Yellow: 60-69%
- Red: < 60%

**Result Column (G):**
- Green background: Win
- Red background: Loss
- Gray background: Push

### Number Formatting

- **Odds:** Custom format `[>=0]+0.00; -0.00`
- **Units:** 1 decimal place
- **Profit/Loss:** Currency with +/− prefix
- **ROI/Win Rate:** Percentage with 1 decimal
- **Confidence:** Percentage with 0 decimals

---

## Protected Ranges

**Protect the following ranges to prevent accidental edits:**

1. **Column H (Profit/Loss):** Entire column - formula auto-calculates
2. **Dashboard Sheet:** All cells except input parameters
3. **Monthly Summary Sheet:** Formula columns

---

## Named Ranges (Optional but Recommended)

| Name | Refers To | Purpose |
|------|-----------|---------|
| `PickDates` | `'Picks Log'!$A:$A` | Date range for charts |
| `PickSports` | `'Picks Log'!$B:$B` | Sport filtering |
| `PickResults` | `'Picks Log'!$G:$G` | Result analysis |
| `PickOdds` | `'Picks Log'!$E:$E` | Odds calculations |
| `PickUnits` | `'Picks Log'!$F:$F` | Unit tracking |
| `PickPL` | `'Picks Log'!$H:$H` | P/L analysis |
| `PickConfidence` | `'Picks Log'!$I:$I` | Confidence metrics |

---

## Data Entry Workflow

1. **Enter new pick** in next available row
2. **Select sport** from dropdown (Column B)
3. **Enter game details** (Column C)
4. **Enter pick details** (Column D)
5. **Enter odds** in American format (Column E)
6. **Enter units** (Column F)
7. **Enter AI confidence** (Column I)
8. **Add notes** (Column J)
9. **Update Result** (Column G) after game completes
10. **Profit/Loss auto-calculates** (Column H)

---

## File Naming Convention

```
BetBrain-Pick-Tracker-YYYY-MM.xlsx
BetBrain-Pick-Tracker-LIVE.xlsx (for active tracking)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-05 | Initial template creation |

---

## Next Steps

1. Review `dashboard-formulas.md` for all calculation formulas
2. Review `sharing-instructions.md` for publishing guidelines
3. Review `sample-picks.md` for example populated data
4. Create Google Sheet and apply template structure
5. Set up charts and visualizations
6. Configure sharing settings
7. Generate public URL and embed code
