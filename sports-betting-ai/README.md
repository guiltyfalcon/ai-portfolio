# 🏆 Sports Betting AI

**Production-Ready Multi-Sport Prediction & Bet Tracking Platform**

A comprehensive sports betting intelligence application that combines live odds data, ML-powered predictions, and professional bet tracking with bankroll management.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🎯 Overview

Sports Betting AI is a full-featured betting intelligence platform covering **NBA, NFL, MLB, NHL, and NCAAB**. It provides:

- **Live Predictions** - Probability-based game predictions with confidence scores
- **Value Bet Detection** - Automatically identifies +EV betting opportunities
- **Bet Tracking** - Complete bankroll management with ROI analytics
- **Performance Analytics** - Win/loss tracking, streaks, sport breakdowns
- **Kelly Criterion** - Built-in stake sizing calculator

---

## ✨ Features

### 📊 Main Dashboard
| Feature | Description |
|---------|-------------|
| **Live Predictions** | Game predictions with win probabilities for today's games |
| **Value Bets** | Highlights bets where odds exceed predicted probability (+EV) |
| **Multi-Sport Coverage** | NBA, NFL, MLB, NHL, NCAAB, NCAAF |
| **Real-Time Odds** | Live odds from multiple bookmakers (requires API key) |
| **Team Stats** | Standings, injuries, recent performance integrated |

### 📈 Bet Tracker
| Feature | Description |
|---------|-------------|
| **Bankroll Management** | Set starting bankroll, track current balance |
| **Quick Bet Entry** | Fast input with common bet type presets |
| **Kelly Calculator** | Recommended stake based on edge and bankroll |
| **Performance Charts** | Win/loss distribution, profit over time, sport breakdown |
| **Streak Tracking** | Current and longest winning/losing streaks |
| **CSV Export/Import** | Backup and restore bet history |
| **Filtering** | Filter by sport, date range, bet type, status |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/sports-betting-ai

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
# Start the Streamlit app
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🔑 API Configuration

### Optional: The Odds API

For live betting odds from multiple bookmakers:

1. Get a free API key at [the-odds-api.com](https://the-odds-api.com)
2. Create `.streamlit/secrets.toml`:
   ```toml
   THEODDS_API_KEY = "your_api_key_here"
   ```

**Free Tier:** 500 requests/month (sufficient for personal use)

### Optional: BallDontLie API

For additional NBA stats:

1. Get a free API key at [balldontlie.io](https://www.balldontlie.io)
2. Add to `.streamlit/secrets.toml`:
   ```toml
   BALLDONTLIE_API_KEY = "your_api_key_here"
   ```

### No API Keys? No Problem!

The app works fully with just ESPN's free API:
- ✅ Game predictions
- ✅ Team standings and stats
- ✅ Bet tracking functionality
- ❌ Live odds comparison (requires The Odds API)

---

## 📁 Project Structure

```
sports-betting-ai/
├── Home.py                      # Main dashboard entry point
├── sports-betting-ai.py         # Alternative entry point
├── auth.py                      # Authentication utilities
├── requirements.txt             # Python dependencies
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── api/                        # Data layer
│   ├── espn.py                 # ESPN API client
│   ├── odds.py                 # The Odds API client
│   ├── balldontlie.py          # BallDontLie API client
│   ├── yahoo_scraper.py        # Yahoo odds scraper (automated)
│   └── webhook.py              # Webhook handlers
├── models/                     # ML layer
│   ├── predictor.py            # Game prediction models
│   └── universal_predictor.py  # Cross-sport prediction
├── data/                       # Data storage
│   └── bet_tracker.py          # Bet tracking logic
├── pages/                      # Multi-page app navigation
│   └── 01_Bet_Tracker.py       # Bet tracker dashboard
└── utils/                      # Utilities
    └── config.py               # Configuration helpers
```

---

## 📊 Screenshots

### Main Dashboard
*Live predictions with probability scores and value bet detection*

### Bet Tracker
*Bankroll management, performance analytics, and bet history*

*(Screenshots coming soon - run locally to see the app in action)*

---

## 🤖 Automated Data Collection

The project includes automated scrapers that run on a schedule:

```bash
# Yahoo odds scraper (runs every 2 hours)
python3 api/yahoo_scraper.py
```

This automatically:
- Fetches odds for today and tomorrow
- Enriches with ESPN standings, injuries, recent results
- Caches data for fast app loading
- Commits updates to git for version history

---

## 🧮 Prediction Model

The prediction system uses:

1. **Team Strength Ratings** - Based on recent performance and standings
2. **Home Field Advantage** - Sport-specific home/away adjustments
3. **Head-to-Head History** - Historical matchup data when available
4. **Injury Impact** - Key player availability adjustments
5. **Rest Days** - Fatigue factor for back-to-back games

**Output:** Win probability for each team, confidence score, and recommended bet type.

---

## 📈 Bet Tracking Features

### Kelly Criterion Calculator

Automatically calculates optimal bet size based on:
- Your estimated edge (prediction vs odds)
- Current bankroll
- Risk tolerance (full Kelly, half Kelly, quarter Kelly)

### Performance Analytics

- **Overall Record** - Win/Loss/Push with win percentage
- **ROI** - Return on investment across all bets
- **Sport Breakdown** - Performance by league (NBA, NFL, etc.)
- **Profit Chart** - Cumulative profit over time
- **Streak Analysis** - Current and longest streaks

---

## 💡 Usage Tips

1. **Start Small** - Track bets even if you're not betting real money
2. **Use Kelly** - Let the calculator suggest stake sizes
3. **Export Regularly** - CSV backup before major changes
4. **Review Performance** - Check which sports you're best at
5. **No API Key?** - App still works great with ESPN data only

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| App won't start | Check Python 3.11+, run `pip install -r requirements.txt` |
| No odds showing | Add THEODDS_API_KEY to secrets.toml |
| Predictions not loading | Check internet connection, ESPN API is free |
| Bets not persisting | Use CSV export (session clears on refresh by design) |
| Port already in use | Run `streamlit run Home.py --server.port 8502` |

---

## 🔮 Future Enhancements

- [ ] User authentication with persistent cloud storage
- [ ] Advanced ML models (XGBoost, LSTM for time series)
- [ ] Parlay builder with combined EV calculation
- [ ] Player props tracking and analysis
- [ ] Historical backtesting interface
- [ ] Real-time push notifications for value bets
- [ ] Mobile-responsive UI improvements

---

## 📝 License

MIT License — Feel free to use, modify, and distribute.

---

## 🙏 Credits

- **ESPN API** - Free sports data and statistics
- **The Odds API** - Live betting odds from multiple bookmakers
- **BallDontLie** - NBA stats and player data
- **Streamlit** - Amazing web application framework

---

## 📧 Contact

**DJ** - [guiltyfalcon.github.io](https://guiltyfalcon.github.io)

Part of the [AI Portfolio](../) collection.
