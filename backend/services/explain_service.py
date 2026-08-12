import re

from services.dependency_resolver import (
    resolve_python_import,
    resolve_js_import,
)
from config.llm_config import GROQ_MODEL, TEMPERATURE
from services.groq_service import get_groq_client
from services.prompt_builder import (
    FILE_EXPLANATION_SYSTEM_PROMPT,
    build_file_explanation_prompt,
)
from models.ast_models import FileASTResult, FunctionInfo
from models.explain_models import FileExplanationResponse


def gather_file_context(
    file_path: str,
    ast_results: list[FileASTResult],
    dependency_graph,
) -> dict | None:
    """Gather AST and dependency information for a file."""

    normalized_file_path = file_path.replace("\\", "/")

    file_ast = next(
        (
            r
            for r in ast_results
            if r.file_path.replace("\\", "/") == normalized_file_path
        ),
        None,
    )

    if file_ast is None:
        return None

    all_file_paths = {
        r.file_path.replace("\\", "/")
        for r in ast_results
    }

    ext = (
        normalized_file_path.rsplit(".", 1)[-1]
        if "." in normalized_file_path
        else ""
    )

    internal_deps = []
    external_deps = set()

    for imp in file_ast.imports:
        resolved = None

        if ext == "py":
            resolved = resolve_python_import(
                imp.module,
                imp.is_relative,
                normalized_file_path,
                all_file_paths,
                imported_names=getattr(imp, "imported_names", None),
                level=getattr(imp, "level", 0),
            )

        elif ext in ("js", "jsx", "ts", "tsx"):
            resolved = resolve_js_import(
                imp.module,
                normalized_file_path,
                all_file_paths,
            )

        if resolved:
            internal_deps.append(resolved)
        else:
            module_name = imp.module

            if not module_name:
                imported_names = getattr(
                    imp,
                    "imported_names",
                    [],
                )
                module_name = ", ".join(imported_names)

            if module_name:
                external_deps.add(module_name)

    dependents = []

    if dependency_graph and normalized_file_path in dependency_graph:
        dependents = list(
            dependency_graph.predecessors(normalized_file_path)
        )

    return {
        "file_path": normalized_file_path,
        "language": ext,
        "functions": file_ast.functions,
        "classes": file_ast.classes,
        "internal_deps": sorted(set(internal_deps)),
        "external_deps": sorted(external_deps),
        "dependents": dependents,
    }


def explain_file(
    file_path: str,
    ast_results: list[FileASTResult],
    dependency_graph,
) -> FileExplanationResponse:
    """Generate an AI explanation for a file."""

    context = gather_file_context(
        file_path,
        ast_results,
        dependency_graph,
    )

    if context is None:
        raise ValueError(
            f"File not found in analyzed results: {file_path}"
        )

    client = get_groq_client()

    prompt = build_file_explanation_prompt(context)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": FILE_EXPLANATION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=TEMPERATURE,
        max_tokens=300,
    )

    summary = response.choices[0].message.content or ""

    return FileExplanationResponse(
        file_path=context["file_path"],
        language=context["language"],
        summary=summary,
        function_count=len(context["functions"]),
        class_count=len(context["classes"]),
        functions=[
            f.name
            for f in context["functions"]
        ],
        classes=[
            c.name
            for c in context["classes"]
        ],
        internal_dependencies=context["internal_deps"],
        dependents=context["dependents"],
        external_dependencies=context["external_deps"],
    )


def extract_function_source(
    file_content: str,
    start_line: int,
    end_line: int,
) -> str:
    """Extract exact source lines for a function."""

    lines = file_content.splitlines()

    function_lines = lines[
        start_line - 1:end_line
    ]

    return "\n".join(function_lines)


def find_function(
    file_ast: FileASTResult,
    function_name: str,
) -> FunctionInfo | None:
    """Find a function by name."""

    return next(
        (
            f
            for f in file_ast.functions
            if f.name == function_name
        ),
        None,
    )


def gather_function_context(
    repo_name: str,
    file_path: str,
    function_name: str,
    ast_results: list[FileASTResult],
    file_content: str,
    call_graph_result,
) -> dict | None:
    """Gather source and call-graph context for a function."""

    file_ast = next(
        (
            r
            for r in ast_results
            if r.file_path.replace("\\", "/")
            == file_path.replace("\\", "/")
        ),
        None,
    )

    if file_ast is None:
        return None

    func = find_function(
        file_ast,
        function_name,
    )

    if func is None:
        return None

    source_code = extract_function_source(
        file_content,
        func.start_line,
        func.end_line,
    )

    calls_made = []
    called_by = []

    if call_graph_result:
        calls_made = [
            c.callee_name
            for c in call_graph_result.calls
            if (
                c.caller_function == function_name
                and c.caller_file == file_path
                and c.resolved
            )
        ]

        called_by = [
            c.caller_function
            for c in call_graph_result.calls
            if (
                c.callee_name == function_name
                and c.callee_file == file_path
            )
        ]

    return {
        "repo_name": repo_name,
        "file_path": file_path,
        "function": func,
        "source_code": source_code,
        "calls_made": sorted(set(calls_made)),
        "called_by": sorted(set(called_by)),
    }


def parse_structured_explanation(
    raw_text: str,
) -> dict:
    """Extract structured explanation sections."""

    sections = {
        "purpose": "",
        "parameters_explained": "",
        "returns_explained": "",
        "flow_summary": "",
    }

    patterns = {
        "purpose": (
            r"PURPOSE:\s*(.*?)(?=PARAMETERS:|$)"
        ),
        "parameters_explained": (
            r"PARAMETERS:\s*(.*?)(?=RETURNS:|$)"
        ),
        "returns_explained": (
            r"RETURNS:\s*(.*?)(?=FLOW:|$)"
        ),
        "flow_summary": (
            r"FLOW:\s*(.*?)$"
        ),
    }

    for key, pattern in patterns.items():
        match = re.search(
            pattern,
            raw_text or "",
            re.DOTALL | re.IGNORECASE,
        )

        if match:
            sections[key] = match.group(1).strip()

    return sections