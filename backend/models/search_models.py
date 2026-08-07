# backend/models/search_models.py
from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    repo_name: str
    top_k: int = 5
    language_filter: Optional[str] = None   # e.g. "python" — optional narrowing

class SearchResultItem(BaseModel):
    chunk_id: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    content: str
    similarity_score: float   # 0 to 1, higher = more relevant

class SearchResponse(BaseModel):
    query: str
    repo_name: str
    results: list[SearchResultItem]
    result_count: int