import streamlit as st
import openai
import os

# Page setup
st.set_page_config(page_title="AI Fitness Chatbot", page_icon="💪", layout="centered")
st.title("💪 AI Fitness Chatbot")
st.subheader("Get personalized fitness & nutrition advice")

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your AI fitness assistant. Ask me about workouts, nutrition, or fitness goals!"}
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask me anything about fitness..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable fitness and nutrition coach. Provide helpful, safe, and evidence-based advice."},
                    *st.session_state.messages
                ],
                stream=True,
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.get("content"):
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"I apologize, I'm having trouble connecting. Error: {str(e)}"
            message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar info
st.sidebar.title("About")
st.sidebar.info("""
This AI chatbot provides fitness and nutrition guidance using OpenAI's GPT model.

**Features:**
• Personalized workout advice
• Nutrition recommendations
• Goal setting help
• Evidence-based information

**Disclaimer:** This is for informational purposes. Consult a doctor before starting any exercise program.
""")

st.sidebar.title("Setup")
st.sidebar.code("""
# Install requirements
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-key-here'

# Run app
streamlit run app.py
""")