from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation
from app.services.embeddings.model import embedding_model
from app.services.vector_store.chroma_store import vector_store
from app.services.chat.llm_client import llm_client
from app.core.config import settings

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question
    
    docs, metas, similarities = [], [], []
    try:
        # 1. Embed question (this might fail if HF API is down)
        if vector_store.collection.count() > 0:
            query_embedding = embedding_model.encode([question])[0]
            # 2. Retrieve chunks
            docs, metas, similarities = vector_store.search(query_embedding, top_k=settings.TOP_K)
    except Exception as e:
        print(f"Vector search/embedding failed: {e}. Falling back to default resume.")
        docs = []
    
    if not docs:
        import os
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "fallback_resume.txt")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                fallback_content = f.read()
            docs = [fallback_content]
            metas = [{"filename": "fallback_resume.txt", "chunk_index": 0}]
            similarities = [1.0]
        else:
            return ChatResponse(
                answer="I couldn't find that information in the uploaded documents. (Fallback resume not found either.)",
                citations=[]
            )
        
    # 3. Format context
    context = "\n\n".join(docs)
    
    # 4. Generate answer
    try:
        answer = await llm_client.generate_response(question, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
        
    # 5. Format citations
    citations = []
    for doc, meta, score in zip(docs, metas, similarities):
        citations.append(
            SourceCitation(
                filename=meta.get("filename", "Unknown"),
                chunk_index=meta.get("chunk_index", 0),
                similarity_score=round(score, 4),
                text=doc
            )
        )
        
    # If the model explicitly says it couldn't find it
    if "couldn't find that information" in answer:
        citations = []
        
    return ChatResponse(
        answer=answer,
        citations=citations
    )
