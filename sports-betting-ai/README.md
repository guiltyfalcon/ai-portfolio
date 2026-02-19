# 🏆 Sports Betting AI

A multi-sport prediction engine using machine learning to identify value bets across NBA, NFL, MLB, and NHL.

## 🎯 Features

- **Multi-Sport Support**: NBA, NFL, MLB, NHL
- **Real-Time Odds**: Integration with The Odds API
- **Historical Data**: ESPN API for team/player stats
- **ML Predictions**: Neural network win probability models
- **Value Detection**: Identifies +EV (positive expected value) bets
- **Web Dashboard**: Streamlit interface for picks and tracking

## 🏗️ Architecture

```
sports-betting-ai/
├── api/              # Data sources (ESPN, Odds API)
├── data/             # Data processing & feature engineering
├── models/           # ML models for each sport
├── ui/               # Streamlit dashboard
├── utils/            # Helpers & config
└── requirements.txt  # Dependencies
```

## 📊 Data Sources

- **ESPN API**: Free, no auth required — team stats, player data, schedules
- **The Odds API**: Live betting lines — requires API key

## 🚀 Getting Started

1. Set your Odds API key: `export THEODDS_API_KEY=your_key`
2. Install dependencies: `pip install -r requirements.txt`
3. Run dashboard: `streamlit run ui/app.py`

## 📈 Model Performance

- NBA: Training on 5 seasons of historical data
- Features: ELO ratings, home/away, rest days, injuries, recent form
- Target: Win probability vs. implied odds from betting lines

---
*Built with TensorFlow, scikit-learn, and Streamlit*
