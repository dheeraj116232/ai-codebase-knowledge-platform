# backend/config/embedding_config.py

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384   # bge-small outputs 384-dim vectors
EMBEDDING_BATCH_SIZE = 32   # process chunks in batches, not one-by-one
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "