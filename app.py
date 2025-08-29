import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate API key
if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in environment variables.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Load models
model_pro = genai.GenerativeModel("models/gemini-1.5-pro-latest")
model_flash = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Streamlit page config
st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title("💬 Gemini Pro / Flash Chatbot with Auto-fallback")

# Sidebar: Temperature + Clear chat
temperature = st.sidebar.slider("🎛️ Creativity (Temperature)", 0.0, 1.0, 0.7)
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.history = []
    st.experimental_rerun()

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Display previous messages
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input (only one, with key!)
prompt = st.chat_input("Type your message here...", key="chat_input_main")

if prompt:
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.spinner("🤖 Gemini Pro is thinking..."):
        model_used = "Gemini Pro"
        try:
            response = model_pro.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            reply = response.text
        except Exception as e:
            if "429" in str(e):
                model_used = "Gemini Flash"
                st.warning("⚠️ Pro quota exceeded, switching to Flash...")
                try:
                    response = model_flash.generate_content(
                        prompt,
                        generation_config={"temperature": temperature}
                    )
                    reply = response.text
                except Exception as e2:
                    reply = f"❌ Error on Flash model too: {e2}"
                    st.error(reply)
            else:
                reply = f"❌ Error: {e}"
                st.error(reply)

    # Display assistant message if success
    if not reply.startswith("❌"):
        reply += f"\n\n*Response from {model_used}*"
        st.chat_message("assistant").markdown(reply)

    # Save assistant message to history
    st.session_state.history.append({"role": "assistant", "content": reply})
