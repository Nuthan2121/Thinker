from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found. Set it in your .env file.")
