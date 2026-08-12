# backend/services/dependency_graph_service.py
import networkx as nx
from models.ast_models import FileASTResult
from models.graph_models import DependencyEdge, DependencyGraphResult
from services.dependency_resolver import resolve_python_import, resolve_js_import

def build_dependency_graph(
    ast_results: list[FileASTResult],
    repo_name: str,
) -> tuple[DependencyGraphResult, nx.DiGraph]:
    all_file_paths = {r.file_path.replace("\\", "/") for r in ast_results}

    graph = nx.DiGraph()
    for path in all_file_paths:
        graph.add_node(path)

    edges: list[DependencyEdge] = []
    external_packages: set[str] = set()

    for file_result in ast_results:
        source_file = file_result.file_path.replace("\\", "/")
        ext = source_file.rsplit(".", 1)[-1] if "." in source_file else ""

        for imp in file_result.imports:
            resolved = None

            if ext == "py":
                resolved = resolve_python_import(
                    imp.module,
                    imp.is_relative,
                    source_file,
                    all_file_paths,
                    imported_names=imp.imported_names,
                    level=imp.level,
                )
            elif ext in ("js", "jsx", "ts", "tsx"):
                resolved = resolve_js_import(imp.module, source_file, all_file_paths)

            if resolved:
                graph.add_edge(source_file, resolved)
                edges.append(DependencyEdge(
                    source_file=source_file,
                    target_file=resolved,
                    is_external=False,
                    import_line=imp.line,
                ))
            else:
                external_target = imp.module or ", ".join(imp.imported_names)
                external_packages.add(external_target)
                edges.append(DependencyEdge(
                    source_file=source_file,
                    target_file=external_target,
                    is_external=True,
                    import_line=imp.line,
                ))

    in_degrees = sorted(graph.in_degree(), key=lambda x: x[1], reverse=True)
    most_depended_on = [
        {"file": file, "dependent_count": count}
        for file, count in in_degrees if count > 0
    ][:10]

    internal_edge_count = sum(1 for e in edges if not e.is_external)

    result = DependencyGraphResult(
        repo_name=repo_name,
        total_files=len(all_file_paths),
        total_internal_edges=internal_edge_count,
        total_external_dependencies=len(external_packages),
        edges=edges,
        most_depended_on=most_depended_on,
        external_packages=sorted(external_packages),
    )

    return result, graph


def find_circular_dependencies(graph: nx.DiGraph) -> list[list[str]]:
    """Returns groups of files that import each other in a cycle — often a code smell worth flagging."""
    try:
        cycles = list(nx.simple_cycles(graph))
        return cycles
    except Exception:
        return []
