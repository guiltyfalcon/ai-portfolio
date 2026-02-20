# 🖼️ Image Classifier

Deep learning image classification application using TensorFlow/Keras and MobileNetV2.

## Features

- 🖼️ Drag-and-drop image upload
- 🔍 Instant classification into 1000+ categories
- 📊 Confidence scores with visual bars
- 🏷️ Top-5 predictions display
- 📱 Mobile-friendly interface

## Demo

**Live App:** [Coming Soon - Deploy to Streamlit Cloud]

## Tech Stack

- Python 3.11+
- Streamlit
- TensorFlow/Keras
- MobileNetV2 (pre-trained)
- Pillow (image processing)

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New App"
3. Select repository and branch
4. Set main file: `image-classifier/app.py`
5. Deploy!

**Note:** First deployment may take 3-5 minutes as TensorFlow downloads.

## How It Works

1. **Image Upload:** User uploads image via drag-and-drop
2. **Preprocessing:** Image resized to 224x224 for MobileNetV2
3. **Inference:** Model predicts image category
4. **Results:** Top-5 predictions with confidence scores

## Model Details

- **Architecture:** MobileNetV2
- **Dataset:** ImageNet (1000 categories)
- **Input Size:** 224x224 pixels
- **Top-1 Accuracy:** ~72%
- **Top-5 Accuracy:** ~91%

## Example Categories

- Animals (dog breeds, cat breeds, wildlife)
- Vehicles (cars, airplanes, boats)
- Objects (furniture, electronics, instruments)
- Food (pizza, sushi, ice cream)
- And 900+ more!

---

Part of the [AI Portfolio](../)
