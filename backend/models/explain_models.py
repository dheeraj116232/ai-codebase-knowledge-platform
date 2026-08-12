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

class FunctionExplanationRequest(BaseModel):
    repo_name: str
    file_path: str
    function_name: str

class FunctionExplanationResponse(BaseModel):
    function_name: str
    file_path: str
    start_line: int
    end_line: int
    signature: str                  # e.g. "def login(username, password)"
    purpose: str                    # AI-generated
    parameters_explained: str       # AI-generated
    returns_explained: str          # AI-generated
    flow_summary: str               # AI-generated step-by-step
    calls_made: list[str]           # from Step 14's call graph — functions this one calls
    called_by: list[str]            # from Step 14 — functions that call this one