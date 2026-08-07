# backend/config/chunk_config.py

CHUNK_SIZE = 1000        # characters per chunk
CHUNK_OVERLAP = 150      # overlap between consecutive chunks

# Map our internal language labels to LangChain's Language enum
from langchain_text_splitters import Language

LANGCHAIN_LANGUAGE_MAP = {
    "python": Language.PYTHON,
    "javascript": Language.JS,
    "typescript": Language.TS,
    "java": Language.JAVA,
    "go": Language.GO,
    "rust": Language.RUST,
    "cpp": Language.CPP,
    "c": Language.CPP,   # LangChain has no separate C enum; CPP separators work reasonably
    "markdown": Language.MARKDOWN,
}