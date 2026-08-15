# backend/services/search_service.py
from services.embedding_service import embedding_service
from services.vector_db_service import get_collection
from models.search_models import SearchRequest, SearchResponse, SearchResultItem
from config.rerank_config import INITIAL_RETRIEVAL_K, FINAL_TOP_K, RERANKING_ENABLED

MIN_SIMILARITY_SCORE = 0.80


def _load_rerank_service():
    try:
        from services.rerank_service import rerank_service
        return rerank_service
    except ModuleNotFoundError:
        return None


def semantic_search(request: SearchRequest, use_reranking: bool = RERANKING_ENABLED) -> SearchResponse:
    collection = get_collection()

    existing = collection.get(where={"repo_name": request.repo_name}, limit=1)
    if not existing["ids"]:
        return SearchResponse(query=request.query, repo_name=request.repo_name, results=[], result_count=0)

    query_vector = embedding_service.embed_query(request.query)

    where_filter = {"repo_name": request.repo_name}
    if request.language_filter:
        where_filter = {"$and": [{"repo_name": request.repo_name}, {"language": request.language_filter}]}

    # STAGE 1: broad retrieval — pull more candidates than we'll actually use
    retrieval_k = INITIAL_RETRIEVAL_K if use_reranking else request.top_k

    raw_results = collection.query(
        query_embeddings=[query_vector],
        n_results=retrieval_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    candidates: list[SearchResultItem] = []
    if raw_results["ids"] and raw_results["ids"][0]:
        for i in range(len(raw_results["ids"][0])):
            distance = raw_results["distances"][0][i]
            similarity = 1 - (distance / 2)
            metadata = raw_results["metadatas"][0][i]

            candidates.append(SearchResultItem(
                chunk_id=raw_results["ids"][0][i],
                file_path=metadata["file_path"],
                language=metadata["language"],
                start_line=metadata["start_line"],
                end_line=metadata["end_line"],
                content=raw_results["documents"][0][i],
                similarity_score=round(similarity, 4),
            ))

    candidates = [c for c in candidates if c.similarity_score >= MIN_SIMILARITY_SCORE]

    # STAGE 2: rerank the candidates, keep only the best few — falls back gracefully
    # if rerank_service isn't installed (e.g. removed to save memory on Render)
    if use_reranking and candidates:
        rerank_service = _load_rerank_service()
        if rerank_service is not None:
            top_k = min(FINAL_TOP_K, request.top_k)
            final_results = rerank_service.rerank(request.query, candidates, top_k=top_k)
        else:
            final_results = candidates[:request.top_k]
    else:
        final_results = candidates[:request.top_k]

    return SearchResponse(
        query=request.query,
        repo_name=request.repo_name,
        results=final_results,
        result_count=len(final_results),
    )