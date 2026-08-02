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
    
    # 1. Embed question
    query_embedding = embedding_model.encode([question])[0]
    
    # 2. Retrieve chunks
    docs, metas, similarities = vector_store.search(query_embedding, top_k=settings.TOP_K)
    
    if not docs:
        return ChatResponse(
            answer="I couldn't find that information in the uploaded documents.",
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
