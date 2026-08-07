# backend/config/llm_config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# llama-3.3-70b-versatile: strong reasoning, good for explaining code
# llama-3.1-8b-instant: much faster/cheaper, weaker reasoning — good fallback for simple queries
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

MAX_CONTEXT_CHUNKS = 6          # cap how many retrieved chunks go into the prompt
MAX_TOKENS_RESPONSE = 1024
TEMPERATURE = 0.2               # low temperature — factual code explanation, not creative writing