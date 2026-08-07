# backend/services/embedding_service.py
from config.embedding_config import EMBEDDING_MODEL_NAME, EMBEDDING_BATCH_SIZE, BGE_QUERY_INSTRUCTION
from sentence_transformers import SentenceTransformer
from config.embedding_config import EMBEDDING_MODEL_NAME, EMBEDDING_BATCH_SIZE
from models.chunk_models import CodeChunk
import numpy as np

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        # Singleton pattern — only one model instance lives in memory
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_loaded(self):
        if self._model is None:
            print(f"Loading embedding model: {EMBEDDING_MODEL_NAME} ...")
            self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print("Embedding model loaded.")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts, batched for efficiency."""
        self._ensure_loaded()

        if not texts:
            return []

        embeddings = self._model.encode(
            texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,   # normalize -> enables cosine similarity via dot product
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """
        Embeds a search query. Uses the BGE instruction prefix — this asymmetry
        (queries get a prefix, documents/chunks do not) is specific to how
        bge-small-en-v1.5 was trained, and measurably improves retrieval accuracy.
        """
        self._ensure_loaded()
        prefixed = BGE_QUERY_INSTRUCTION + query
        embedding = self._model.encode([prefixed], normalize_embeddings=True)
        return embedding[0].tolist()
    
    def embed_chunks(chunks: list[CodeChunk]) -> list[dict]:
        """
        Takes chunks, returns list of dicts pairing each chunk with its embedding.
        Kept as plain dicts here since this is the direct input to ChromaDB in Step 6.
        """
        texts = [c.content for c in chunks]
        vectors = embedding_service.embed_texts(texts)

        return [
            {"chunk": chunk, "embedding": vector}
            for chunk, vector in zip(chunks, vectors)
        ]

# Module-level singleton instance, imported wherever needed
embedding_service = EmbeddingService()