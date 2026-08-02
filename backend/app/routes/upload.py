from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import os
import uuid
from app.core.config import settings
from app.services.document_loader.loaders import document_loader
from app.services.chunking import recursive_character_text_splitter
from app.services.embeddings.model import embedding_model
from app.services.vector_store.chroma_store import vector_store

router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024 # 20 MB

def process_file_background(file_path: str, document_id: str, original_filename: str):
    try:
        # 1. Load document
        docs = document_loader.load_file(file_path)
        
        for doc in docs:
            filename = doc["filename"]
            content = doc["content"]
            
            # 2. Split into chunks
            chunks = recursive_character_text_splitter(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            if not chunks:
                continue
                
            # 3. Generate embeddings
            embeddings = embedding_model.encode(chunks)
            
            # 4. Store in Vector DB
            vector_store.add_chunks(document_id, filename, chunks, embeddings)
            
    except Exception as e:
        print(f"Error processing file {original_filename}: {e}")
        # In a real app, update document status in a database
    finally:
        # Cleanup uploaded file if it's not needed
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/upload")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    results = []
    
    for file in files:
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 20MB limit.")
            
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in document_loader.supported_extensions and ext != '.zip':
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
            
        document_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}_{file.filename}")
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # Enqueue background processing
        background_tasks.add_task(process_file_background, file_path, document_id, file.filename)
        
        results.append({
            "id": document_id,
            "filename": file.filename,
            "status": "processing"
        })
        
    return {"message": "Files uploaded successfully", "documents": results}
