import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from typing import List, Dict, Any, Tuple
import os

class ChromaStore:
    def __init__(self):
        os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        from app.services.embeddings.model import embedding_model
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_model.model
        )

    def add_chunks(self, document_id: str, filename: str, chunks: List[str], embeddings: List[List[float]]):
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
        except Exception:
            # Handle ChromaDB bug when DB is corrupted/empty
            return [], [], []
        
        # Distances in Chroma with cosine/l2 can vary. Lower distance = higher similarity.
        # We can map distance to a similarity score depending on the space, but for now we'll just return it.
        # Default space is l2. We'll return (documents, metadatas, distances).
        if not results['documents'] or not results['documents'][0]:
            return [], [], []

        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results['distances'][0]
        
        # Convert distances to a pseudo-similarity score (1 / (1 + distance))
        similarities = [1.0 / (1.0 + d) for d in distances]
        
        return docs, metas, similarities

    def delete_document(self, document_id: str):
        # We can't delete by metadata natively in a simple way without getting ids first,
        # but chromadb allows where clause in delete
        self.collection.delete(where={"document_id": document_id})

    def get_stats(self) -> Dict[str, Any]:
        try:
            count = self.collection.count()
        except Exception:
            count = 0
            
        # Calculate size of vector db directory
        total_size = 0
        for dirpath, _, filenames in os.walk(settings.VECTOR_DB_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
                    
        return {
            "total_embeddings": count,
            "vector_db_size_bytes": total_size
        }
        
    def reindex(self):
        # Just clear collection
        self.client.delete_collection(name="documents")
        from app.services.embeddings.model import embedding_model
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_model.model
        )

vector_store = ChromaStore()
