# backend/services/embedding_service.py
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from config.embedding_config import BGE_QUERY_INSTRUCTION

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")

class EmbeddingService:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_client(self) -> InferenceClient:
        if self._client is None:
            if not HF_TOKEN:
                raise RuntimeError("HF_TOKEN is not set. Add it to your .env file.")
            self._client = InferenceClient(
                provider="hf-inference",
                api_key=HF_TOKEN,
            )
        return self._client

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        client = self._get_client()
        embeddings = []
        for text in texts:
            result = client.feature_extraction(text, model="BAAI/bge-small-en-v1.5")
            embeddings.append(result.tolist() if hasattr(result, "tolist") else list(result))
        return embeddings

    def embed_query(self, query: str) -> list[float]:
        client = self._get_client()
        prefixed = BGE_QUERY_INSTRUCTION + query
        result = client.feature_extraction(prefixed, model="BAAI/bge-small-en-v1.5")
        return result.tolist() if hasattr(result, "tolist") else list(result)

embedding_service = EmbeddingService()