# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend Dependencies
FROM python:3.12-slim AS backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt
RUN find /opt/venv -type d -name "__pycache__" -exec rm -r {} +

# Stage 3: Final Runtime
FROM python:3.12-slim
WORKDIR /app

COPY --from=backend-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist /app/static

RUN mkdir -p /app/vector_db /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
