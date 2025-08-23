import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in environment variables.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

model_pro = genai.GenerativeModel("models/gemini-1.5-pro-latest")
model_flash = genai.GenerativeModel("models/gemini-1.5-flash-latest")

st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title("💬 Gemini Pro / Flash Chatbot with Auto-fallback")

if "history" not in st.session_state:
    st.session_state.history = []

prompt = st.chat_input("Type your message here...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.spinner("🤖 Gemini Pro is thinking..."):
        try:
            response = model_pro.generate_content(prompt)
            reply = response.text
        except Exception as e:
            if "429" in str(e):
                st.warning("Pro quota exceeded, switching to Flash...")
                try:
                    response = model_flash.generate_content(prompt)
                    reply = response.text + "\n\n*Response from Gemini Flash*"
                except Exception as e2:
                    reply = f"❌ Error on Flash model too: {e2}"
            else:
                reply = f"❌ Error: {e}"

    st.chat_message("assistant").markdown(reply)
    st.session_state.history.append({"role": "assistant", "content": reply})
