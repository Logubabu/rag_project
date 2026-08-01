import chromadb
from chromadb.config import Settings
import config
from embeddings import embedding_service
import uuid

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.VECTOR_DB_DIR)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, document_id: str, filename: str, chunks: list[str]):
        if not chunks:
            return
            
        embeddings = embedding_service.get_embeddings(chunks)
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "filename": filename} for _ in chunks]
        
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, top_k: int = config.TOP_K):
        query_embedding = embedding_service.get_embeddings([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            dists = results['distances'][0]
            
            for doc, meta, dist in zip(docs, metas, dists):
                # chromadb distance for cosine space is 1 - cosine_similarity
                score = 1.0 - dist
                formatted_results.append({
                    "text": doc,
                    "filename": meta.get("filename", "unknown"),
                    "score": score
                })
        return formatted_results

    def delete_document(self, document_id: str):
        self.collection.delete(where={"document_id": document_id})

vector_store = VectorStore()
