# Sports Betting AI

**Live Website:** https://sports-betting-ai-demo.streamlit.app

A multi-sport prediction engine using machine learning to identify value bets across NBA, NFL, MLB, and NHL.

## 🚀 Quick Start

### Run Locally
```bash
cd sports-betting-ai
pip install -r requirements.txt
streamlit run Home.py
```

### Deploy to Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Set `THEODDS_API_KEY` in secrets
5. Deploy!

## 📁 Structure
```
sports-betting-ai/
├── Home.py                 # Entry point (streamlit multi-page)
├── .streamlit/config.toml  # Theme and settings
├── pages/                  # Additional pages
├── api/                    # Data sources
├── models/                 # ML models
├── ui/                     # Dashboard components
└── requirements.txt
```

## 🔑 API Keys Required
- **The Odds API**: Get free key at [the-odds-api.com](https://the-odds-api.com)
- **ESPN API**: Free, no key needed

Set in Streamlit Cloud secrets or `.env` file.

---
**Live Demo:** https://sports-betting-ai-demo.streamlit.app
