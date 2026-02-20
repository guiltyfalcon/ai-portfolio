# 😊 Sentiment Analyzer

AI-powered sentiment analysis tool that classifies text as positive, negative, or neutral.

## Features

- 📝 Single text analysis with confidence scores
- 📊 Batch analysis (CSV upload ready)
- 📈 Interactive visualizations (gauge charts, pie charts)
- ☁️ Word cloud generation
- 🎯 Rule-based + ML hybrid approach

## Demo

**Live App:** [Coming Soon - Deploy to Streamlit Cloud]

## Tech Stack

- Python 3.11+
- Streamlit
- Plotly, Matplotlib
- scikit-learn (for advanced mode)
- NLTK

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download NLTK data (if needed)
python -c "import nltk; nltk.download('punkt')"

# Run app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New App"
3. Select repository and branch
4. Set main file: `sentiment-analyzer/app.py`
5. Deploy!

## How It Works

1. **Text Preprocessing:** Cleans and tokenizes input
2. **Sentiment Detection:** Scans for positive/negative words
3. **Negation Handling:** Understands "not good" vs "good"
4. **Confidence Scoring:** Calculates based on word ratios

## Example Results

| Text | Sentiment | Confidence |
|------|-----------|------------|
| "I absolutely love this!" | 😊 Positive | 95% |
| "Terrible waste of money" | 😞 Negative | 92% |
| "It arrived on time" | 😐 Neutral | 50% |

---

Part of the [AI Portfolio](../)
