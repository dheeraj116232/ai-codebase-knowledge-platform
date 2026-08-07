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
    is_method: bool = False
    parent_class: Optional[str] = None
    is_async: bool = False

class ClassInfo(BaseModel):
    name: str
    file_path: str
    start_line: int
    end_line: int
    base_classes: list[str]
    docstring: Optional[str] = None
    method_names: list[str]

class ImportInfo(BaseModel):
    file_path: str
    line: int
    module: str
    imported_names: list[str]
    is_relative: bool = False

class FileASTResult(BaseModel):
    file_path: str
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    imports: list[ImportInfo]
    parse_error: Optional[str] = None
    raw_calls: list[dict] = []