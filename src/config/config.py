import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_PRIVATE_KEY = os.getenv("LANGFUSE_PRIVATE_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

MONGODB_URI = os.getenv("MONGODB_URI")
DB = os.getenv("DB")
ECC_COLLECTION = os.getenv("ECC_COLLECTION")