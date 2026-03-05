# BetBrain AI - Bet Slip Graphic Template

## Overview
Text-based template for creating bet slip graphics in Canva. Designed for Twitter posts showcasing AI-powered betting picks.

---

## Layout Specifications

### Canvas Size
- **Dimensions:** 1080 x 1080 px (Square format for Twitter)
- **Alternative:** 1080 x 1350 px (Portrait for more vertical space)

### Color Scheme
| Element | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| Background | Black | #000000 | Main canvas background |
| Primary Accent | Green | #00FF88 | Wins, confidence bars, highlights |
| Secondary | White | #FFFFFF | Text, borders, icons |
| Dark Gray | Gray | #1A1A1A | Card backgrounds, sections |
| Light Gray | Gray | #333333 | Dividers, secondary elements |

### Typography
| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Header (BetBrain AI) | Montserrat / Poppins | 48px | Bold | White |
| Pick Title | Montserrat / Poppins | 36px | Bold | White |
| Odds | Roboto Mono / Space Mono | 32px | Bold | Green (#00FF88) |
| Labels (Confidence, Units, etc.) | Montserrat | 20px | Medium | Light Gray (#CCCCCC) |
| Values | Montserrat | 24px | Bold | White |
| AI Analysis | Montserrat | 18px | Regular | White |

---

## Template Structure

```
┌─────────────────────────────────────────┐
│  🧠 BETBRAIN AI                    ⚡   │  ← Header Bar
├─────────────────────────────────────────┤
│                                         │
│           DAILY PICK                    │  ← Pick Title
│                                         │
│    [Team/Player Name]                   │
│    [vs Opponent / Event]                │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│   ODDS           CONFIDENCE             │
│   +150           ████████░░ 80%        │
│                                         │
│   UNITS          AI ANALYSIS            │
│   2.5U           [Brief analysis text   │
│                  explaining the pick    │
│                  rationale in 2-3 lines]│
│                                         │
├─────────────────────────────────────────┤
│  🎯 @holikidTV     #BetBrain #Betting   │  ← Footer
└─────────────────────────────────────────┘
```

---

## Field Specifications

### 1. Header Bar
- **Height:** 80px
- **Background:** Dark gradient (Black to #1A1A1A)
- **Left:** 🧠 BETBRAIN AI logo/text
- **Right:** ⚡ lightning bolt icon

### 2. Pick Title Section
- **Height:** 200px
- **Background:** Black
- **Content:**
  - "DAILY PICK" or "FEATURED PLAY" label (small, green)
  - Main pick title (large, white)
  - Matchup details (medium, light gray)

### 3. Stats Grid (2x2)
- **Height:** 350px
- **Background:** Dark gray cards (#1A1A1A)
- **Layout:**
  - Top Left: ODDS (large green number)
  - Top Right: CONFIDENCE (progress bar + percentage)
  - Bottom Left: UNITS (white number + "U")
  - Bottom Right: AI ANALYSIS (text block)

### 4. Footer Bar
- **Height:** 60px
- **Background:** Black
- **Left:** 🎯 @holikidTV
- **Right:** Hashtags (#BetBrain #Betting #AIPicks)

---

## Example: Filled Out Template

```
┌─────────────────────────────────────────┐
│  🧠 BETBRAIN AI                    ⚡   │
├─────────────────────────────────────────┤
│                                         │
│           DAILY PICK                    │
│                                         │
│    Kansas City Chiefs                   │
│    vs Buffalo Bills - NFL Playoffs      │
│    Spread: Chiefs -3.5                  │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│   ODDS           CONFIDENCE             │
│   -110           ████████░░ 82%        │
│                                         │
│   UNITS          AI ANALYSIS            │
│   3U             Chiefs cover 78% in    │
│                  playoff road games     │
│                  when favored. Bills    │
│                  missing key defender.  │
│                                         │
├─────────────────────────────────────────┤
│  🎯 @holikidTV     #BetBrain #NFL       │
└─────────────────────────────────────────┘
```

---

## Confidence Bar Visual

### Progress Bar Design
- **Total Width:** 200px
- **Height:** 12px
- **Background:** #333333 (dark gray)
- **Fill:** #00FF88 (green)
- **Border Radius:** 6px (rounded)

### Percentage Indicators
| Confidence | Bar Fill | Color | Text |
|------------|----------|-------|------|
| 90-100% | ██████████ | #00FF88 | "LOCK 🔒" |
| 75-89% | ████████░░ | #00FF88 | "HIGH" |
| 60-74% | ██████░░░░ | #FFD700 | "MEDIUM" |
| 50-59% | █████░░░░░ | #FFA500 | "MODERATE" |
| <50% | ████░░░░░░ | #FF4444 | "LOW" |

---

## Canva Build Instructions

1. **Create Design:** 1080 x 1080 px
2. **Background:** Solid black (#000000)
3. **Add Header Rectangle:** 1080 x 80px, gradient black to #1A1A1A
4. **Add Footer Rectangle:** 1080 x 60px, solid black
5. **Create 4 Cards:** 480 x 150px each, #1A1A1A background, 8px border radius
6. **Add Text Elements:** Use fonts specified above
7. **Create Confidence Bar:** Rectangle with rounded corners, green fill
8. **Add Icons:** Brain (🧠), Lightning (⚡), Target (🎯)
9. **Export:** PNG, high quality, transparent background if needed

---

## Export Settings for Twitter

- **Format:** PNG (preferred) or JPG
- **Quality:** 100% / Maximum
- **Color Profile:** sRGB
- **File Size:** Keep under 5MB (Twitter limit)
- **Resolution:** 72 DPI (screen optimized)

---

## Usage Notes

- Update odds and confidence for each pick
- Keep AI analysis concise (2-3 lines max)
- Use consistent units notation (e.g., "2.5U" or "3 Units")
- Rotate hashtags to avoid Twitter spam filters
- A/B test different layouts (square vs portrait)
