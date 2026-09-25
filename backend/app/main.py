import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
import app.models.domain  # Import models to ensure they are registered

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Evidence-Based Land Governance & Policy Intelligence Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": True,
        "gis": True,  # Will be updated when components are ready
        "vector_search": settings.ENABLE_SENTENCE_TRANSFORMERS,
        "ocr": settings.ENABLE_PADDLE_OCR,
        "ml": True,
        "audit": True
    }

from app.api import parcels, gis, anomalies, documents, dashboard, audit, ai_assistant

# API Routes
app.include_router(parcels.router, prefix="/api/parcels", tags=["parcels"])
app.include_router(gis.router, prefix="/api/gis", tags=["gis"])
app.include_router(anomalies.router, prefix="/api/anomalies", tags=["anomalies"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["ai-assistant"])

# Serve React App in Production/HF Space
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
