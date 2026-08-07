# backend/models/file_models.py
from pydantic import BaseModel
from typing import Optional

class ParsedFile(BaseModel):
    path: str              # relative path, e.g. "src/auth/login.py"
    absolute_path: str     # full filesystem path
    extension: str         # ".py"
    language: str          # "python"
    size_bytes: int
    line_count: int
    content: Optional[str] = None  # populated only when needed (memory control)

class RepoParseResult(BaseModel):
    repo_name: str
    total_files_scanned: int
    total_files_included: int
    total_files_ignored: int
    files: list[ParsedFile]
    languages: dict[str, int]  # {"python": 40, "typescript": 12}