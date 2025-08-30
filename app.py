import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from textblob import TextBlob
import json

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

# Inject custom CSS for background color (or background image)
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8ff;  /* Light Alice Blue color */
        /* For background image, uncomment the line below and provide the URL of your image */
        /* background-image: url('https://path_to_your_image.jpg'); */
        /* background-size: cover; */
        /* background-position: center center; */
        /* background-attachment: fixed; */
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Sentiment analysis function
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
    if sentiment > 0:
        return "Positive", sentiment
    elif sentiment < 0:
        return "Negative", sentiment
    else:
        return "Neutral", sentiment

# Model selection in the sidebar
selected_model = st.sidebar.selectbox("Choose Model", ["Gemini Pro", "Gemini Flash"])

# Handle user input and generate response
if prompt:
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    # Analyze sentiment of the user input
    sentiment_label, sentiment_score = analyze_sentiment(prompt)
    st.sidebar.write(f"Sentiment: {sentiment_label} ({sentiment_score:.2f})")

    with st.spinner(f"🤖 {selected_model} is thinking..."):
        model_used = selected_model
        try:
            if model_used == "Gemini Pro":
                response = model_pro.generate_content(
                    prompt,
                    generation_config={"temperature": temperature}
                )
            else:
                response = model_flash.generate_content(
                    prompt,
                    generation_config={"temperature": temperature}
                )
            reply = response.text
        except Exception as e:
            reply = f"❌ Error: {e}"
            st.error(reply)

    # Display assistant message if success
    if not reply.startswith("❌"):
        reply += f"\n\n*Response from {model_used}*"
        st.chat_message("assistant").markdown(reply)

    # Save assistant message to history
    st.session_state.history.append({"role": "assistant", "content": reply})

# Save chat history to a JSON file
def save_chat_history():
    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.history, f, indent=4)

# Add the save button to the sidebar
if st.sidebar.button("💾 Save Chat History"):
    save_chat_history()
    st.sidebar.success("Chat history saved as chat_history.json")
