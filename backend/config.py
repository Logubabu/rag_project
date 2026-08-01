import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Models
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL_NAME = "HuggingFaceTB/SmolLM2-360M-Instruct"

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Search
TOP_K = 5

# Ensure directories exist
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
