from chromadb.utils import embedding_functions
from typing import List

class EmbeddingModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            from app.core.config import settings
            cls._instance.model = embedding_functions.HuggingFaceEmbeddingFunction(
                api_key=settings.HF_API_KEY,
                model_name=settings.EMBEDDING_MODEL
            )
        return cls._instance

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        # DefaultEmbeddingFunction returns a list of embeddings
        # which are lists of floats.
        return self.model(texts)

embedding_model = EmbeddingModel()
