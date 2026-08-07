# backend/models/chunk_models.py
from pydantic import BaseModel

class CodeChunk(BaseModel):
    chunk_id: str          # unique id, e.g. "auth.py::0"
    repo_name: str
    file_path: str         # relative path, e.g. "src/auth/login.py"
    language: str
    content: str
    start_line: int
    end_line: int
    chunk_index: int       # position within the file (0, 1, 2...)
    char_count: int