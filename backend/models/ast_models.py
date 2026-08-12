# backend/models/ast_models.py
from pydantic import BaseModel
from typing import Optional

class FunctionInfo(BaseModel):
    name: str
    file_path: str
    start_line: int
    end_line: int
    arguments: list[str]
    decorators: list[str]
    docstring: Optional[str] = None
    is_method: bool = False          # true if defined inside a class
    parent_class: Optional[str] = None
    is_async: bool = False

class ClassInfo(BaseModel):
    name: str
    file_path: str
    start_line: int
    end_line: int
    base_classes: list[str]          # parent classes it inherits from
    docstring: Optional[str] = None
    method_names: list[str]

class ImportInfo(BaseModel):
    file_path: str
    line: int
    module: str                      # e.g. "os.path" or "requests"
    imported_names: list[str]        # e.g. ["join", "exists"] for "from os.path import join, exists"
    is_relative: bool = False
    level: int = 0                    # relative import level for "from ." / "from .."

class FileASTResult(BaseModel):
    file_path: str
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    imports: list[ImportInfo]
    parse_error: Optional[str] = None  # populated if the file had a syntax error
    raw_calls: list[dict] = []         # [{caller, callee, line}, ...] — used by Step 14's call graph
