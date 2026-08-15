from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.git_service import clone_repository
from services.parser_service import parse_repository
# backend/main.py 
from services.chunk_service import chunk_repository
from services.parser_service import parse_repository
from services.embedding_service import embedding_service
from services.chunk_service import chunk_repository
from services.parser_service import parse_repository
from services.vector_db_service import store_chunks
from models.search_models import SearchRequest
from services.search_service import semantic_search
from services.groq_service import generate_answer
from services.search_service import semantic_search
from models.search_models import SearchRequest
from services.unified_ast_service import parse_repository_ast
from services.dependency_graph_service import build_dependency_graph, find_circular_dependencies
from services.unified_ast_service import parse_repository_ast
from services.cache import set_cached_ast, set_cached_graph
from services.callgraph_service import build_call_graph, build_call_graph_networkx
from models.explain_models import FileExplanationRequest
from services.explain_service import explain_file
from services.cache import get_cached_ast, get_cached_graph
from models.explain_models import FunctionExplanationRequest
from services.explain_service import explain_function
from services.cache import get_cached_ast, get_cached_graph, get_cached_parse
from models.codesearch_models import CodeSearchRequest
from services.codesearch_service import code_search
from services.cache import get_cached_ast
from services.diagram_service import build_dependency_diagram
from services.cache import get_cached_graph
from services.cache import set_cached_ast, set_cached_graph, set_cached_callgraph
from services.unified_ast_service import parse_repository_ast
from services.dependency_graph_service import build_dependency_graph
from services.callgraph_service import build_call_graph
app = FastAPI()

# backend/main.py
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CloneRequest(BaseModel):
    github_url: str

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "AI Codebase Knowledge Platform API is running"
    }
    
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/clone")
def clone(request: CloneRequest):
    try:
        result = clone_repository(request.github_url)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
     
@app.post("/parse")
def parse(request: CloneRequest):
    from services.git_service import get_repo_name, REPOS_DIR
    import os

    repo_name = get_repo_name(request.github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Repository not cloned yet. Call /clone first.")

    result = parse_repository(local_path, repo_name)
    # Don't return full file content over the wire for large repos — summarize instead
    summary = result.model_dump(exclude={"files"})
    summary["sample_files"] = [f.path for f in result.files[:20]]
    return summary

@app.post("/chunk")
def chunk(request: CloneRequest):
    import os
    from services.git_service import get_repo_name, REPOS_DIR

    repo_name = get_repo_name(request.github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Repository not cloned yet. Call /clone first.")

    parsed = parse_repository(local_path, repo_name)
    chunks = chunk_repository(parsed.files, repo_name)

    return {
        "repo_name": repo_name,
        "total_files": len(parsed.files),
        "total_chunks": len(chunks),
        "avg_chunks_per_file": round(len(chunks) / max(len(parsed.files), 1), 2),
        "sample_chunks": [
            {
                "chunk_id": c.chunk_id,
                "file_path": c.file_path,
                "lines": f"{c.start_line}-{c.end_line}",
                "preview": c.content[:150] + ("..." if len(c.content) > 150 else "")
            }
            for c in chunks[:5]
        ]
    }
    
@app.post("/embed")
def embed(request: CloneRequest):
    import os, time
    from services.git_service import get_repo_name, REPOS_DIR

    repo_name = get_repo_name(request.github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Repository not cloned yet. Call /clone first.")

    parsed = parse_repository(local_path, repo_name)
    chunks = chunk_repository(parsed.files, repo_name)

    start = time.time()
    texts = [c.content for c in chunks]
    vectors = embedding_service.embed_texts(texts)
    elapsed = time.time() - start

    return {
        "repo_name": repo_name,
        "total_chunks": len(chunks),
        "embedding_dimension": len(vectors[0]) if vectors else 0,
        "time_seconds": round(elapsed, 2),
        "chunks_per_second": round(len(chunks) / elapsed, 2) if elapsed > 0 else None,
    }
    
@app.post("/index")
def index_repository(request: CloneRequest):
    import os, time
    from services.git_service import clone_repository, get_repo_name, REPOS_DIR

    start = time.time()

    try:
        clone_result = clone_repository(request.github_url)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    repo_name = clone_result["repo_name"]
    local_path = clone_result["local_path"]

    parsed = parse_repository(local_path, repo_name)
    chunks = chunk_repository(parsed.files, repo_name)

    if not chunks:
        raise HTTPException(status_code=400, detail="No indexable files found in repository.")

    texts = [c.content for c in chunks]
    vectors = embedding_service.embed_texts(texts)

    store_result = store_chunks(chunks, vectors, repo_name)

    elapsed = time.time() - start

    return {
        "repo_name": repo_name,
        "files_indexed": len(parsed.files),
        "chunks_stored": store_result["stored_count"],
        "time_seconds": round(elapsed, 2),
    }
    
@app.post("/search")
def search(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = semantic_search(request)

    if result.result_count == 0:
        # Not an error — just means nothing matched, or repo isn't indexed
        pass

    return result

class AskRequest(BaseModel):
    question: str
    repo_name: str
    top_k: int = 6

@app.post("/ask")
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    search_result = semantic_search(SearchRequest(
        query=request.question,
        repo_name=request.repo_name,
        top_k=request.top_k,
    ))

    if search_result.result_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No relevant code found. Has this repository been indexed?"
        )

    try:
        answer = generate_answer(request.question, search_result.results)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "question": request.question,
        "repo_name": request.repo_name,
        **answer,
    }
    
   

@app.post("/analyze")
def analyze(request: CloneRequest):
    import os
    from services.git_service import get_repo_name, REPOS_DIR

    repo_name = get_repo_name(request.github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Repository not cloned yet. Call /clone first.")

    parsed = parse_repository(local_path, repo_name)
    ast_results = parse_repository_ast(parsed.files)
    set_cached_ast(repo_name, ast_results)

    total_functions = sum(len(r.functions) for r in ast_results)
    total_classes = sum(len(r.classes) for r in ast_results)
    files_with_errors = [r.file_path for r in ast_results if r.parse_error]

    return {
        "repo_name": repo_name,
        "python_files_analyzed": len(ast_results),
        "total_functions": total_functions,
        "total_classes": total_classes,
        "files_with_syntax_errors": files_with_errors,
        "sample_functions": [
            {
                "name": f.name,
                "file": f.file_path,
                "lines": f"{f.start_line}-{f.end_line}",
                "arguments": f.arguments,
                "is_method": f.is_method,
                "parent_class": f.parent_class,
            }
            for r in ast_results for f in r.functions[:3]
        ][:10],
    }
    
@app.post("/dependencies")
def dependencies(request: CloneRequest):
    import os
    from services.git_service import get_repo_name, REPOS_DIR

    repo_name = get_repo_name(request.github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Repository not cloned yet. Call /clone first.")

    parsed = parse_repository(local_path, repo_name)
    ast_results = parse_repository_ast(parsed.files)
    set_cached_ast(repo_name, ast_results)

    result, graph = build_dependency_graph(ast_results, repo_name)
    set_cached_graph(repo_name, graph)

    cycles = find_circular_dependencies(graph)

    return {
        **result.model_dump(exclude={"edges"}),  # omit raw edges from the summary response (can be large)
        "sample_edges": [e.model_dump() for e in result.edges[:15]],
        "circular_dependencies": cycles[:5],  # cap in case there are many
        "has_circular_dependencies": len(cycles) > 0,
    }
    
@app.post("/callgraph")
def callgraph(request: CloneRequest):
    import os
    from services.git_service import get_repo_name, REPOS_DIR

    repo_name = get_repo_name(request.github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Repository not cloned yet. Call /clone first.")

    parsed = parse_repository(local_path, repo_name)
    ast_results = parse_repository_ast(parsed.files)

    result = build_call_graph(ast_results, repo_name)

    return {
        "repo_name": result.repo_name,
        "total_calls_found": result.total_calls_found,
        "total_resolved": result.total_resolved,
        "total_unresolved": result.total_unresolved,
        "resolution_rate": round(result.total_resolved / max(result.total_calls_found, 1) * 100, 1),
        "most_called_functions": result.most_called_functions,
        "sample_calls": [c.model_dump() for c in result.calls[:15]],
    }
    

@app.post("/explain-function")
def explain_function_endpoint(request: FunctionExplanationRequest):
    ast_results = get_cached_ast(request.repo_name)
    parsed = get_cached_parse(request.repo_name)
    call_graph_result = get_cached_graph(request.repo_name)  # or a separate call-graph cache — see note below

    if ast_results is None or parsed is None:
        raise HTTPException(status_code=404, detail="Repository not analyzed yet.")

    target_file = next((f for f in parsed.files if f.path == request.file_path), None)
    if target_file is None or not target_file.content:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

    try:
        result = explain_function(
            request.repo_name, request.file_path, request.function_name,
            ast_results, target_file.content, call_graph_result,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result

@app.post("/code-search")
def code_search_endpoint(request: CodeSearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    ast_results = get_cached_ast(request.repo_name)
    if ast_results is None:
        raise HTTPException(status_code=404, detail="Repository not analyzed yet. Call /analyze first.")

    result = code_search(request, ast_results)
    return result

@app.get("/diagram/{repo_name}")
def diagram(repo_name: str):
    graph = get_cached_graph(repo_name)
    if graph is None:
        raise HTTPException(status_code=404, detail="Repository not analyzed yet. Call /dependencies first.")

    result = build_dependency_diagram(graph, repo_name)
    return result


@app.post("/index")
def index_repository(request: CloneRequest):
    import time
    start = time.time()

    clone_result = clone_repository(request.github_url)
    repo_name = clone_result["repo_name"]
    local_path = clone_result["local_path"]

    parsed = parse_repository(local_path, repo_name)
    chunks = chunk_repository(parsed.files, repo_name)

    if not chunks:
        raise HTTPException(status_code=400, detail="No indexable files found in repository.")

    vectors = embedding_service.embed_texts([c.content for c in chunks])
    store_chunks(chunks, vectors, repo_name)

    # NEW: run structural analysis and cache it, so explain-file/function,
    # code-search, and diagram endpoints work immediately without extra calls
    ast_results = parse_repository_ast(parsed.files)
    set_cached_ast(repo_name, ast_results)

    graph_result, graph = build_dependency_graph(ast_results, repo_name)
    set_cached_graph(repo_name, graph)

    callgraph_result = build_call_graph(ast_results, repo_name)
    set_cached_callgraph(repo_name, callgraph_result)

    elapsed = time.time() - start

    return {
        "repo_name": repo_name,
        "files_indexed": len(parsed.files),
        "chunks_stored": len(chunks),
        "functions_found": sum(len(r.functions) for r in ast_results),
        "classes_found": sum(len(r.classes) for r in ast_results),
        "internal_dependencies": graph_result.total_internal_edges,
        "time_seconds": round(elapsed, 2),
    }