# Lightweight RAG Application

A lightweight, production-quality Retrieval-Augmented Generation (RAG) web application built with FastAPI, React, and local open-source models. It allows you to upload documents and chat with them securely without using paid APIs.

## Features
- **Local Execution**: 100% local, no API keys needed.
- **Multiple File Types**: Supports PDF, TXT, DOCX, CSV, JSON, ZIP, etc.
- **Vector Storage**: Uses ChromaDB for fast, persistent document embedding retrieval.
- **Modern UI**: Built with React, Vite, and Tailwind CSS.
- **LLM & Embeddings**: Uses `SmolLM2-360M-Instruct` and `all-MiniLM-L6-v2`.

## Project Structure
```text
RAG/
├── backend/
│   ├── app.py              # FastAPI application and endpoints
│   ├── chat.py             # LLM setup and chat logic
│   ├── config.py           # Configuration parameters
│   ├── document_loader.py  # File parsing logic
│   ├── embeddings.py       # Sentence-Transformers model setup
│   ├── models.py           # Pydantic models for validation
│   ├── requirements.txt    # Python dependencies
│   ├── utils.py            # Recursive text splitter
│   └── vector_store.py     # ChromaDB wrapper
└── frontend/
    ├── package.json        # Node.js dependencies
    ├── src/
    │   ├── App.jsx         # Main layout
    │   ├── index.css       # Tailwind base styles
    │   ├── main.jsx        # React entry point
    │   ├── pages/          # Chat and Files pages
    │   └── services/       # API integration via Axios
    ├── tailwind.config.js
    └── vite.config.js
```

## Installation & Running Locally

### Backend Setup
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   uvicorn app:app --reload
   ```

*Note: The first time you run this, it will download the Hugging Face models (`SmolLM2-360M-Instruct` and `all-MiniLM-L6-v2`). This may take a few minutes.*

### Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## API Endpoints
- `POST /upload`: Upload one or multiple files.
- `POST /chat`: Submit a question and get a generated response based on your documents.
- `GET /documents`: List all uploaded files.
- `DELETE /documents/{id}`: Delete a specific file.

## Deployment Guide
- **Frontend (Vercel)**: Connect your GitHub repository to Vercel and set the Root Directory to `frontend`. Vite settings will automatically apply.
- **Backend (Render)**: Connect your repository to Render, select `backend` as the root directory, use `pip install -r requirements.txt` as the Build Command, and `uvicorn app:app --host 0.0.0.0 --port $PORT` as the Start Command.
