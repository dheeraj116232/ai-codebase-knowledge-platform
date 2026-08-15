# backend/scripts/memory_check.py — run manually, not part of the app
import psutil
import os

process = psutil.Process(os.getpid())

print(f"Baseline: {process.memory_info().rss / 1024 / 1024:.1f} MB")

from services.embedding_service import embedding_service
embedding_service.embed_texts(["test"])
print(f"After embedding model load: {process.memory_info().rss / 1024 / 1024:.1f} MB")

from services.rerank_service import rerank_service
from models.search_models import SearchResultItem
dummy = SearchResultItem(chunk_id="x", file_path="x", language="python",
                          start_line=1, end_line=1, content="test", similarity_score=0.5)
rerank_service.rerank("test query", [dummy], top_k=1)
print(f"After reranker load: {process.memory_info().rss / 1024 / 1024:.1f} MB")