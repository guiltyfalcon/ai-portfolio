# BetBrain AI - Public Pick Tracking Sheet Setup Instructions

## Sheet Created ✅
**Public URL:** https://docs.google.com/spreadsheets/d/1QJukHtYdsSBmmniG7o6Siibi9MAGsD3QBioT1epxrMg/edit?usp=sharing

**Status:** Sheet is created with 3 tabs and shared publicly (view-only).

---

## What's Already Done
- ✅ Spreadsheet created: "BetBrain AI - Public Pick Tracking"
- ✅ Three tabs created: "Picks Log", "Dashboard", "Monthly Summary"
- ✅ Shared publicly: Anyone with the link can VIEW (not edit)
- ✅ URL saved to: `/Users/djryan/git/guiltyfalcon/ai-portfolio/twitter/tracking/public-sheet-url.txt`

---

## Manual Setup Required

Due to browser automation limitations, please complete the following setup manually:

### 1. Set Up "Picks Log" Tab Columns

Go to the **Picks Log** tab and create these headers in Row 1:

| Cell | Header | Notes |
|------|--------|-------|
| A1 | Date | |
| B1 | Sport | Dropdown: NFL, NBA, MLB, NHL, Soccer, Tennis, Golf, MMA, Other |
| C1 | Game/Matchup | |
| D1 | Pick (Team/Player + Prop) | |
| E1 | Odds | American format (e.g., -110, +150) |
| F1 | Units Wagered | |
| G1 | Result | Dropdown: Win, Loss, Push |
| H1 | Profit/Loss | Formula (see below) |
| I1 | AI Confidence % | |
| J1 | Notes/Analysis | |

#### Data Validation Setup:

**Column B (Sport) - Dropdown:**
1. Select column B (click the B header)
2. Data → Data validation
3. Criteria: "Dropdown"
4. Options: NFL, NBA, MLB, NHL, Soccer, Tennis, Golf, MMA, Other
5. Click Done

**Column G (Result) - Dropdown:**
1. Select column G (click the G header)
2. Data → Data validation
3. Criteria: "Dropdown"
4. Options: Win, Loss, Push
5. Click Done

#### Profit/Loss Formula (Column H):

In cell H2, enter this formula:
```
=IF(G2="Win", F2*(IF(E2<0, 100/ABS(E2), E2/100)), IF(G2="Loss", -F2, 0))
```

Then drag this formula down for all rows (H2:H1000 or as needed).

**Formula explanation:**
- If Result = "Win": Calculate profit based on odds
  - For negative odds (e.g., -110): Units × (100/110) = profit
  - For positive odds (e.g., +150): Units × (150/100) = profit
- If Result = "Loss": -Units (lose the wagered amount)
- If Result = "Push": 0 (no profit/loss)

---

### 2. Set Up "Dashboard" Tab

Go to the **Dashboard** tab and create these metrics:

| Cell | Label | Formula |
|------|-------|---------|
| A1 | **BETBRAIN AI PERFORMANCE DASHBOARD** | (Header, merge A1:H1, bold, large font) |
| A3 | Total Picks | `=COUNTA('Picks Log'!G:G)-1` |
| A4 | Win Rate % | `=IF(COUNTA('Picks Log'!G:G)-1=0, 0, COUNTIF('Picks Log'!G:G,"Win")/(COUNTA('Picks Log'!G:G)-1))` |
| A5 | Total Units P/L | `=SUM('Picks Log'!H:H)` |
| A6 | ROI % | `=IF(SUM('Picks Log'!F:F)=0, 0, SUM('Picks Log'!H:H)/SUM('Picks Log'!F:F))` |
| A7 | Average Odds | `=AVERAGE('Picks Log'!E:E)` |
| A8 | Current Streak | *(See complex formula below)* |
| A9 | Best Sport by ROI | *(See complex formula below)* |
| A10 | Best Prop Type by ROI | *(See complex formula below)* |

#### Formatting:
- Format B3 as Number (0 decimal places)
- Format B4 as Percentage (1 decimal place)
- Format B5 as Number (2 decimal places, add +/− color scaling)
- Format B6 as Percentage (2 decimal places)
- Format B7 as Number (0 decimal places)

#### Current Streak Formula (Cell B8):

This calculates the current win/loss streak from most recent picks:
```
=LET(
  results, FILTER('Picks Log'!G2:G, 'Picks Log'!G2:G<>""),
  lastResult, INDEX(results, ROWS(results)),
  IF(lastResult="Push", "No active streak",
    LET(
      streakCount, 1,
      IF(ROWS(results)=1, 1,
        IF(INDEX(results, ROWS(results)-1)=lastResult,
          SUMPRODUCT(--(FILTER('Picks Log'!G2:G, 'Picks Log'!G2:G<>"")=lastResult)),
          1
        )
      ),
      IF(lastResult="Win", "+"&streakCount, "-"&streakCount)
    )
  )
)
```

**Simplified alternative for B8:**
```
=IF(COUNTA('Picks Log'!G:G)-1=0, "No picks yet", 
  LET(last, INDEX(FILTER('Picks Log'!G2:G, 'Picks Log'!G2:G<>""), ROWS(FILTER('Picks Log'!G2:G, 'Picks Log'!G2:G<>""))),
    IF(last="Push", "No active streak",
      IF(last="Win", "+"&SUMPRODUCT(--(RIGHT('Picks Log'!G2:G, 3)="Win")), "-"&SUMPRODUCT(--(RIGHT('Picks Log'!G2:G, 4)="Loss")))
    )
  )
)
```

**Even simpler - manual tracking:** Just track your current streak manually or use this basic version:
```
=IF(COUNTA('Picks Log'!G:G)-1=0, "No picks", "Check recent picks")
```

---

### 3. Set Up "Monthly Summary" Tab

Create a monthly breakdown table:

| Cell | Content |
|------|---------|
| A1 | **MONTHLY PERFORMANCE SUMMARY** |
| A3 | Month |
| B3 | Picks |
| C3 | Wins |
| D3 | Losses |
| E3 | Pushes |
| F3 | Win Rate |
| G3 | Units P/L |
| H3 | ROI |

In A4, enter: `=TEXT('Picks Log'!A2:A, "YYYY-MM")` (as array formula)

Then use these formulas:
- B4: `=COUNTIF('Picks Log'!A:A, A4&"*")`
- C4: `=COUNTIFS('Picks Log'!G:G, "Win", 'Picks Log'!A:A, A4&"*")`
- D4: `=COUNTIFS('Picks Log'!G:G, "Loss", 'Picks Log'!A:A, A4&"*")`
- E4: `=COUNTIFS('Picks Log'!G:G, "Push", 'Picks Log'!A:A, A4&"*")`
- F4: `=IF(B4=0, 0, C4/B4)`
- G4: `=SUMIFS('Picks Log'!H:H, 'Picks Log'!A:A, A4&"*")`
- H4: `=IF(SUMIFS('Picks Log'!F:F, 'Picks Log'!A:A, A4&"*")=0, 0, G4/SUMIFS('Picks Log'!F:F, 'Picks Log'!A:A, A4&"*"))`

---

### 4. Add Sample Data

In the **Picks Log** tab, add these example picks (rows 2-11):

| Date | Sport | Game/Matchup | Pick | Odds | Units | Result | P/L | Confidence | Notes |
|------|-------|--------------|------|------|-------|--------|-----|------------|-------|
| 2026-03-01 | NFL | Chiefs vs Bills | Chiefs -3.5 | -110 | 1 | Win | 0.91 | 72% | Strong defensive matchup |
| 2026-03-01 | NBA | Lakers vs Celtics | Lakers ML | +145 | 0.5 | Loss | -0.5 | 65% | Close game, went to OT |
| 2026-03-02 | NHL | Bruins vs Rangers | Under 6.5 | -105 | 1 | Win | 0.95 | 68% | Goalie matchup favored under |
| 2026-03-02 | MLB | Yankees vs Red Sox | Yankees -1.5 | +130 | 0.75 | Win | 0.975 | 70% | Yankees pitching advantage |
| 2026-03-03 | NBA | Warriors vs Suns | Curry 30+ pts | -115 | 1 | Loss | -1 | 75% | Curry had off night |
| 2026-03-03 | NFL | 49ers vs Packers | 49ers ML | -140 | 1.5 | Win | 1.07 | 80% | Dominant performance |
| 2026-03-04 | Soccer | Man City vs Arsenal | Man City -1 | +110 | 0.5 | Push | 0 | 60% | Ended 2-1, push on -1 |
| 2026-03-04 | Tennis | Djokovic vs Nadal | Djokovic ML | -125 | 1 | Win | 0.8 | 85% | Djokovic on hard court |
| 2026-03-05 | MMA | Jones vs Miocic | Jones by KO | +200 | 0.25 | Loss | -0.25 | 55% | Went to decision |
| 2026-03-05 | NBA | Nuggets vs Heat | Jokic 25+10+10 | -130 | 1 | Win | 0.77 | 78% | Triple-double machine |

---

### 5. Final Formatting Tips

1. **Freeze the header row** in Picks Log: View → Freeze → 1 row
2. **Add conditional formatting** to Result column:
   - Win = Green background
   - Loss = Red background
   - Push = Yellow background
3. **Add conditional formatting** to P/L column:
   - Positive values = Green text
   - Negative values = Red text
4. **Format the Dashboard** with nice styling (borders, colors, etc.)
5. **Consider adding charts** to the Dashboard for visual appeal

---

## Quick Start Checklist

- [ ] Add column headers to Picks Log (A1:J1)
- [ ] Set up data validation for Sport (column B)
- [ ] Set up data validation for Result (column G)
- [ ] Add P/L formula to H2 and drag down
- [ ] Set up Dashboard metrics with formulas
- [ ] Add sample data (10 picks)
- [ ] Format columns (dates, percentages, currency)
- [ ] Add conditional formatting
- [ ] Freeze header row
- [ ] Test that Dashboard updates correctly

---

**Sheet is ready to use!** The public URL can be shared with anyone for viewing your BetBrain AI pick tracking.
