# backend/config/rerank_config.py

RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
INITIAL_RETRIEVAL_K = 25    # broad recall stage
FINAL_TOP_K = 6             # what actually goes to Groq

import os

# Allow disabling reranking entirely via env var, without a code change
RERANKING_ENABLED = os.getenv("RERANKING_ENABLED", "true").lower() == "true"