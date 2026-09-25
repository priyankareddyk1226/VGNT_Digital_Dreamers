# ---- Build Stage for React Frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Build Stage for Python Backend & AI ----
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies required for OpenCV, GeoPandas, and other C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install them
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/backend /app/frontend

# Copy backend source code
COPY backend/ /app/backend/

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Setup user for Hugging Face Spaces (runs as non-root user '1000')
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/app/backend \
    PORT=7860

# Ensure the /app/data directory is writable (though on HF spaces we'll use /data or it will be ephemeral)
# Note: HF spaces provides a persistent volume at /data if requested, or we can use local paths.

# Expose the standard HF port
EXPOSE 7860

# Run Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
