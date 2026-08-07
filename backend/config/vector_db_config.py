# backend/config/vector_db_config.py
import os
from dotenv import load_dotenv

load_dotenv()

# "local" for development, "cloud" for production (Chroma Cloud)
CHROMA_MODE = os.getenv("CHROMA_MODE", "local")

CHROMA_LOCAL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "chroma_data"
)

# Only needed when CHROMA_MODE = "cloud"
CHROMA_CLOUD_API_KEY = os.getenv("CHROMA_CLOUD_API_KEY", "")
CHROMA_CLOUD_TENANT = os.getenv("CHROMA_CLOUD_TENANT", "")
CHROMA_CLOUD_DATABASE = os.getenv("CHROMA_CLOUD_DATABASE", "")

COLLECTION_NAME = "code_chunks"