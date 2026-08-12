# backend/models/graph_models.py
from pydantic import BaseModel

class DependencyEdge(BaseModel):
    source_file: str        # the file that has the import
    target_file: str        # the resolved internal file, OR the external package name
    is_external: bool       # True if target isn't a file in this repo (e.g. "requests", "react")
    import_line: int

class DependencyGraphResult(BaseModel):
    repo_name: str
    total_files: int
    total_internal_edges: int
    total_external_dependencies: int
    edges: list[DependencyEdge]
    most_depended_on: list[dict]     # [{"file": "utils.py", "dependent_count": 12}, ...]
    external_packages: list[str]     # deduplicated list, e.g. ["requests", "flask", "os"]