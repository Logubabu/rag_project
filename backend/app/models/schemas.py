from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    question: str
    
class SourceCitation(BaseModel):
    filename: str
    chunk_index: int
    similarity_score: float
    text: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[SourceCitation]

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    chunks_count: int

class StatisticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_embeddings: int
    vector_db_size_bytes: int
    embedding_model: str
    llm_provider: str
