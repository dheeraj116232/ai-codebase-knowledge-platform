from services.dependency_resolver import resolve_python_import, resolve_js_import
from config.llm_config import GROQ_MODEL, TEMPERATURE
from services.groq_service import get_groq_client
from services.prompt_builder import FILE_EXPLANATION_SYSTEM_PROMPT, build_file_explanation_prompt
from models.ast_models import FileASTResult
from models.explain_models import FileExplanationResponse

def gather_file_context(file_path: str, ast_results: list[FileASTResult], dependency_graph) -> dict | None:
    normalized_file_path = file_path.replace("\\", "/")
    file_ast = next(
        (r for r in ast_results if r.file_path.replace("\\", "/") == normalized_file_path),
        None,
    )
    if file_ast is None:
        return None

    all_file_paths = {r.file_path.replace("\\", "/") for r in ast_results}
    ext = normalized_file_path.rsplit(".", 1)[-1] if "." in normalized_file_path else ""

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
                imported_names=imp.imported_names,
                level=imp.level,
            )
        elif ext in ("js", "jsx", "ts", "tsx"):
            resolved = resolve_js_import(imp.module, normalized_file_path, all_file_paths)

        if resolved:
            internal_deps.append(resolved)
        else:
            external_deps.add(imp.module or ", ".join(imp.imported_names))

    dependents = (
        list(dependency_graph.predecessors(normalized_file_path))
        if dependency_graph and normalized_file_path in dependency_graph
        else []
    )

    return {
        "file_path": normalized_file_path,
        "language": ext,
        "functions": file_ast.functions,
        "classes": file_ast.classes,
        "internal_deps": internal_deps,
        "external_deps": sorted(external_deps),
        "dependents": dependents,
    }
    

def explain_file(file_path: str, ast_results: list[FileASTResult], dependency_graph) -> FileExplanationResponse:
    context = gather_file_context(file_path, ast_results, dependency_graph)

    if context is None:
        raise ValueError(f"File not found in analyzed results: {file_path}")

    client = get_groq_client()
    prompt = build_file_explanation_prompt(context)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": FILE_EXPLANATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=300,   # summaries should be short — cap it explicitly
    )

    summary = response.choices[0].message.content

    return FileExplanationResponse(
        file_path=context["file_path"],
        language=context["language"],
        summary=summary,
        function_count=len(context["functions"]),
        class_count=len(context["classes"]),
        functions=[f.name for f in context["functions"]],
        classes=[c.name for c in context["classes"]],
        internal_dependencies=context["internal_deps"],
        dependents=context["dependents"],
        external_dependencies=context["external_deps"],
    )
