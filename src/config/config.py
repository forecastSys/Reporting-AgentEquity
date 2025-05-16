import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")