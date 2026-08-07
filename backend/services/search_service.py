# backend/services/search_service.py
from services.embedding_service import embedding_service
from services.vector_db_service import get_collection
from models.search_models import SearchRequest, SearchResponse, SearchResultItem

def semantic_search(request: SearchRequest) -> SearchResponse:
    collection = get_collection()

    # Quick check: does this repo have any chunks at all?
    # This avoids a confusing empty-but-technically-successful query when the
    # real issue is "this repo was never indexed"
    existing = collection.get(where={"repo_name": request.repo_name}, limit=1)
    if not existing["ids"]:
        return SearchResponse(
            query=request.query,
            repo_name=request.repo_name,
            results=[],
            result_count=0,
        )

    # Embed the query using the QUERY-specific method (with bge instruction prefix)
    query_vector = embedding_service.embed_query(request.query)

    # Build metadata filter — always scope to the repo, optionally to a language
    where_filter = {"repo_name": request.repo_name}
    if request.language_filter:
        where_filter = {
            "$and": [
                {"repo_name": request.repo_name},
                {"language": request.language_filter},
            ]
        }

    raw_results = collection.query(
        query_embeddings=[query_vector],
        n_results=request.top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    results: list[SearchResultItem] = []

    if raw_results["ids"] and raw_results["ids"][0]:
        for i in range(len(raw_results["ids"][0])):
            distance = raw_results["distances"][0][i]
            # ChromaDB with cosine space returns distance in [0, 2]; convert to similarity [0, 1]
            similarity = 1 - (distance / 2)

            metadata = raw_results["metadatas"][0][i]
            document = raw_results["documents"][0][i]
            chunk_id = raw_results["ids"][0][i]

            results.append(SearchResultItem(
                chunk_id=chunk_id,
                file_path=metadata["file_path"],
                language=metadata["language"],
                start_line=metadata["start_line"],
                end_line=metadata["end_line"],
                content=document,
                similarity_score=round(similarity, 4),
            ))

    return SearchResponse(
        query=request.query,
        repo_name=request.repo_name,
        results=results,
        result_count=len(results),
    )