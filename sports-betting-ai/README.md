# Sports Betting AI Pro - Improved Version

An enhanced sports betting prediction and tracking application built with Streamlit.

## What's New in This Version

### Fixed Issues
- **Navigation Error Fixed**: Proper page structure that works with Streamlit's multi-page apps
- **API Error Handling**: Graceful fallbacks when The Odds API key is missing
- **Session State Persistence**: Better handling of bet tracking data
- **Duplicate Page Prevention**: Clean page structure without conflicts

### New Features

#### Enhanced Bet Tracker
- **Bankroll Management**: Set and track your starting bankroll
- **Kelly Criterion Calculator**: Built-in stake sizing recommendations
- **CSV Export/Import**: Backup and restore your bet history
- **Advanced Filtering**: Filter by sport, date range, and sort options
- **Performance Analytics**: 
  - Win/Loss/Push distribution pie chart
  - Profit over time line chart
  - Sport-by-sport performance breakdown
  - Winning and losing streak tracking
- **Quick Pick Buttons**: Fast entry for common bet types
- **Closing Line Value (CLV)**: Track your line shopping success

#### Improved UI
- **Modern Dark Theme**: Enhanced gradient backgrounds and glassmorphism cards
- **Animated Elements**: Live badge with pulse animation, gradient text effects
- **Responsive Layout**: Better column distribution and card layouts
- **Color-coded Results**: Green for wins, red for losses, orange for pushes

#### Enhanced APIs
- **ESPN API**: Added caching (5-minute TTL) for better performance
- **Odds API**: Better error handling and configuration checking
- **Support for More Sports**: NCAAB, NCAAF, Soccer, UFC
- **Live Games Tracking**: Real-time game status updates

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional but Recommended)

Create a `.streamlit/secrets.toml` file:
```toml
THEODDS_API_KEY = "your_api_key_here"
```

Get your free API key at: https://the-odds-api.com

### 3. Run the App
```bash
streamlit run Home.py
```

## File Structure
```
sports-betting-ai-improved/
├── Home.py                    # Main entry point
├── pages/
│   └── 01_Bet_Tracker.py      # Enhanced bet tracking
├── data/
│   └── bet_tracker.py         # Bet tracking logic
├── api/
│   ├── espn.py               # ESPN API client
│   └── odds.py               # The Odds API client
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Features Overview

### Main Dashboard (Home.py)
- Live sports predictions for NBA, NFL, MLB, NHL
- Value bet detection with edge calculation
- Real-time odds display
- Probability visualization
- Quick game tracking

### Bet Tracker (pages/01_Bet_Tracker.py)
- **Dashboard**: Overall statistics with charts
- **Add Bet**: Quick bet entry with Kelly calculator
- **Pending Bets**: Manage and settle pending wagers
- **History**: Complete bet history with filtering

## API Information

### ESPN API (Free)
- No API key required
- Provides team data, schedules, and scores
- Rate limited but generous

### The Odds API (Free Tier Available)
- Free tier: 500 requests/month
- Provides live betting odds
- Multiple bookmakers supported

## Tips for Users

1. **Start with the ESPN data**: The app works great even without The Odds API key
2. **Use the Kelly Criterion**: Let the calculator help with stake sizing
3. **Track everything**: Consistent tracking is key to improving
4. **Export regularly**: Backup your data with CSV exports
5. **Filter by sport**: Use filters to analyze performance by league

## Troubleshooting

### App won't start
- Check Python version (3.9+ recommended)
- Ensure all dependencies are installed
- Verify file structure is correct

### No odds showing
- Add THEODDS_API_KEY to secrets.toml
- Check API quota at https://the-odds-api.com

### Bets not saving
- Session state is cleared on page refresh (by design)
- Use CSV export to persist data between sessions

## Future Enhancements
- User authentication for persistent storage
- More advanced ML predictions
- Parlay builder with EV calculation
- Player props tracking
- Historical backtesting

## License
MIT License - Feel free to modify and distribute

## Credits
- ESPN API for free sports data
- The Odds API for live betting lines
- Streamlit for the amazing web framework
# Cache bust 1771706148
