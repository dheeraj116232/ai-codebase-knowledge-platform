# backend/models/explain_models.py
from pydantic import BaseModel

class FileExplanationRequest(BaseModel):
    repo_name: str
    file_path: str

class FileExplanationResponse(BaseModel):
    file_path: str
    language: str
    summary: str                    # AI-generated purpose paragraph
    function_count: int
    class_count: int
    functions: list[str]            # names, for quick display
    classes: list[str]
    internal_dependencies: list[str]   # files this file imports
    dependents: list[str]              # files that import this file
    external_dependencies: list[str]   # 3rd-party packages used