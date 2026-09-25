from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.domain import Anomaly, Parcel
import json

router = APIRouter()

@router.get("/")
def get_anomalies(
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get anomalies with optional severity filter."""
    query = db.query(Anomaly)
    if severity:
        query = query.filter(Anomaly.severity == severity.upper())
    anomalies = query.order_by(Anomaly.detected_at.desc()).limit(limit).all()
    
    result = []
    for a in anomalies:
        parcel = db.query(Parcel).filter(Parcel.id == a.parcel_id).first()
        result.append({
            "id": a.id,
            "parcel_id": a.parcel_id,
            "survey_number": parcel.survey_number if parcel else "Unknown",
            "district": parcel.district if parcel else "Unknown",
            "village": parcel.village if parcel else "Unknown",
            "rule_id": a.rule_id,
            "severity": a.severity,
            "message": a.message,
            "evidence": a.evidence,
            "confidence": a.confidence,
            "detected_at": a.detected_at.isoformat() if a.detected_at else None,
        })
    return result

@router.get("/stats")
def get_anomaly_stats(db: Session = Depends(get_db)):
    """Get anomaly statistics."""
    from sqlalchemy import func
    stats = db.query(Anomaly.severity, func.count(Anomaly.id)).group_by(Anomaly.severity).all()
    return {s: c for s, c in stats}

@router.get("/{anomaly_id}")
def get_anomaly(anomaly_id: str, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly
