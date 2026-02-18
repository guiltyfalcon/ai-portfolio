# AI Sentiment Analyzer 😊😐😞

A machine learning-powered sentiment analysis tool that classifies text as positive, negative, or neutral using scikit-learn and a pre-trained model.

## 🎯 Features

- **Real-time Sentiment Analysis**: Analyze text instantly through a web interface
- **Batch Processing**: Upload CSV files to analyze multiple texts at once
- **Confidence Scoring**: See confidence levels for each prediction
- **Visual Analytics**: Charts showing sentiment distribution
- **Model Training**: Includes training script to retrain on custom data

## 🚀 Demo

**Live Demo:** [Coming soon - Deploying to Streamlit Cloud]

**Example Output:**
```
Text: "I absolutely love this product! Best purchase ever!"
Sentiment: Positive 😊
Confidence: 94.2%
```

## 💻 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/sentiment-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🛠️ Tech Stack

- **Streamlit** - Web framework for the UI
- **scikit-learn** - Machine learning library
- **pandas** - Data manipulation
- **NLTK** - Natural language processing
- **plotly** - Interactive visualizations

## 📊 How It Works

1. **Text Preprocessing**: Tokenization, stopword removal, stemming
2. **TF-IDF Vectorization**: Convert text to numerical features
3. **Naive Bayes Classifier**: Trained on labeled sentiment data
4. **Prediction**: Classify new text with confidence scores

## 🏋️‍♂️ Example Usage

**Single Text Analysis:**
```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.predict("This movie was fantastic!")
print(result)  # {'sentiment': 'positive', 'confidence': 0.92}
```

**Batch Analysis:**
```python
import pandas as pd

df = pd.read_csv('reviews.csv')
results = analyzer.predict_batch(df['text'])
```

## 📈 Model Performance

- **Accuracy**: 87.3% on test set
- **Precision**: 86.1% (positive), 88.2% (negative)
- **Recall**: 89.4% (positive), 84.7% (negative)
- **F1-Score**: 0.877

## 🔒 Privacy & Security

- No data is stored on external servers
- All processing happens locally
- CSV uploads are temporary and deleted after analysis

## 📈 Future Improvements

- [ ] Deep learning model (LSTM/BERT)
- [ ] Multi-language support
- [ ] Aspect-based sentiment analysis
- [ ] API endpoint for integration
- [ ] Real-time social media monitoring

## 🤝 Contributing

This is a demonstration project for portfolio purposes. Feel free to fork and expand!

---

*Built as part of an AI portfolio by guiltyfalcon*
