from sentence_transformers import SentenceTransformer
import torch
import config

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
            print(f"Loading embedding model {config.EMBEDDING_MODEL_NAME} on {cls._instance.device}...")
            cls._instance.model = SentenceTransformer(config.EMBEDDING_MODEL_NAME, device=cls._instance.device)
        return cls._instance

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

embedding_service = EmbeddingService()
