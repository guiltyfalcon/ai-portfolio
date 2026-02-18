# AI Image Classifier 🖼️🤖

A deep learning image classification application using TensorFlow/Keras and a pre-trained MobileNetV2 model. Classify images into 1000+ ImageNet categories.

## 🎯 Features

- **Drag & Drop Interface**: Easy image upload via web UI
- **Real-time Classification**: Instant predictions with confidence scores
- **Top-K Predictions**: See top 5 most likely categories
- **Pre-trained Model**: Uses MobileNetV2 trained on ImageNet
- **Transfer Learning Script**: Fine-tune on custom datasets

## 🚀 Demo

**Live Demo:** [Coming soon - Deploying to Streamlit Cloud]

**Example Output:**
```
Image: golden_retriever.jpg

Top Predictions:
1. Golden Retriever - 98.4% 🐕
2. Labrador Retriever - 1.1%
3. Chesapeake Bay Retriever - 0.3%
4. Flat-Coated Retriever - 0.1%
5. Curly-Coated Retriever - 0.05%
```

## 💻 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/image-classifier

# Install dependencies
pip install -r requirements.txt

# Download pre-trained model (optional - auto-downloads on first run)
python download_model.py

# Run the app
streamlit run app.py
```

## 🛠️ Tech Stack

- **Streamlit** - Web framework for the UI
- **TensorFlow/Keras** - Deep learning framework
- **MobileNetV2** - Pre-trained CNN architecture
- **Pillow** - Image processing
- **NumPy** - Numerical operations

## 📊 How It Works

1. **Image Preprocessing**: Resize to 224x224, normalize pixel values
2. **Feature Extraction**: MobileNetV2 extracts image features
3. **Classification**: Dense layer outputs 1000 class probabilities
4. **Post-processing**: Apply softmax, get top-k predictions

## 🏋️‍♂️ Example Usage

**Single Image Classification:**
```python
from image_classifier import ImageClassifier

classifier = ImageClassifier()
results = classifier.predict('path/to/image.jpg')
print(results)
# [{'label': 'golden_retriever', 'confidence': 0.984, 'name': 'Golden Retriever'}, ...]
```

**Transfer Learning:**
```python
# Fine-tune on custom dataset
classifier.train_custom(
    train_dir='data/train',
    val_dir='data/val',
    epochs=10,
    learning_rate=0.0001
)
```

## 📈 Model Performance

- **Base Model**: MobileNetV2 (ImageNet)
- **Top-1 Accuracy**: 71.3% on ImageNet
- **Top-5 Accuracy**: 90.1% on ImageNet
- **Inference Time**: ~50ms per image (CPU)
- **Model Size**: 14MB

## 🔒 Privacy & Security

- All image processing happens locally
- No images are uploaded to external servers
- Model runs entirely on your machine

## 📈 Future Improvements

- [ ] Custom model training UI
- [ ] Object detection capabilities
- [ ] Batch image processing
- [ ] Model quantization for faster inference
- [ ] Support for custom class labels

## 🤝 Contributing

This is a demonstration project for portfolio purposes. Feel free to fork and expand!

---

*Built as part of an AI portfolio by guiltyfalcon*
