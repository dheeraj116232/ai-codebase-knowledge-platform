# backend/models/diagram_models.py
from pydantic import BaseModel

class DiagramResult(BaseModel):
    repo_name: str
    mermaid_syntax: str
    node_count: int
    edge_count: int
    was_reduced: bool
    original_node_count: int
    caption: str | None = None