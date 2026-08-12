# backend/services/callgraph_service.py
import ast
from models.callgraph_models import FunctionCall
from models.ast_models import FunctionInfo
from models.ast_models import FileASTResult
from models.callgraph_models import FunctionCall, CallGraphResult
import networkx as nx
class CallVisitor(ast.NodeVisitor):
    """Walks a single function's body and records every call expression inside it."""

    def __init__(self, caller_name: str, caller_file: str):
        self.caller_name = caller_name
        self.caller_file = caller_file
        self.calls: list[FunctionCall] = []

    def visit_Call(self, node):
        callee_name = self._extract_callee_name(node.func)
        if callee_name:
            self.calls.append(FunctionCall(
                caller_function=self.caller_name,
                caller_file=self.caller_file,
                callee_name=callee_name,
                call_line=node.lineno,
                resolved=False,   # resolution happens in a second pass, see step 4
            ))
        self.generic_visit(node)  # keep walking — catches nested/chained calls too

    def _extract_callee_name(self, func_node) -> str | None:
        # Simple call: foo()
        if isinstance(func_node, ast.Name):
            return func_node.id
        # Method/attribute call: obj.foo() -> we record "foo", the object is unknown statically
        if isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None


def extract_calls_from_function(function_source_ast_node, caller_name: str, caller_file: str) -> list[FunctionCall]:
    visitor = CallVisitor(caller_name, caller_file)
    visitor.visit(function_source_ast_node)
    return visitor.calls


def build_call_graph(ast_results: list[FileASTResult], repo_name: str) -> CallGraphResult:
    # Build a lookup: function name -> list of (file, FunctionInfo) that define it
    # (a name can map to multiple functions across the repo — duplicates are expected)
    name_to_definitions: dict[str, list[str]] = {}
    for result in ast_results:
        for func in result.functions:
            name_to_definitions.setdefault(func.name, []).append(result.file_path)

    all_calls: list[FunctionCall] = []

    for result in ast_results:
        for raw_call in getattr(result, "raw_calls", []):
            callee_name = raw_call["callee"]
            candidates = name_to_definitions.get(callee_name, [])

            # If exactly one function in the repo has this name, we resolve with confidence.
            # If multiple, we still record it but flag ambiguity by picking the first
            # and noting resolved=True only for the unambiguous case — a deliberate,
            # documented simplification rather than guessing silently.
            resolved = len(candidates) == 1
            callee_file = candidates[0] if resolved else None

            all_calls.append(FunctionCall(
                caller_function=raw_call["caller"],
                caller_file=result.file_path,
                callee_name=callee_name,
                call_line=raw_call["line"],
                resolved=resolved,
                callee_file=callee_file,
            ))

    # Most-called functions = highest frequency as a callee, among resolved calls
    call_counts: dict[str, int] = {}
    for c in all_calls:
        if c.resolved:
            key = f"{c.callee_name} ({c.callee_file})"
            call_counts[key] = call_counts.get(key, 0) + 1

    most_called = sorted(call_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    most_called_functions = [{"function": k, "call_count": v} for k, v in most_called]

    resolved_count = sum(1 for c in all_calls if c.resolved)

    return CallGraphResult(
        repo_name=repo_name,
        total_calls_found=len(all_calls),
        total_resolved=resolved_count,
        total_unresolved=len(all_calls) - resolved_count,
        calls=all_calls,
        most_called_functions=most_called_functions,
    )
    
def build_call_graph_networkx(call_result: CallGraphResult) -> nx.DiGraph:
    graph = nx.DiGraph()
    for call in call_result.calls:
        if not call.resolved:
            continue
        caller_id = f"{call.caller_file}::{call.caller_function}"
        callee_id = f"{call.callee_file}::{call.callee_name}"
        graph.add_edge(caller_id, callee_id, line=call.call_line)
    return graph