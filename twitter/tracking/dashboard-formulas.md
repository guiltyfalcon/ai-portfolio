# BetBrain AI - Dashboard Formulas Reference

## Overview
This document contains all formulas needed for the BetBrain pick tracking dashboard. Formulas are written for Google Sheets but can be adapted for Excel.

---

## Core Metrics (Dashboard Sheet)

### B2: Total Picks
```excel
=COUNTA('Picks Log'!A:A)-1
```
*Counts all entries excluding header row*

---

### B3: Win Rate %
```excel
=IF(B2=0,0,COUNTIF('Picks Log'!G:G,"Win")/B2)
```
*Calculates wins divided by total picks. Returns 0 if no picks yet.*

**Alternative (excludes pushes):**
```excel
=IF(COUNTIF('Picks Log'!G:G,"Win")+COUNTIF('Picks Log'!G:G,"Loss")=0,0,COUNTIF('Picks Log'!G:G,"Win")/(COUNTIF('Picks Log'!G:G,"Win")+COUNTIF('Picks Log'!G:G,"Loss")))
```

---

### B4: Total Units Profit/Loss
```excel
=SUM('Picks Log'!H:H)
```
*Sums all profit/loss values from Column H*

---

### B5: ROI %
```excel
=IF(SUM('Picks Log'!F:F)=0,0,B4/SUM('Picks Log'!F:F))
```
*Total P/L divided by total units wagered*

---

### B6: Average Odds
```excel
=AVERAGE('Picks Log'!E:E)
```
*Simple average of all odds*

**For American odds conversion to implied probability:**
```excel
=AVERAGE(IF('Picks Log'!E:E>0,100/('Picks Log'!E:E+100),ABS('Picks Log'!E:E)/(ABS('Picks Log'!E:E)+100)))
```
*Array formula - enter with Ctrl+Shift+Enter in Excel*

---

### B7: Current Streak
```excel
=LET(
  results, FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),
  lastResult, INDEX(results, ROWS(results)),
  streakCount, 0,
  i, ROWS(results),
  WHILE(i>0,
    IF(INDEX(results,i)=lastResult,
      streakCount+1,
      BREAK(streakCount)
    ),
    i-1
  ),
  IF(lastResult="Win", streakCount, -streakCount)
)
```

**Simplified version (Google Sheets):**
```excel
=IF(ARRAY_CONSTRAIN(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),1,1)="Win",
  COUNTA(TAKE(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),-1,COUNTIF(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),"Win"))),
  -COUNTA(TAKE(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),-1,COUNTIF(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),"Loss")))
)
```

**Even simpler (works in both):**
```excel
=IF(INDEX(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),ROWS(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>"")),"Win",
  MATCH("Loss",INDEX(SORT(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),ROWS(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>"")),1),,1),"Win"),0)-1,
  -MATCH("Win",INDEX(SORT(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>""),ROWS(FILTER('Picks Log'!G:G,'Picks Log'!G:G<>"")),1),,1),"Loss"),0)+1
)
```

**Most compatible version:**
```excel
=IF(OFFSET('Picks Log'!G1,COUNTA('Picks Log'!G:G)-1,0)="Win",
  COUNTIF(OFFSET('Picks Log'!G1,COUNTA('Picks Log'!G:G)-MATCH("Loss",OFFSET('Picks Log'!G1,COUNTA('Picks Log'!G:G)-1,0,-MATCH("Loss",OFFSET('Picks Log'!G1,0,0,COUNTA('Picks Log'!G:G)-1),0),0),0,-MATCH("Loss",OFFSET('Picks Log'!G1,0,0,COUNTA('Picks Log'!G:G)-1),0),0),"Loss")+1,
  -COUNTIF(OFFSET('Picks Log'!G1,COUNTA('Picks Log'!G:G)-1,0,-MATCH("Win",OFFSET('Picks Log'!G1,COUNTA('Picks Log'!G:G)-1,0,-MATCH("Win",OFFSET('Picks Log'!G1,0,0,COUNTA('Picks Log'!G:G)-1),0),0),0,-MATCH("Win",OFFSET('Picks Log'!G1,0,0,COUNTA('Picks Log'!G:G)-1),0),0),"Win")+1
)
```

**Recommended (simplest, most reliable):**
```excel
=IF(COUNTA('Picks Log'!G:G)<=1,0,
  IF(INDEX('Picks Log'!G:G,COUNTA('Picks Log'!G:G))="Win",
    COUNTIF(INDEX('Picks Log'!G:G,COUNTA('Picks Log'!G:G)-COUNTIF(INDEX('Picks Log'!G:G,1:COUNTA('Picks Log'!G:G)),"Loss")):INDEX('Picks Log'!G:G,COUNTA('Picks Log'!G:G)),"Win"),
    -COUNTIF(INDEX('Picks Log'!G:G,COUNTA('Picks Log'!G:G)-COUNTIF(INDEX('Picks Log'!G:G,1:COUNTA('Picks Log'!G:G)),"Win")):INDEX('Picks Log'!G:G,COUNTA('Picks Log'!G:G)),"Loss")
  )
)
```

---

### B8: Best Sport by ROI
```excel
=INDEX(FILTER(UNIQUE('Picks Log'!B:B),UNIQUE('Picks Log'!B:B)<>""),
  MATCH(MAX(IF(UNIQUE('Picks Log'!B:B)<>"",
    SUMIF('Picks Log'!B:B,UNIQUE('Picks Log'!B:B),'Picks Log'!H:H)/SUMIF('Picks Log'!B:B,UNIQUE('Picks Log'!B:B),'Picks Log'!F:F),0)),
    IF(UNIQUE('Picks Log'!B:B)<>"",
      SUMIF('Picks Log'!B:B,UNIQUE('Picks Log'!B:B),'Picks Log'!H:H)/SUMIF('Picks Log'!B:B,UNIQUE('Picks Log'!B:B),'Picks Log'!F:F),0),0))
```

**Array formula version:**
```excel
=LET(
  sports, UNIQUE(FILTER('Picks Log'!B:B,'Picks Log'!B:B<>"")),
  sportROI, MAP(sports, LAMBDA(s, SUMIF('Picks Log'!B:B,s,'Picks Log'!H:H)/SUMIF('Picks Log'!B:B,s,'Picks Log'!F:F))),
  INDEX(sports, MATCH(MAX(sportROI), sportROI, 0))
)
```

---

### B9: Best Prop Type by ROI
*Requires extracting prop type from Column D (Pick)*

```excel
=LET(
  props, UNIQUE(FILTER(
    IF(REGEXMATCH('Picks Log'!D:D,"Moneyline"),"Moneyline",
    IF(REGEXMATCH('Picks Log'!D:D,"Spread"),"Spread",
    IF(REGEXMATCH('Picks Log'!D:D,"Total|Over|Under"),"Total",
    IF(REGEXMATCH('Picks Log'!D:D,"Points"),"Points",
    IF(REGEXMATCH('Picks Log'!D:D,"Rebounds"),"Rebounds",
    IF(REGEXMATCH('Picks Log'!D:D,"Assists"),"Assists",
    IF(REGEXMATCH('Picks Log'!D:D,"Prop"),"Other Prop","Unknown")))))))),
    'Picks Log'!D:D<>"")),
  propROI, MAP(props, LAMBDA(p, 
    SUMIF('Picks Log'!D:D,"*"&p&"*",'Picks Log'!H:H)/SUMIF('Picks Log'!D:D,"*"&p&"*",'Picks Log'!F:F))),
  INDEX(props, MATCH(MAX(propROI), propROI, 0))
)
```

---

### B10: Last Updated
```excel
=NOW()
```
*Updates automatically on sheet recalculation*

---

## Profit/Loss Calculation (Picks Log Column H)

### H2 Formula (copy down for all rows)
```excel
=IF(G2="", "", 
  IF(G2="Push", 0,
    IF(G2="Win", 
      IF(E2>0, F2*(E2/100), F2*(100/ABS(E2))),
      IF(G2="Loss", -F2, "")
    )
  )
)
```

**Explanation:**
- If Result is empty: return empty
- If Push: return 0
- If Win and positive odds (underdog): units × (odds/100)
- If Win and negative odds (favorite): units × (100/|odds|)
- If Loss: negative units wagered

---

## Monthly Summary Formulas

### Month Column (A2, copy down)
```excel
=TEXT('Picks Log'!A2, "YYYY-MM")
```

### Picks per Month (B2, copy down)
```excel
=COUNTIF('Picks Log'!$A:$A, ">="&DATE(YEAR(A2),MONTH(A2),1))-COUNTIF('Picks Log'!$A:$A, ">="&EDATE(A2,1))
```

**Alternative:**
```excel
=COUNTIFS('Picks Log'!$A:$A, ">="&A2&"-01", 'Picks Log'!$A:$A, "<"&EDATE(A2&"-01",1))
```

### Wins per Month (C2)
```excel
=COUNTIFS('Picks Log'!$A:$A, ">="&A2&"-01", 'Picks Log'!$A:$A, "<"&EDATE(A2&"-01",1), 'Picks Log'!$G:$G, "Win")
```

### Losses per Month (D2)
```excel
=COUNTIFS('Picks Log'!$A:$A, ">="&A2&"-01", 'Picks Log'!$A:$A, "<"&EDATE(A2&"-01",1), 'Picks Log'!$G:$G, "Loss")
```

### Win Rate per Month (E2)
```excel
=IF(C2+D2=0, 0, C2/(C2+D2))
```

### Units P/L per Month (F2)
```excel
=SUMIFS('Picks Log'!$H:$H, 'Picks Log'!$A:$A, ">="&A2&"-01", 'Picks Log'!$A:$A, "<"&EDATE(A2&"-01",1))
```

### ROI per Month (G2)
```excel
=IF(SUMIFS('Picks Log'!$F:$F, 'Picks Log'!$A:$A, ">="&A2&"-01", 'Picks Log'!$A:$A, "<"&EDATE(A2&"-01",1))=0, 0, F2/SUMIFS('Picks Log'!$F:$F, 'Picks Log'!$A:$A, ">="&A2&"-01", 'Picks Log'!$A:$A, "<"&EDATE(A2&"-01",1)))
```

---

## Chart Data Ranges

### Win/Loss by Sport (for Column Chart)

| Range | Formula |
|-------|---------|
| Sports List | `=UNIQUE(FILTER('Picks Log'!B:B,'Picks Log'!B:B<>""))` |
| Wins per Sport | `=COUNTIF('Picks Log'!B:B, A2, 'Picks Log'!G:G, "Win")` |
| Losses per Sport | `=COUNTIF('Picks Log'!B:B, A2, 'Picks Log'!G:G, "Loss")` |

### ROI Trend Over Time (for Line Chart)

| Range | Formula |
|-------|---------|
| Dates | `='Picks Log'!A:A` |
| Cumulative ROI | Running calculation of total P/L ÷ total units |

**Cumulative ROI Formula (K2, copy down):**
```excel
=IF(A2="","",SUM($H$2:H2)/SUM($F$2:F2))
```

### Monthly Breakdown (for Bar Chart)

Use Monthly Summary sheet columns A (Month) and F (Units P/L) or G (ROI)

---

## Advanced Analytics (Optional)

### Kelly Criterion Recommendation
```excel
=IF(I2="","",((E2/100*(I2/100))-(1-(I2/100)))/(E2/100)*100)
```
*Suggests optimal bet size based on edge and odds*

### Expected Value (EV)
```excel
=IF(OR(E2="",I2=""),"",
  (I2/100 * IF(E2>0,E2/100,100/ABS(E2))) - ((1-I2/100) * 1)
)
```
*Positive EV indicates profitable long-term bet*

### Sharp Money Indicator
```excel
=IF(AND(I2>=75,ABS(E2)>=150),"SHARP","REGULAR")
```
*Flags high-confidence plays on significant lines*

---

## Conditional Formatting Rules

### Profit/Loss Column (H)

**Green (Positive):**
- Format: Green fill, dark green text
- Formula: `=$H2>0`

**Red (Negative):**
- Format: Red fill, dark red text
- Formula: `=$H2<0`

**Yellow (Push/Zero):**
- Format: Yellow fill, black text
- Formula: `=$H2=0`

### AI Confidence Column (I)

**High Confidence (Green):**
- Format: Green fill
- Formula: `=$I2>=70`

**Medium Confidence (Yellow):**
- Format: Yellow fill
- Formula: `=AND($I2>=60,$I2<70)`

**Low Confidence (Red):**
- Format: Red fill
- Formula: `=$I2<60`

### Result Column (G)

**Win:**
- Format: Green background
- Formula: `=$G2="Win"`

**Loss:**
- Format: Red background
- Formula: `=$G2="Loss"`

**Push:**
- Format: Gray background
- Formula: `=$G2="Push"`

---

## Data Validation Rules

### Sport Dropdown (Column B)
```
NBA,NFL,MLB,NHL,Soccer,Tennis,Golf,Boxing,MMA,College Basketball,College Football,Other
```

### Result Dropdown (Column G)
```
Win,Loss,Push
```

### AI Confidence Range (Column I)
- Minimum: 50
- Maximum: 100
- Step: 1

### Odds Format (Column E)
- Custom formula to validate American odds format:
```excel
=OR(AND(E2>=-10000,E2<=-100),AND(E2>=100,E2<=10000),E2="")
```

---

## Performance Optimization Tips

1. **Use ARRAYFORMULA** where possible to reduce calculation overhead
2. **Avoid entire column references** in complex formulas (use specific ranges)
3. **Use FILTER instead of array formulas** in Google Sheets for better performance
4. **Limit volatile functions** (NOW, TODAY, RAND) to necessary cells only
5. **Consider helper columns** for complex calculations that are referenced multiple times

---

## Error Handling

### IFERROR Wrapper
Wrap complex formulas to handle empty data gracefully:
```excel
=IFERROR(your_formula, 0)
```
or
```excel
=IFERROR(your_formula, "No data yet")
```

### Check for Division by Zero
```excel
=IF(denominator=0, 0, numerator/denominator)
```

---

## Testing Your Formulas

1. Enter 5-10 sample picks with varying results
2. Verify Profit/Loss calculates correctly
3. Check Win Rate matches manual calculation
4. Confirm ROI is accurate
5. Test streak counter with different W/L sequences
6. Verify sport/prop type breakdowns work correctly

---

## Version Notes

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-05 | Initial formula set |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| #DIV/0! error | Add IF check for zero denominator |
| #VALUE! error | Check data types match (text vs number) |
| Formula not updating | Check calculation settings (should be Automatic) |
| Slow performance | Reduce range sizes, use helper columns |
| Streak not working | Verify Result column has exact text matches |
