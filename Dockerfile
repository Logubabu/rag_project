# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend Dependencies
FROM python:3.12-slim AS backend-builder
WORKDIR /app
COPY backend/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 3: Final Image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VITE_API_URL=/api

WORKDIR /app

# Copy python dependencies
COPY --from=backend-builder /install /usr/local

# Copy backend code
COPY backend/ /app/

# Copy built frontend from Stage 1 to a static directory
COPY --from=frontend-builder /app/frontend/dist /app/static

# Prune unnecessary files to reduce image size
RUN find /usr/local/lib/python3.12 -type d -name "__pycache__" -exec rm -r {} + || true \
    && find /usr/local/lib/python3.12 -type d -name "tests" -exec rm -r {} + || true \
    && rm -rf /usr/local/lib/python3.12/site-packages/pip \
    && rm -rf /usr/local/lib/python3.12/site-packages/setuptools

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
