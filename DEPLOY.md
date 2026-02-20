# Deployment Guide

Complete guide for deploying any project in this portfolio to Streamlit Cloud.

---

## 🚀 Quick Deploy (Any Project)

### Step 1: Prerequisites
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Step 2: Deploy

**Option A: Deploy from this repo**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New App"
3. Select repository: `guiltyfalcon/ai-portfolio`
4. Select branch: `main`
5. Set main file path:
   - Sports Betting AI: `sports-betting-ai/Home.py`
   - Fitness Chatbot: `fitness-chatbot/app.py`
   - Sentiment Analyzer: `sentiment-analyzer/app.py`
   - Image Classifier: `image-classifier/app.py`
   - QA Bot: `qa-bot/app.py`
6. Click "Deploy"

**Option B: Copy to separate repo** (Recommended for production)

1. Create new GitHub repo (e.g., `my-fitness-chatbot`)
2. Copy project files:
   ```bash
   cp -r fitness-chatbot/* my-fitness-chatbot/
   cd my-fitness-chatbot
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```
3. Deploy from new repo on Streamlit Cloud

---

## 🔑 Adding API Keys

### For Sports Betting AI

1. In Streamlit Cloud, go to your app → Settings → Secrets
2. Add:
```toml
THEODDS_API_KEY = "your-odds-api-key-here"
BALLDONTLIE_API_KEY = "your-balldontlie-key-here"
```
3. Redeploy app

**Get free API keys:**
- The Odds API: [the-odds-api.com](https://the-odds-api.com) (free tier: 500 calls/day)
- BallDontLie: [balldontlie.io](https://www.balldontlie.io) (free tier available)

### For Fitness Chatbot / QA Bot

1. Get OpenAI API key: [platform.openai.com](https://platform.openai.com)
2. Add to Streamlit Cloud secrets:
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

---

## 📋 Pre-Deployment Checklist

- [ ] `requirements.txt` exists with all dependencies
- [ ] `app.py` or `Home.py` is in project root
- [ ] `.gitignore` excludes `__pycache__/`, `.env`, secrets
- [ ] README.md has clear description
- [ ] All API keys added to Streamlit Cloud secrets
- [ ] Test locally: `streamlit run app.py`
- [ ] No hardcoded API keys in code

---

## 🐛 Troubleshooting

### "Module not found" error
Add missing package to `requirements.txt`

### "API key invalid" error
Check secrets are added in Streamlit Cloud settings

### App won't start
Check Streamlit Cloud logs (Settings → Logs)

### Slow loading
- Reduce image sizes
- Add caching with `@st.cache_data`
- Optimize data loading

---

## 🔄 Updating Deployed Apps

**Auto-update:**
- Push changes to GitHub
- Streamlit Cloud auto-redeploys

**Manual redeploy:**
- Go to app dashboard
- Click "Reboot"

---

## 📊 Current Deployments

| Project | Repo Path | Deployed URL |
|---------|-----------|--------------|
| Sports Betting AI | `sports-betting-ai/` | [Live](https://guiltyfalcon-ai-portfolio-sports-betting-aihome-jhaeqn.streamlit.app) |
| Fitness Chatbot | `fitness-chatbot/` | *Deploying* |
| Sentiment Analyzer | `sentiment-analyzer/` | *Deploying* |
| Image Classifier | `image-classifier/` | *Deploying* |
| QA Bot | `qa-bot/` | *Deploying* |

---

## 💡 Pro Tips

1. **Use separate repos** for production apps (easier management)
2. **Pin dependency versions** in `requirements.txt` (avoid breaking changes)
3. **Add caching** for API calls and data loading
4. **Monitor usage** in Streamlit Cloud dashboard
5. **Set up alerts** for when apps go down

---

## 🆘 Need Help?

- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io)
- Streamlit Forum: [discuss.streamlit.io](https://discuss.streamlit.io)
- GitHub Issues: Open issue in this repo

---

*Happy deploying! 🚀*
