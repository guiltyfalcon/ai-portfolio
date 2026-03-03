# 💪 Fitness Chatbot

**AI-Powered Personal Fitness & Nutrition Assistant**

A conversational AI assistant that provides personalized workout advice, nutrition recommendations, and fitness guidance powered by OpenAI GPT.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?logo=openai)

---

## 🎯 Overview

Fitness Chatbot is your 24/7 AI fitness coach. Whether you're looking to build muscle, lose weight, improve endurance, or just stay healthy, get instant personalized advice through natural conversation.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Personalized Workouts** | Custom workout plans based on your goals, equipment, and fitness level |
| **Nutrition Guidance** | Meal suggestions, macro calculations, and diet advice |
| **Goal Setting** | Help defining and tracking fitness goals |
| **Exercise Form Tips** | Proper technique explanations for any exercise |
| **Progression Advice** | How to increase weights, reps, and intensity safely |
| **Recovery Tips** | Rest day guidance, stretching, and injury prevention |
| **Conversation History** | Context-aware responses that remember your goals |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/fitness-chatbot

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file with your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

Or set as environment variable:
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

Get your API key at [platform.openai.com](https://platform.openai.com)

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 💬 Example Conversations

**User:** "I want to build muscle but I only have dumbbells at home"

**Bot:** Provides a complete dumbbell-only hypertrophy program with sets, reps, and progression scheme.

---

**User:** "What should I eat before a morning workout?"

**Bot:** Suggests pre-workout nutrition options based on timing, goals, and dietary preferences.

---

**User:** "How do I improve my pull-ups? I can only do 2"

**Bot:** Provides a progressive overload plan with assisted variations and complementary exercises.

---

## 🏗️ Architecture

```
fitness-chatbot/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
└── .streamlit/
    └── secrets.toml           # API keys (create this)
```

---

## 🧠 How It Works

1. **User Input** - You type a fitness/nutrition question
2. **Context Building** - App includes conversation history and your stated goals
3. **GPT Processing** - OpenAI generates personalized, expert-level advice
4. **Response Display** - Formatted response with actionable recommendations

The AI is trained on fitness literature, exercise science, and nutrition research to provide evidence-based guidance.

---

## ⚙️ Configuration Options

### Model Selection

Edit `app.py` to change the GPT model:

```python
model = "gpt-3.5-turbo"  # Fast and cost-effective
# model = "gpt-4"        # More detailed responses (higher cost)
```

### System Prompt

Customize the AI's personality and expertise by modifying the system prompt in `app.py`.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Add OPENAI_API_KEY to secrets.toml or environment |
| "Rate limit exceeded" | Wait a moment, or upgrade your OpenAI plan |
| Response seems generic | Provide more context about your specific situation |
| App won't start | Run `pip install -r requirements.txt` |

---

## ⚠️ Disclaimer

This chatbot provides **informational guidance only** and is not a substitute for:
- Professional medical advice
- Certified personal training
- Registered dietitian consultation

**Always consult a healthcare provider** before starting any new exercise or nutrition program, especially if you have pre-existing conditions.

---

## 💰 Cost Estimate

Using GPT-3.5-turbo:
- ~$0.002 per conversation
- 100 conversations ≈ $0.20

Very affordable for personal use!

---

## 🔮 Future Enhancements

- [ ] User profiles with saved goals and preferences
- [ ] Workout logging and progress tracking
- [ ] Image recognition for form checks
- [ ] Integration with fitness trackers (Fitbit, Apple Watch)
- [ ] Meal planning with grocery lists
- [ ] Video exercise demonstrations

---

## 📝 License

MIT License — Feel free to use and modify.

---

## 🙏 Credits

- **OpenAI** - GPT language model
- **Streamlit** - Web application framework

---

Part of the [AI Portfolio](../) collection.
