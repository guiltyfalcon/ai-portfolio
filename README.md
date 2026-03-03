# AI Portfolio 🤖

A collection of production-grade AI applications built with Python, Streamlit, and modern ML frameworks.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Projects

| Project | Description | Status |
|---------|-------------|--------|
| **🏆 Sports Betting AI** | Multi-sport prediction engine with ML-powered value bets, bet tracking, and live odds | ⭐ Production Ready |
| **💪 Fitness Chatbot** | AI fitness & nutrition assistant powered by GPT | ✅ Complete |
| **😊 Sentiment Analyzer** | Real-time sentiment analysis with visualizations and word clouds | ✅ Complete |
| **🖼️ Image Classifier** | Deep learning image classification with MobileNetV2 | ✅ Complete |
| **💬 QA Bot** | Smart Q&A chatbot with conversation history and context | ✅ Complete |
| **📰 RPA News Summarizer** | Intelligent RPA engine for automated news aggregation and summarization | ✅ Complete |
| **🧩 Code Explainer** | AI utility for translating code to plain English documentation | ✅ Complete |

---

## 🏆 Featured Project: Sports Betting AI

**Production-Ready Multi-Sport Prediction Engine**

A comprehensive sports betting intelligence platform covering NBA, NFL, MLB, NHL, NCAAB:

**Features:**
- 🔮 **Live Predictions** - Probability-based game predictions with confidence scores
- 💰 **Value Bet Detection** - Automatically finds +EV betting opportunities
- 📊 **Player Props** - Props analysis for all major sports
- 📈 **Bet Tracking** - Full bankroll management with ROI analytics
- 🔄 **Live Odds** - Real-time odds comparison across multiple bookmakers
- 🧮 **Kelly Criterion** - Built-in stake sizing calculator
- 📤 **CSV Export** - Export your bet history for analysis
- 📉 **Performance Analytics** - Win/loss tracking, streaks, sport-by-sport breakdown

**Tech Stack:**
- Python 3.13, Streamlit, scikit-learn, pandas, numpy
- ESPN API (free), The Odds API, BallDontLie API
- Automated data collection with cron-scheduled scrapers

**Quick Start:**
```bash
cd sports-betting-ai
pip install -r requirements.txt
streamlit run Home.py
```

**See Full Docs:** [`sports-betting-ai/README.md`](sports-betting-ai/README.md)

---

## 🛠️ Technologies Used

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.11+ |
| **Web Framework** | Streamlit |
| **ML/AI** | scikit-learn, TensorFlow/Keras, OpenAI GPT |
| **Data** | pandas, numpy, requests |
| **Visualization** | Plotly, Matplotlib, WordCloud |
| **APIs** | ESPN, The Odds API, BallDontLie, OpenAI |
| **Deployment** | Streamlit Cloud, GitHub Actions |

---

## 🚀 Quick Start

### Method 1: Virtual Environment (Recommended)

```bash
# Clone repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio

# Choose a project
cd sports-betting-ai  # or fitness-chatbot, sentiment-analyzer, etc.

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run Home.py    # or app.py depending on project
```

### Method 2: System-Wide (macOS/Linux)

```bash
# Clone and navigate
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/sports-betting-ai  # or other project

# Install dependencies
pip install --break-system-packages -r requirements.txt

# Run the app
streamlit run Home.py
```

### Deploy to Streamlit Cloud

**All apps are ready for one-click deployment:**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app" and select `guiltyfalcon/ai-portfolio`
3. Set main file path for each app:
   - Sports Betting AI: `sports-betting-ai/Home.py`
   - Fitness Chatbot: `fitness-chatbot/app.py`
   - Sentiment Analyzer: `sentiment-analyzer/app.py`
   - Image Classifier: `image-classifier/app.py`
   - QA Bot: `qa-bot/app.py`
   - RPA News Summarizer: `rpa-news-summarizer/app.py`
   - Code Explainer: `code-explainer/app.py`
4. Add required API keys in Secrets (see individual READMEs)
5. Deploy!

**Note:** Some apps (Fitness Chatbot, QA Bot, Code Explainer, News Summarizer) require OpenAI API keys. Sports Betting AI works with free ESPN API.

---

## 🔑 API Keys

Some projects need API keys (all have free tiers):

| Project | API | Required | Get Key |
|---------|-----|----------|---------|
| Sports Betting AI | The Odds API | Optional | [the-odds-api.com](https://the-odds-api.com) |
| Sports Betting AI | BallDontLie | Optional | [balldontlie.io](https://www.balldontlie.io) |
| Fitness Chatbot | OpenAI | Yes | [platform.openai.com](https://platform.openai.com) |
| QA Bot | OpenAI | Yes | [platform.openai.com](https://platform.openai.com) |
| Code Explainer | OpenAI | Yes | [platform.openai.com](https://platform.openai.com) |

**Note:** Sports Betting AI works without API keys using ESPN's free API + cached data.

---

## 💡 What Makes This Portfolio Different

**These aren't tutorials — they're production-ready applications:**

✅ **Real Data Integration** - Live APIs (ESPN, Odds, OpenAI) with proper error handling  
✅ **Automated Data Collection** - Cron-scheduled scrapers keep data fresh  
✅ **Full-Stack Thinking** - Backend logic, frontend UI, deployment considerations  
✅ **Clean Architecture** - Modular code with separation of concerns  
✅ **Documentation** - Each project has clear README with setup instructions  

**Sports Betting AI** demonstrates the most complexity:
- Automated odds scraping every 2 hours
- Multi-page Streamlit app with navigation
- Bet tracking with persistent storage
- ML-powered predictions with probability scores
- Performance analytics and visualization

---

## 📝 License

MIT License — Feel free to use this code for your own projects!

---

## 👨‍💻 Author

**DJ** — Cloud administrator, digital entrepreneur, AI enthusiast

- 🔗 Portfolio: [guiltyfalcon.github.io](https://guiltyfalcon.github.io)
- 💼 GitHub: [@guiltyfalcon](https://github.com/guiltyfalcon)

---

*Built with ❤️ and ☕ using Python + Streamlit*
