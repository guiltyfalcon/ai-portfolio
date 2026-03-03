# 😊 Sentiment Analyzer

**Real-Time Text Sentiment Analysis with Visualizations**

A powerful sentiment analysis tool that detects emotions in text, generates word clouds, and provides detailed visual analytics.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![NLP](https://img.shields.io/badge/NLP-Sentiment-green)

---

## 🎯 Overview

Sentiment Analyzer uses rule-based and machine learning techniques to analyze text sentiment. Perfect for analyzing customer feedback, social media posts, reviews, or any text content to understand emotional tone.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Sentiment Detection** | Classifies text as Positive, Negative, or Neutral |
| **Confidence Score** | Shows how confident the model is in its prediction |
| **Word Cloud** | Visual representation of most frequent words |
| **Emotion Breakdown** | Detailed analysis of specific emotions detected |
| **Batch Analysis** | Analyze multiple texts at once |
| **Export Results** | Download analysis as CSV |
| **Real-Time Processing** | Instant analysis as you type |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/sentiment-analyzer

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📊 How It Works

### Sentiment Analysis Methods

1. **Rule-Based Analysis**
   - Uses positive/negative word dictionaries
   - Considers negations and intensifiers
   - Fast and interpretable

2. **Machine Learning**
   - Trained on labeled sentiment datasets
   - Captures context and nuance
   - Higher accuracy on complex text

### Visualizations

- **Sentiment Gauge** - Visual indicator of overall sentiment
- **Word Cloud** - Size reflects word frequency
- **Emotion Chart** - Breakdown of specific emotions
- **Confidence Bar** - Model certainty visualization

---

## 💡 Use Cases

| Use Case | Example |
|----------|---------|
| **Customer Feedback** | Analyze product reviews for sentiment trends |
| **Social Media Monitoring** | Track brand sentiment across posts |
| **Survey Analysis** | Process open-ended survey responses |
| **Content Moderation** | Flag negative or toxic content |
| **Market Research** | Understand public opinion on topics |
| **Writing Assistant** | Check tone of emails or documents |

---

## 🏗️ Architecture

```
sentiment-analyzer/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
└── .streamlit/
    └── config.toml            # Streamlit configuration
```

---

## 📸 Features Showcase

### Text Input & Analysis
Enter any text and get instant sentiment analysis with confidence scores.

### Word Cloud Visualization
See which words dominate your text, sized by frequency.

### Sentiment Distribution
Visual breakdown of positive, negative, and neutral content.

---

## ⚙️ Technical Details

### Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
matplotlib>=3.7.0
wordcloud>=1.9.0
nltk>=3.8.0
scikit-learn>=1.3.0
```

### Sentiment Categories

| Category | Score Range | Color |
|----------|-------------|-------|
| **Positive** | 0.6 - 1.0 | 🟢 Green |
| **Neutral** | 0.4 - 0.6 | 🟡 Yellow |
| **Negative** | 0.0 - 0.4 | 🔴 Red |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Word cloud not showing | Ensure text has enough content (50+ words) |
| Slow analysis | Large texts take longer; try shorter chunks |
| Import errors | Run `pip install -r requirements.txt` |
| NLTK data missing | App downloads automatically on first run |

---

## 🔮 Future Enhancements

- [ ] Multi-language support (Spanish, French, German, etc.)
- [ ] Aspect-based sentiment (analyze specific topics)
- [ ] Sarcasm detection
- [ ] Emotion-specific models (anger, joy, sadness, fear)
- [ ] API endpoint for integration
- [ ] Historical trend analysis
- [ ] Comparison mode (compare multiple texts)

---

## 📝 License

MIT License — Feel free to use and modify.

---

## 🙏 Credits

- **NLTK** - Natural language processing tools
- **Plotly** - Interactive visualizations
- **WordCloud** - Word cloud generation
- **Streamlit** - Web application framework

---

Part of the [AI Portfolio](../) collection.
