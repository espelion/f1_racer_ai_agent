import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_key() -> str:
    return GEMINI_API_KEY
