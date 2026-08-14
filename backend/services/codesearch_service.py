# backend/services/codesearch_service.py
from models.ast_models import FileASTResult
from models.codesearch_models import FileMatch
from services.search_service import semantic_search
from models.search_models import SearchRequest
from models.codesearch_models import SemanticMatch
from models.codesearch_models import CodeSearchRequest, CodeSearchResponse
def search_exact_matches(query: str, ast_results: list[FileASTResult], max_results: int) -> list[FileMatch]:
    query_lower = query.lower()
    matches: list[FileMatch] = []

    for result in ast_results:
        # Filename match
        if query_lower in result.file_path.lower():
            matches.append(FileMatch(
                file_path=result.file_path,
                match_type="filename",
                matched_name=result.file_path,
            ))

        # Function name match
        for func in result.functions:
            if query_lower in func.name.lower():
                matches.append(FileMatch(
                    file_path=result.file_path,
                    match_type="function_name",
                    matched_name=func.name,
                    line=func.start_line,
                ))

        # Class name match
        for cls in result.classes:
            if query_lower in cls.name.lower():
                matches.append(FileMatch(
                    file_path=result.file_path,
                    match_type="class_name",
                    matched_name=cls.name,
                    line=cls.start_line,
                ))

    return matches[:max_results]

def search_semantic_matches(query: str, repo_name: str, max_results: int) -> list[SemanticMatch]:
    result = semantic_search(
        SearchRequest(query=query, repo_name=repo_name, top_k=max_results),
        use_reranking=True,
    )

    return [
        SemanticMatch(
            file_path=r.file_path,
            start_line=r.start_line,
            end_line=r.end_line,
            content_preview=(r.content[:200] + "...") if len(r.content) > 200 else r.content,
            relevance_score=r.similarity_score,
        )
        for r in result.results
    ]
    
def code_search(request: CodeSearchRequest, ast_results: list[FileASTResult]) -> CodeSearchResponse:
    exact = search_exact_matches(request.query, ast_results, request.max_results)
    semantic = search_semantic_matches(request.query, request.repo_name, request.max_results)

    # Deduplicate: if a file already appears in exact matches, don't repeat it
    # in semantic matches unless it's a genuinely different code location
    exact_files = {m.file_path for m in exact}
    semantic_filtered = [
        m for m in semantic
        if not (m.file_path in exact_files and m.relevance_score < 0.5)
    ]

    return CodeSearchResponse(
        query=request.query,
        exact_matches=exact,
        semantic_matches=semantic_filtered,
        total_results=len(exact) + len(semantic_filtered),
    )