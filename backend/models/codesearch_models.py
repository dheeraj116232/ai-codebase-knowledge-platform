# backend/models/codesearch_models.py
from pydantic import BaseModel

class CodeSearchRequest(BaseModel):
    query: str
    repo_name: str
    max_results: int = 20

class FileMatch(BaseModel):
    file_path: str
    match_type: str          # "filename" | "function_name" | "class_name"
    matched_name: str
    line: int | None = None

class SemanticMatch(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    content_preview: str
    relevance_score: float

class CodeSearchResponse(BaseModel):
    query: str
    exact_matches: list[FileMatch]
    semantic_matches: list[SemanticMatch]
    total_results: int