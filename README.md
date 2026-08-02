# Production-Ready RAG Application

A lightweight, scalable, and modular Retrieval-Augmented Generation (RAG) application built with Python (FastAPI), React, ChromaDB, and Groq API. It uses `sentence-transformers` for embedding generation locally without relying on heavy frameworks like LangChain.

## Features
- **Upload Documents:** Supports PDF, DOCX, TXT, CSV, Excel, JSON, Markdown, Code files, and ZIP archives.
- **Custom Text Chunking:** Splits text with customizable size (800) and overlap (100).
- **Local Embeddings:** Uses `sentence-transformers/all-MiniLM-L6-v2` loaded once for efficiency.
- **Vector Search:** Persists vectors locally using ChromaDB.
- **LLM Integration:** Connects to Groq API (primary) with fallback to Hugging Face Inference API.
- **ChatGPT-Style UI:** React frontend featuring drag & drop upload, progress bars, dark mode, typing animation, markdown rendering, and source citations.
- **Clean Architecture:** Modular backend built with FastAPI.
- **Dockerized:** Ready for deployment on Hugging Face Spaces, Render, Koyeb, etc.

## Folder Structure

```
rag-app/
│
├── backend/
│   ├── app/
│   │   ├── core/         # Config and logging
│   │   ├── models/       # Pydantic schemas
│   │   ├── routes/       # API endpoints (upload, chat, documents, system)
│   │   ├── services/     # Core logic (loaders, chunking, embeddings, vector_store, chat)
│   │   └── main.py       # FastAPI application entry
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/   # ChatInterface, UploadManager
│   │   ├── services/     # Axios API service
│   │   ├── App.jsx       # Main layout
│   │   └── index.css     # Tailwind CSS entry
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── .env                  # Environment variables
├── Dockerfile            # Multi-stage Docker build
└── README.md             # This file
```

## Environment Variables

Create a `.env` file in the root directory:

```env
LLM_PROVIDER=groq
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=5

GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_hf_api_key_here
```

## Installation & Running Locally

### Backend

1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Docker Deployment

This project includes a multi-stage Dockerfile that builds the React frontend and serves it statically via FastAPI.

### Build Docker Image
```bash
docker build -t rag-app .
```

### Run Docker Container
```bash
docker run -p 8000:8000 --env-file .env rag-app
```
Access the application at `http://localhost:8000`.

## API Documentation

Once the backend is running, access the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints
- `POST /api/upload`: Upload files for processing.
- `POST /api/chat`: Ask questions to the RAG system.
- `GET /api/documents`: List uploaded documents.
- `DELETE /api/document/{id}`: Delete a document and its embeddings.
- `GET /api/statistics`: Get system statistics.
- `POST /api/reindex`: Clear the vector database.
