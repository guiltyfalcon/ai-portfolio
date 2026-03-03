# 📰 RPA News Summarizer

**Intelligent News Aggregation & Summarization Engine**

Automatically aggregates news articles from multiple sources and uses AI to generate concise summaries, saving you hours of reading time.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai)

---

## 🎯 Overview

RPA News Summarizer uses Robotic Process Automation (RPA) techniques to fetch news from multiple sources and leverages OpenAI GPT to generate AI-powered summaries. Stay informed without information overload.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-Source Aggregation** | Fetch news from multiple RSS feeds and APIs |
| **AI Summarization** | GPT-powered concise summaries of long articles |
| **Topic Detection** | Automatically categorize articles by topic |
| **Batch Processing** | Summarize multiple articles at once |
| **Export Results** | Download summaries as PDF or Markdown |
| **Customizable Sources** | Add your own news RSS feeds |
| **Fresh News** - Set update schedules to keep content current |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/rpa-news-summarizer

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file with your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

Get your API key at [platform.openai.com](https://platform.openai.com)

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📊 How It Works

### Pipeline Architecture

1. **Article Fetching** - RPA agents scrape news from RSS feeds and URLs
2. **Content Extraction** - Extract article text, metadata, and publication info
3. **AI Summarization** - OpenAI GPT generates concise summaries
4. **Topic Classification** - Articles tagged by topic (tech, business, etc.)
5. **Display & Export** - User-friendly interface with export options

### Summarization Strategy

- **Executive Summary** - 2-3 sentence overview for quick scanning
- **Key Points** - Bullet points of main takeaways
- **Sentiment Analysis** - Positive, negative, or neutral tone detection

---

## 🏗️ Architecture

```
rpa-news-summarizer/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── feeds.json                  # RSS feed configuration
└── .streamlit/
    └── secrets.toml           # API keys (create this)
```

---

## ⚙️ Configuration

### Custom RSS Feeds

Edit `feeds.json` to add your own news sources:

```json
{
  "news_sources": [
    {
      "name": "TechCrunch",
      "url": "https://techcrunch.com/feed/",
      "category": "technology"
    },
    {
      "name": "BBC News",
      "url": "http://feeds.bbci.co.uk/news/rss.xml",
      "category": "general"
    }
  ]
}
```

### Summary Length

Adjust in `app.py`:

```python
max_summary_length = 150  # words
key_points_count = 5      # bullet points
```

---

## 💡 Use Cases

| Use Case | Example |
|----------|---------|
| **Morning Briefing** - Get daily news summaries in 5 minutes |
| **Industry Monitoring** - Track news in your sector automatically |
| **Competitor Research** - Summarize competitor news mentions |
| **Policy Tracking** - Monitor regulatory news and updates |
| **Research** - Gather and summarize articles on specific topics |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| RSS feeds not loading | Check feed URLs and internet connection |
| Summarization fails | Verify OpenAI API key is valid |
| Slow processing | Reduce number of articles per batch |
| Article text empty | Some sites block scraping; try other sources |

---

## 🔮 Future Enhancements

- [ ] Real-time push notifications for breaking news
- [ ] Multi-language support
- [ ] Custom keyword alerts
- [ ] Historical news archive search
- [ ] Integration with Slack/Teams
- [ ] Sentiment trend tracking over time
- [ ] Automated report generation

---

## 💰 Cost Estimate

Using GPT-3.5-turbo:
- ~$0.001 per article summary
- 1,000 articles ≈ $1.00

Very cost-effective for automated news consumption!

---

## 📝 License

MIT License — Feel free to use and modify.

---

## 🙏 Credits

- **OpenAI** - GPT summarization
- **feedparser** - RSS feed parsing
- **Streamlit** - Web application framework

---

Part of the [AI Portfolio](../) collection.