# ---- Build Stage for React Frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Python Backend ----
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgl1 libglib2.0-0 wget \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
RUN mkdir -p /app/data /app/backend /app/frontend
COPY backend/ /app/backend/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
ENV PYTHONPATH=/app/backend
EXPOSE 10000
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"
