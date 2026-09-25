from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.domain import AuditEvent
from datetime import datetime
import hashlib, json

router = APIRouter()

@router.get("/")
def get_audit_events(limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "record_id": e.record_id,
            "actor": e.actor,
            "action": e.action,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "data_hash": e.data_hash,
            "previous_hash": e.previous_hash,
            "current_hash": e.current_hash,
        }
        for e in events
    ]

@router.get("/verify/{event_id}")
def verify_chain_integrity(event_id: str, db: Session = Depends(get_db)):
    """Verify the cryptographic chain integrity for a given event."""
    event = db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
    if not event:
        return {"valid": False, "reason": "Event not found"}
    
    # Recompute hash
    payload = f"{event.event_type}:{event.record_id}:{event.actor}:{event.action}:{event.data_hash}:{event.previous_hash}"
    expected_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    is_valid = expected_hash == event.current_hash
    return {
        "event_id": event_id,
        "valid": is_valid,
        "expected_hash": expected_hash,
        "stored_hash": event.current_hash,
        "previous_hash": event.previous_hash,
    }

@router.get("/stats")
def audit_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(AuditEvent.id)).scalar()
    by_type = db.query(AuditEvent.event_type, func.count(AuditEvent.id)).group_by(AuditEvent.event_type).all()
    return {"total": total, "by_type": {t: c for t, c in by_type}}
