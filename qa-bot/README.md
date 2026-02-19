# QA Bot

A smart question-answering chatbot powered by OpenAI's GPT models.

## Features

- Interactive chat interface with conversation history
- Persistent chat sessions
- Customizable system prompts
- Model selection (GPT-4, GPT-3.5)
- Temperature control for response creativity
- Token usage tracking

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-key-here"
```

3. Run the app:
```bash
streamlit run app.py
```

## Usage

- Type any question in the chat input
- Adjust settings in the sidebar (model, temperature, system prompt)
- Clear chat history with the sidebar button
- View token usage for each conversation

## Demo

<a href="https://qa-bot-demo.streamlit.app" target="_blank">Live Demo</a> - *coming soon*

## Technologies

- Python 3.8+
- Streamlit
- OpenAI API
- Streamlit Chat
