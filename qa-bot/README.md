# 💬 QA Bot

Smart question-answering chatbot with conversation history and customizable AI behavior.

## Features

- 💬 Real-time chat interface
- 🧠 GPT-4 / GPT-4o-mini support
- 📝 Conversation history management
- ⚙️ Customizable system prompts
- 🔢 Token usage tracking
- 🎨 Modern, clean UI

## Demo

**Live App:** [Coming Soon - Deploy to Streamlit Cloud]

## Tech Stack

- Python 3.11+
- Streamlit
- OpenAI GPT-4 / GPT-4o-mini
- streamlit-chat (UI component)

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-key-here'

# Run app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New App"
3. Select repository and branch
4. Set main file: `qa-bot/app.py`
5. Add `OPENAI_API_KEY` to secrets
6. Deploy!

## API Key

Get your OpenAI API key at [platform.openai.com](https://platform.openai.com)

**Note:** Free tier includes $5 credit for new accounts.

## Customization

### System Prompts

Change the AI's behavior in the sidebar:

- **General Assistant:** Helpful, concise answers
- **Code Expert:** Programming-focused responses
- **Creative Writer:** Imaginative, detailed replies
- **Custom:** Define your own

### Model Selection

- **GPT-4:** Best quality, higher cost
- **GPT-4o-mini:** Fast, cost-effective

## Features in Detail

### Conversation History
- View full chat history
- Clear conversations
- Persistent in session

### Token Tracking
- Real-time token count
- Estimate API costs
- Monitor usage

### Message Interface
- User messages (right side)
- AI responses (left side)
- Timestamps included

---

Part of the [AI Portfolio](../)
