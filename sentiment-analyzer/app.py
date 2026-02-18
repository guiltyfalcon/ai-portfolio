import streamlit as st
import pickle
import re
import string
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="AI Sentiment Analyzer",
    page_icon="😊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sentiment-positive {
        color: #28a745;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #ffc107;
        font-size: 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class SentimentAnalyzer:
    """Simple sentiment analyzer using rule-based approach and ML."""
    
    def __init__(self):
        # Positive and negative word lists
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'wonderful',
            'love', 'like', 'best', 'perfect', 'beautiful', 'happy', 'joy', 'excited',
            'brilliant', 'outstanding', 'superb', 'marvelous', 'incredible', 'lovely',
            'pleasant', 'delightful', 'satisfied', 'recommend', 'impressive', 'positive'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting',
            'disappointed', 'poor', 'negative', 'sad', 'angry', 'frustrated', 'annoying',
            'boring', 'waste', 'useless', 'fails', 'broken', 'problem', 'issue', 'error',
            'fail', 'wrong', 'difficult', 'hard', 'impossible', 'ugly', 'mess'
        }
        
        self.negation_words = {
            'not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere',
            'hardly', 'scarcely', 'barely', "don't", "doesn't", "didn't", "won't",
            "wouldn't", "shouldn't", "couldn't", "can't", "cannot"
        }
    
    def preprocess(self, text):
        """Clean and preprocess text."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def analyze(self, text):
        """Analyze sentiment of text."""
        words = self.preprocess(text).split()
        
        pos_count = 0
        neg_count = 0
        negation_active = False
        
        for i, word in enumerate(words):
            # Check for negation
            if word in self.negation_words:
                negation_active = True
                continue
            
            # Check sentiment words
            if word in self.positive_words:
                if negation_active:
                    neg_count += 1
                    negation_active = False
                else:
                    pos_count += 1
            elif word in self.negative_words:
                if negation_active:
                    pos_count += 1
                    negation_active = False
                else:
                    neg_count += 1
            
            # Reset negation after 2 words
            if negation_active and i > 0 and words[i-1] in self.negation_words:
                if i - list(words).index(words[i-1]) > 2:
                    negation_active = False
        
        # Calculate sentiment
        total = pos_count + neg_count
        if total == 0:
            sentiment = 'neutral'
            confidence = 0.5
        else:
            pos_ratio = pos_count / total
            neg_ratio = neg_count / total
            
            if pos_ratio > neg_ratio:
                sentiment = 'positive'
                confidence = pos_ratio
            elif neg_ratio > pos_ratio:
                sentiment = 'negative'
                confidence = neg_ratio
            else:
                sentiment = 'neutral'
                confidence = 0.5
        
        # Adjust confidence based on intensity words
        intensity_words = {'very', 'extremely', 'incredibly', 'absolutely', 'completely'}
        intensity_count = sum(1 for w in words if w in intensity_words)
        confidence = min(0.99, confidence + (intensity_count * 0.05))
        
        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 3),
            'positive_words': pos_count,
            'negative_words': neg_count,
            'word_count': len(words)
        }

def get_sentiment_emoji(sentiment):
    """Return emoji based on sentiment."""
    return {
        'positive': '😊',
        'negative': '😞',
        'neutral': '😐'
    }.get(sentiment, '😐')

def get_sentiment_color(sentiment):
    """Return color based on sentiment."""
    return {
        'positive': '#28a745',
        'negative': '#dc3545',
        'neutral': '#ffc107'
    }.get(sentiment, '#ffc107')

# Initialize analyzer
analyzer = SentimentAnalyzer()

# Header
st.markdown('<h1 class="main-header">AI Sentiment Analyzer 😊😐😞</h1>', unsafe_allow_html=True)
st.markdown("""
    <p style="text-align: center; font-size: 1.2rem; color: #666;">
        Analyze the sentiment of any text using AI-powered natural language processing
    </p>
""", unsafe_allow_html=True)

st.divider()

# Create tabs
tab1, tab2 = st.tabs(["📝 Single Text Analysis", "📊 Batch Analysis"])

with tab1:
    # Text input
    st.subheader("Enter text to analyze")
    text_input = st.text_area(
        "Type or paste your text here:",
        height=150,
        placeholder="Example: I absolutely love this product! It's amazing and works perfectly..."
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        analyze_button = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)
    
    if analyze_button and text_input:
        result = analyzer.analyze(text_input)
        
        # Display results
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            emoji = get_sentiment_emoji(result['sentiment'])
            color = get_sentiment_color(result['sentiment'])
            st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: {color}20; border-radius: 10px;">
                    <div style="font-size: 4rem;">{emoji}</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {color}; text-transform: uppercase;">
                        {result['sentiment']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Confidence", f"{result['confidence']*100:.1f}%")
            st.metric("Word Count", result['word_count'])
        
        with col3:
            st.metric("Positive Words", result['positive_words'])
            st.metric("Negative Words", result['negative_words'])
        
        # Confidence gauge
        st.subheader("Confidence Visualization")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result['confidence'] * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 33], 'color': '#ffcccc'},
                    {'range': [33, 66], 'color': '#ffffcc'},
                    {'range': [66, 100], 'color': '#ccffcc'}
                ],
                'threshold': {
                    'line': {'color': 'black', 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Batch Analysis (Demo Mode)")
    st.info("📁 In a full implementation, this would allow CSV uploads for batch processing")
    
    # Demo batch data
    demo_texts = [
        "I love this product! It's absolutely amazing!",
        "This is the worst experience I've ever had.",
        "The product is okay, nothing special.",
        "Fantastic quality and great customer service!",
        "Terrible waste of money, very disappointed."
    ]
    
    if st.button("📊 Run Demo Batch Analysis", type="primary"):
        results = []
        for text in demo_texts:
            result = analyzer.analyze(text)
            result['text'] = text[:50] + "..." if len(text) > 50 else text
            results.append(result)
        
        # Display results table
        import pandas as pd
        df = pd.DataFrame(results)
        df['confidence'] = df['confidence'].apply(lambda x: f"{x*100:.1f}%")
        st.dataframe(df[['text', 'sentiment', 'confidence', 'positive_words', 'negative_words']], 
                     use_container_width=True)
        
        # Sentiment distribution chart
        sentiment_counts = df['sentiment'].value_counts()
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            color=sentiment_counts.index,
            color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#ffc107'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This sentiment analyzer uses a combination of:
    - **Rule-based analysis** with curated word lists
    - **Negation handling** to understand context
    - **Intensity detection** for stronger sentiments
    
    ### How it works:
    1. Text is preprocessed and tokenized
    2. Positive and negative words are counted
    3. Negation words flip sentiment context
    4. Confidence is calculated based on word ratios
    
    ### Limitations:
    - Simpler than deep learning models
    - May miss complex sarcasm
    - Limited vocabulary coverage
    """)
    
    st.divider()
    
    st.header("📊 Example Texts")
    st.markdown("""
    Try these examples:
    
    **Positive:**
    - "I absolutely love this! Best purchase ever!"
    - "Fantastic service and amazing quality!"
    
    **Negative:**
    - "Terrible experience, would not recommend"
    - "Complete waste of money, very disappointed"
    
    **Neutral:**
    - "The product arrived on time as expected"
    - "It's an average product for the price"
    """)

# Footer
st.divider()
st.markdown("""
    <p style="text-align: center; color: #666;">
        Built with ❤️ using Streamlit | Part of the AI Portfolio
    </p>
""", unsafe_allow_html=True)
