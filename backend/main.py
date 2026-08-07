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
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class CloneRequest(BaseModel):
    github_url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Codebase Platform API"}

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