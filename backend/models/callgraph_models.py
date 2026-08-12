# backend/models/callgraph_models.py
from pydantic import BaseModel

class FunctionCall(BaseModel):
    caller_function: str        # e.g. "login"
    caller_file: str
    callee_name: str            # the name being called, e.g. "verify_password"
    call_line: int
    resolved: bool               # True if we matched it to a known function in the repo
    callee_file: str | None = None   # populated only if resolved

class CallGraphResult(BaseModel):
    repo_name: str
    total_calls_found: int
    total_resolved: int
    total_unresolved: int
    calls: list[FunctionCall]
    most_called_functions: list[dict]   # [{"function": "get_db", "file": "db.py", "call_count": 8}]