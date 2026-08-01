from chromadb.utils import embedding_functions

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            print(f"Loading ONNX embedding model (Torch-free)...")
            # DefaultEmbeddingFunction uses all-MiniLM-L6-v2 via ONNX
            cls._instance.ef = embedding_functions.DefaultEmbeddingFunction()
        return cls._instance

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        # chromadb embedding functions return a list of embeddings
        return self.ef(texts)

embedding_service = EmbeddingService()
