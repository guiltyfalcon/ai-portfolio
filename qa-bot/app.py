"""
QA Bot - A smart question-answering chatbot powered by OpenAI GPT.
"""

import streamlit as st
import openai
from streamlit_chat import message
import os

# Page configuration
st.set_page_config(
    page_title="QA Bot - Smart Q&A",
    page_icon="💬",
    layout="centered"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTextInput input {
        border-radius: 20px;
    }
    .token-info {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def get_api_key():
    """Get OpenAI API key from environment or secrets."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    return api_key


def init_session_state():
    """Initialize session state variables."""
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {"role": "system", "content": "You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and concise answers to questions."}
        ]
    if 'total_tokens' not in st.session_state:
        st.session_state['total_tokens'] = 0


def generate_response(prompt, model, temperature):
    """Generate a response from OpenAI API."""
    api_key = get_api_key()
    if not api_key:
        return "Please set your OpenAI API key in environment variables or Streamlit secrets.", 0
    
    client = openai.OpenAI(api_key=api_key)
    
    # Add user message to context
    st.session_state['messages'].append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state['messages'],
            temperature=temperature,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Add assistant response to context
        st.session_state['messages'].append({"role": "assistant", "content": answer})
        st.session_state['total_tokens'] += tokens_used
        
        return answer, tokens_used
    except Exception as e:
        return f"Error: {str(e)}", 0


def main():
    # Header
    st.markdown('&lt;div class="main-header"&gt;💬 QA Bot&lt;/div&gt;', unsafe_allow_html=True)
    st.markdown('&lt;div class="subtitle"&gt;Your smart AI-powered question answering companion&lt;/div&gt;', unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        model = st.selectbox(
            "Choose Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            help="Select the GPT model for responses"
        )
        
        # Temperature slider
        temperature = st.slider(
            "Response Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher = more creative, Lower = more focused"
        )
        
        # System prompt
        system_prompt = st.text_area(
            "System Behavior",
            value="You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and concise answers to questions.",
            height=100,
            help="Define how the AI should behave"
        )
        
        if st.button("Clear Chat History", type="secondary"):
            st.session_state['generated'] = []
            st.session_state['past'] = []
            st.session_state['messages'] = [
                {"role": "system", "content": system_prompt}
            ]
            st.session_state['total_tokens'] = 0
            st.rerun()
        
        # Token usage
        st.markdown("---")
        st.metric("Total Tokens Used", st.session_state['total_tokens'])
    
    # Update system message if changed
    if st.session_state['messages'][0]['content'] != system_prompt:
        st.session_state['messages'][0]['content'] = system_prompt
    
    # Display chat history
    if st.session_state['past']:
        for i, (user_msg, bot_msg) in enumerate(zip(st.session_state['past'], st.session_state['generated'])):
            message(user_msg, is_user=True, key=f"user_{i}")
            message(bot_msg, key=f"bot_{i}")
    
    # Chat input
    prompt = st.chat_input("Ask me anything...")
    
    if prompt:
        with st.spinner("Thinking..."):
            output, tokens = generate_response(prompt, model, temperature)
        
        # Store the output
        st.session_state['past'].append(prompt)
        st.session_state['generated'].append(output)
        
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("&lt;div style='text-align: center; color: #999;'&gt;Powered by OpenAI GPT 💪&lt;/div&gt;", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
