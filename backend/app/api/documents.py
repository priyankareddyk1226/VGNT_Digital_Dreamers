from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import os, hashlib, shutil
from datetime import datetime
from app.database import get_db
from app.models.domain import Document

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def list_documents(limit: int = 50, db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.upload_date.desc()).limit(limit).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "processed_status": d.processed_status,
            "upload_date": d.upload_date.isoformat() if d.upload_date else None,
            "ocr_confidence": d.ocr_confidence,
            "extracted_entities": d.extracted_entities,
        }
        for d in docs
    ]

@router.get("/stats")
def document_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Document.id)).scalar()
    processed = db.query(func.count(Document.id)).filter(Document.processed_status == "PROCESSED").scalar()
    pending = db.query(func.count(Document.id)).filter(Document.processed_status == "PENDING").scalar()
    failed = db.query(func.count(Document.id)).filter(Document.processed_status == "FAILED").scalar()
    return {
        "total": total,
        "processed": processed,
        "pending": pending,
        "failed": failed,
    }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "SALE_DEED",
    db: Session = Depends(get_db)
):
    """Upload a document for processing."""
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Save file
    save_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(content)
    
    doc = Document(
        filename=file.filename,
        file_path=save_path,
        mime_type=file.content_type,
        document_type=document_type,
        document_hash=file_hash,
        processed_status="PENDING",
        upload_date=datetime.utcnow(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Stub: simulate OCR processing
    _process_document_stub(doc, db)
    
    return {"id": doc.id, "filename": doc.filename, "status": doc.processed_status}

def _process_document_stub(doc: Document, db: Session):
    """Stub OCR processing — extracts basic info from filename."""
    import re
    entities = {
        "document_type": doc.document_type,
        "filename": doc.filename,
        "processing_method": "STUB_OCR",
        "extracted_fields": {
            "survey_number": "SY-" + doc.document_hash[:6].upper(),
            "district": "Hyderabad",
            "parties": ["Owner A", "Owner B"],
        }
    }
    doc.processed_status = "PROCESSED"
    doc.ocr_confidence = 0.87
    doc.ocr_text = f"[Stub OCR] Document: {doc.filename}\nType: {doc.document_type}\nHash: {doc.document_hash}"
    doc.extracted_entities = entities
    db.commit()

@router.get("/{doc_id}")
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "processed_status": doc.processed_status,
        "ocr_text": doc.ocr_text,
        "ocr_confidence": doc.ocr_confidence,
        "extracted_entities": doc.extracted_entities,
        "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
    }
