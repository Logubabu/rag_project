import os
import uuid
from datetime import datetime
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil

import config
from models import ChatRequest, ChatResponse, DocumentResponse
from document_loader import process_file
from utils import recursive_text_splitter
from vector_store import vector_store
from chat import llm_service

app = FastAPI(title="RAG Application API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory document tracker (for simplicity, a real app might use sqlite/postgres)
# documents = { doc_id: { "filename": str, "size": int, "upload_date": str } }
DOCUMENTS = {}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []
    
    for file in files:
        if file.size > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 20 MB limit")
            
        file_ext = file.filename.split('.')[-1].lower()
        supported_exts = ['pdf', 'txt', 'docx', 'md', 'csv', 'json', 'py', 'js', 'ts', 'java', 'sql', 'html', 'xml', 'log', 'zip']
        
        if file_ext not in supported_exts:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
            
        doc_id = str(uuid.uuid4())
        file_path = os.path.join(config.UPLOADS_DIR, f"{doc_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process file
        extracted_docs = process_file(file_path, config.UPLOADS_DIR)
        
        if not extracted_docs:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"No text extracted from {file.filename}")
            
        total_chunks = 0
        for doc in extracted_docs:
            chunks = recursive_text_splitter(doc['text'], config.CHUNK_SIZE, config.CHUNK_OVERLAP)
            vector_store.add_chunks(doc_id, doc['filename'], chunks)
            total_chunks += len(chunks)
            
        DOCUMENTS[doc_id] = {
            "filename": file.filename,
            "size": os.path.getsize(file_path),
            "upload_date": datetime.now().isoformat()
        }
        
        results.append({
            "id": doc_id,
            "filename": file.filename,
            "chunks": total_chunks
        })
        
    return {"message": "Files processed successfully", "files": results}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    response_data = llm_service.generate_answer(request.query)
    return ChatResponse(answer=response_data["answer"], sources=response_data["sources"])

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    return [
        DocumentResponse(
            id=doc_id,
            filename=data["filename"],
            size=data["size"],
            upload_date=data["upload_date"]
        ) for doc_id, data in DOCUMENTS.items()
    ]

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found")
        
    vector_store.delete_document(doc_id)
    
    file_path = os.path.join(config.UPLOADS_DIR, f"{doc_id}_{DOCUMENTS[doc_id]['filename']}")
    if os.path.exists(file_path):
        os.remove(file_path)
        
    del DOCUMENTS[doc_id]
    
    return {"message": "Document deleted successfully"}

# --- Serve Frontend Static Files ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount the static directory if it exists (useful for production)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))

