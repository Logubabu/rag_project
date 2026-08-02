from fastapi import APIRouter
from app.models.schemas import StatisticsResponse
from app.services.vector_store.chroma_store import vector_store
from app.core.config import settings

router = APIRouter()

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    stats = vector_store.get_stats()
    
    # Calculate total documents (unique metadatas)
    collection = vector_store.collection
    try:
        results = collection.get(include=['metadatas'])
    except Exception:
        results = {'metadatas': []}
        
    unique_docs = set()
    for meta in results.get('metadatas', []):
        if meta and 'document_id' in meta:
            unique_docs.add(meta['document_id'])
            
    return StatisticsResponse(
        total_documents=len(unique_docs),
        total_chunks=stats["total_embeddings"],
        total_embeddings=stats["total_embeddings"],
        vector_db_size_bytes=stats["vector_db_size_bytes"],
        embedding_model=settings.EMBEDDING_MODEL,
        llm_provider=settings.LLM_PROVIDER
    )

@router.post("/reindex")
async def reindex():
    vector_store.reindex()
    return {"message": "Vector database reindexed successfully. All embeddings cleared."}
