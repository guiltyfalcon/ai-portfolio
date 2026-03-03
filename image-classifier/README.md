# 🖼️ Image Classifier

**Deep Learning Image Classification with MobileNetV2**

Upload any image and get instant AI-powered classification with confidence scores for thousands of object categories.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow)

---

## 🎯 Overview

Image Classifier uses MobileNetV2, a lightweight deep learning model trained on ImageNet, to identify objects in images. Perfect for understanding what's in your photos, batch processing, or learning about computer vision.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Instant Classification** | Upload an image, get predictions in seconds |
| **Top-5 Predictions** | Shows top 5 most likely categories with confidence |
| **Confidence Visualization** | Clear bar charts showing prediction certainty |
| **ImageNet Categories** | 1,000+ object categories recognized |
| **Multiple Formats** | Supports JPG, PNG, GIF, WebP |
| **Batch Processing** | Upload multiple images at once |
| **Mobile-Optimized** | Fast inference with MobileNetV2 architecture |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/image-classifier

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

### MobileNetV2 Architecture

MobileNetV2 is a convolutional neural network designed for mobile and embedded devices:

- **Lightweight** - Only ~3.5 million parameters
- **Fast** - Optimized for quick inference
- **Accurate** - 72% top-1 accuracy on ImageNet
- **Pre-trained** - Already trained on 1.4M ImageNet images

### Classification Process

1. **Upload** - Select or drag-and-drop an image
2. **Preprocessing** - Resize to 224x224, normalize pixel values
3. **Inference** - MobileNetV2 processes the image
4. **Post-processing** - Convert outputs to probabilities
5. **Display** - Show top predictions with confidence scores

---

## 🖼️ Supported Categories

The model recognizes 1,000+ ImageNet categories including:

- **Animals** - Dogs, cats, birds, fish, insects
- **Objects** - Furniture, vehicles, electronics, tools
- **Food** - Fruits, vegetables, dishes, ingredients
- **Nature** - Plants, flowers, landscapes
- **People** - Clothing, accessories, activities
- **Sports** - Equipment, balls, athletic gear

---

## 🏗️ Architecture

```
image-classifier/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
└── .streamlit/
    └── config.toml            # Streamlit configuration
```

---

## 📸 Example Predictions

| Image | Top Prediction | Confidence |
|-------|---------------|------------|
| 🐕 Dog photo | "golden retriever" | 94% |
| 🍕 Pizza | "pizza" | 98% |
| 🚗 Car | "sports car" | 87% |
| 🌸 Flower | "cherry blossom" | 91% |

---

## ⚙️ Technical Details

### Dependencies

```
streamlit>=1.28.0
tensorflow>=2.13.0
numpy>=1.24.0
Pillow>=10.0.0
pandas>=2.0.0
```

### Model Details

| Property | Value |
|----------|-------|
| **Architecture** | MobileNetV2 |
| **Input Size** | 224x224 pixels |
| **Parameters** | ~3.5M |
| **Training Data** | ImageNet (1.4M images) |
| **Categories** | 1,000 classes |
| **Top-1 Accuracy** | 72.0% |
| **Top-5 Accuracy** | 90.3% |

---

## 💡 Use Cases

| Use Case | Example |
|----------|---------|
| **Photo Organization** | Auto-tag photos by content |
| **Quality Control** | Detect defects in products |
| **Accessibility** | Describe images for visually impaired |
| **Content Moderation** | Flag inappropriate images |
| **Inventory Management** | Identify products automatically |
| **Education** | Learn about objects and species |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Model loading slow | First run downloads model (~50MB) |
| Low confidence scores | Image may be unclear or category not in ImageNet |
| Upload fails | Check file format (JPG, PNG, GIF, WebP) |
| Import errors | Run `pip install -r requirements.txt` |

---

## 🔮 Future Enhancements

- [ ] Custom model training on your own categories
- [ ] Object detection (locate objects in image)
- [ ] Image segmentation
- [ ] Support for more models (EfficientNet, ResNet)
- [ ] Real-time camera classification
- [ ] Image similarity search
- [ ] Batch export of predictions

---

## 📝 License

MIT License — Feel free to use and modify.

---

## 🙏 Credits

- **TensorFlow** - Deep learning framework
- **MobileNetV2** - Pre-trained model by Google
- **ImageNet** - Training dataset
- **Streamlit** - Web application framework

---

Part of the [AI Portfolio](../) collection.
