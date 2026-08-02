from chromadb.utils import embedding_functions
from typing import List

class EmbeddingModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            # Chroma's DefaultEmbeddingFunction uses ONNX and all-MiniLM-L6-v2 internally.
            # This requires NO torch, NO network requests at runtime (after initial download),
            # and is extremely fast and lightweight.
            cls._instance.model = embedding_functions.DefaultEmbeddingFunction()
        return cls._instance

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        # DefaultEmbeddingFunction returns a list of embeddings
        # which are lists of floats.
        return self.model(texts)

embedding_model = EmbeddingModel()
