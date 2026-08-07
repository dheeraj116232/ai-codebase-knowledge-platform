import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class VectorDbServiceTests(unittest.TestCase):
    def test_get_chroma_client_falls_back_to_local_when_cloud_is_unavailable(self):
        import services.vector_db_service as vector_db_service

        class FakeCloudClient:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("cloud unavailable")

        class FakePersistentClient:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        with patch.object(vector_db_service, "_client", None), \
             patch.object(vector_db_service, "_collection", None), \
             patch.object(vector_db_service, "chromadb", type("chromadb", (), {"CloudClient": FakeCloudClient, "PersistentClient": FakePersistentClient})), \
             patch.object(vector_db_service, "CHROMA_MODE", "cloud"), \
             patch.object(vector_db_service, "CHROMA_CLOUD_API_KEY", "key"), \
             patch.object(vector_db_service, "CHROMA_CLOUD_TENANT", "tenant"), \
             patch.object(vector_db_service, "CHROMA_CLOUD_DATABASE", "db"):
            client = vector_db_service.get_chroma_client()

        self.assertIsInstance(client, FakePersistentClient)


if __name__ == "__main__":
    unittest.main()
