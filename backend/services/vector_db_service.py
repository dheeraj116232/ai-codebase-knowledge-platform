# backend/services/vector_db_service.py
import os
import chromadb
from models.chunk_models import CodeChunk
from config.vector_db_config import (
    CHROMA_MODE, CHROMA_LOCAL_PATH, COLLECTION_NAME,
    CHROMA_CLOUD_API_KEY, CHROMA_CLOUD_TENANT, CHROMA_CLOUD_DATABASE,
)

_client = None
_collection = None


def get_chroma_client():
    global _client
    if _client is not None:
        return _client

    cloud_config_ready = all([
        CHROMA_MODE == "cloud",
        CHROMA_CLOUD_API_KEY,
        CHROMA_CLOUD_TENANT,
        CHROMA_CLOUD_DATABASE,
    ])

    if cloud_config_ready:
        try:
            _client = chromadb.CloudClient(
                tenant=CHROMA_CLOUD_TENANT,
                database=CHROMA_CLOUD_DATABASE,
                api_key=CHROMA_CLOUD_API_KEY,
            )
            return _client
        except Exception as exc:
            print(f"Chroma cloud client initialization failed: {exc}. Falling back to local storage.")

    os.makedirs(CHROMA_LOCAL_PATH, exist_ok=True)
    _client = chromadb.PersistentClient(path=CHROMA_LOCAL_PATH)
    return _client

def get_collection():
    global _collection
    if _collection is not None:
        return _collection

    client = get_chroma_client()
    _collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection

def store_chunks(chunks: list[CodeChunk], embeddings: list[list[float]], repo_name: str):
    collection = get_collection()

    ids = [f"{repo_name}::{c.chunk_id}" for c in chunks]
    documents = [c.content for c in chunks]
    metadatas = [
        {
            "repo_name": repo_name,
            "file_path": c.file_path,
            "language": c.language,
            "start_line": c.start_line,
            "end_line": c.end_line,
            "chunk_index": c.chunk_index,
        }
        for c in chunks
    ]

    BATCH_SIZE = 500
    for i in range(0, len(ids), BATCH_SIZE):
        collection.upsert(
            ids=ids[i:i + BATCH_SIZE],
            embeddings=embeddings[i:i + BATCH_SIZE],
            documents=documents[i:i + BATCH_SIZE],
            metadatas=metadatas[i:i + BATCH_SIZE],
        )

    return {"stored_count": len(ids)}