import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.logging import setup_logging
from app.routes import upload, chat, documents, system

# Setup logging
logger = setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Production-Ready RAG API",
        description="A scalable and modular RAG API",
        version="1.0.0",
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ensure required directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
    os.makedirs(settings.LOGS_DIR, exist_ok=True)

    # Include Routers
    app.include_router(upload.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(system.router, prefix="/api")

    # Serve static frontend in production (Docker)
    static_dir = os.path.join(settings.BASE_DIR, "static")
    if os.path.exists(static_dir):
        app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            if full_path.startswith("api"):
                return {"error": "API route not found"}
            file_path = os.path.join(static_dir, full_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(static_dir, "index.html"))
    else:
        @app.get("/")
        async def root():
            return {"message": "Welcome to the RAG API. Frontend static files not found."}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
