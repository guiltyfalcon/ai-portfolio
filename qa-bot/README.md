# 💬 QA Bot

**Smart Question-Answering Chatbot with Context Awareness**

An intelligent Q&A assistant powered by OpenAI GPT that maintains conversation history and provides accurate, context-aware answers.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai)

---

## 🎯 Overview

QA Bot is a conversational AI assistant that answers questions across any topic while maintaining context from previous messages. Unlike simple chatbots, it remembers what you've discussed and builds on earlier responses.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Context Awareness** | Remembers conversation history for coherent multi-turn dialogue |
| **Multi-Topic Support** | Answer questions about anything - science, history, tech, etc. |
| **Clear Formatting** | Well-structured responses with headings, lists, and code blocks |
| **Conversation History** | View and scroll through entire chat session |
| **Copy Responses** | One-click copy for easy sharing |
| **Clear Chat** | Start fresh conversations when needed |
| **Customizable Personality** | Adjust response style and expertise level |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/qa-bot

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

**User:** "What is quantum computing?"

**Bot:** Explains quantum computing basics with qubits, superposition, and potential applications.

---

**User:** "How does that compare to classical computers?"

**Bot:** Builds on previous answer, comparing bits vs qubits and computational advantages.

---

**User:** "Can you give me a Python example?"

**Bot:** Provides code example using Qiskit or similar quantum computing library.

---

## 🏗️ Architecture

```
qa-bot/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
└── .streamlit/
    └── secrets.toml           # API keys (create this)
```

---

## ⚙️ How It Works

### Context Management

1. **Message Storage** - Each user message and bot response is stored
2. **Context Window** - Last N messages sent to GPT for context
3. **System Prompt** - Defines bot personality and behavior
4. **Token Management** - Truncates old messages to stay within limits

### Response Generation

1. User submits question
2. App builds context from conversation history
3. Request sent to OpenAI GPT API
4. Response displayed and added to history
5. Context updated for next turn

---

## 🎛️ Configuration Options

### Model Selection

Edit `app.py` to change the GPT model:

```python
model = "gpt-3.5-turbo"     # Fast, affordable
# model = "gpt-4"           # More capable, higher cost
# model = "gpt-4-turbo"     # Latest GPT-4 version
```

### Context Length

Adjust how many previous messages are remembered:

```python
max_context_messages = 10  # Remember last 10 messages
```

### System Prompt

Customize the bot's personality:

```python
system_prompt = """You are a helpful, knowledgeable assistant. 
Provide clear, accurate answers with appropriate detail."""
```

---

## 💡 Use Cases

| Use Case | Example |
|----------|---------|
| **Learning Assistant** | Ask questions about any topic you're studying |
| **Research Helper** | Get explanations of complex concepts |
| **Code Helper** | Programming questions and debugging |
| **Writing Assistant** | Improve documents, check grammar |
| **General Knowledge** | Quick answers to curiosity questions |
| **Interview Prep** | Practice Q&A for job interviews |

---

## 💰 Cost Estimate

Using GPT-3.5-turbo:
- ~$0.001-0.005 per conversation turn
- 100 questions ≈ $0.10-0.50

Very affordable for personal use!

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Add OPENAI_API_KEY to secrets.toml |
| Responses cut off | Model hit token limit; ask more specific questions |
| Forgetting context | Increase max_context_messages in app.py |
| Rate limit errors | Wait a moment between requests |

---

## 🔮 Future Enhancements

- [ ] Document upload (PDF, TXT) for Q&A over your files
- [ ] Web search integration for current information
- [ ] Multiple conversation threads
- [ ] Export conversations to PDF/Markdown
- [ ] Voice input/output support
- [ ] Custom knowledge base integration
- [ ] Response caching for common questions

---

## 📝 License

MIT License — Feel free to use and modify.

---

## 🙏 Credits

- **OpenAI** - GPT language model
- **Streamlit** - Web application framework

---

Part of the [AI Portfolio](../) collection.
