from fastapi import APIRouter
from typing import List
from app.models.schemas import DocumentMetadata
from app.services.vector_store.chroma_store import vector_store

router = APIRouter()

@router.get("/documents", response_model=List[DocumentMetadata])
async def list_documents():
    collection = vector_store.collection
    try:
        results = collection.get(include=['metadatas'])
    except Exception:
        results = {'metadatas': []}
    
    docs_map = {}
    for meta in results.get('metadatas', []):
        if not meta:
            continue
        doc_id = meta.get('document_id')
        if not doc_id:
            continue
        if doc_id not in docs_map:
            docs_map[doc_id] = {
                "id": doc_id,
                "filename": meta.get('filename', 'Unknown'),
                "content_type": meta.get('filename', '').split('.')[-1] if meta.get('filename') else "unknown",
                "size": 0,
                "chunks_count": 0
            }
        docs_map[doc_id]["chunks_count"] += 1
        
    return list(docs_map.values())

@router.get("/document/{id}", response_model=DocumentMetadata)
async def get_document(id: str):
    # Retrieve all chunks for this doc to build metadata
    collection = vector_store.collection
    try:
        results = collection.get(where={"document_id": id}, include=['metadatas'])
    except Exception:
        results = {'metadatas': []}
    
    if not results.get('metadatas'):
        return None
        
    meta = results['metadatas'][0]
    return DocumentMetadata(
        id=id,
        filename=meta.get('filename', 'Unknown'),
        content_type=meta.get('filename', '').split('.')[-1],
        size=0,
        chunks_count=len(results['metadatas'])
    )

@router.delete("/document/{id}")
async def delete_document(id: str):
    vector_store.delete_document(id)
    return {"message": "Document deleted successfully"}
