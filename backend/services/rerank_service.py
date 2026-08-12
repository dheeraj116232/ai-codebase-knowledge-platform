# backend/services/rerank_service.py
from sentence_transformers import CrossEncoder
from config.rerank_config import RERANK_MODEL_NAME
from models.search_models import SearchResultItem

class RerankService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_loaded(self):
        if self._model is None:
            print(f"Loading reranker model: {RERANK_MODEL_NAME} ...")
            self._model = CrossEncoder(RERANK_MODEL_NAME)
            print("Reranker loaded.")

    def rerank(self, query: str, candidates: list[SearchResultItem], top_k: int) -> list[SearchResultItem]:
        self._ensure_loaded()

        if not candidates:
            return []

        # Cross-encoder expects (query, document) pairs
        pairs = [[query, c.content] for c in candidates]
        scores = self._model.predict(pairs)

        # Attach new scores and sort — replacing the bi-encoder similarity_score
        # with the more precise cross-encoder score
        scored = list(zip(candidates, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        reranked = []
        for item, score in scored[:top_k]:
            item_copy = item.model_copy(update={"similarity_score": round(float(score), 4)})
            reranked.append(item_copy)

        return reranked

rerank_service = RerankService()