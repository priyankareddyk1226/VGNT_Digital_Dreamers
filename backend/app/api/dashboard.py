from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import get_db
from app.models.domain import Parcel, Anomaly, Document, Transaction, AuditEvent
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get a complete dashboard summary for the overview page."""
    total_parcels = db.query(func.count(Parcel.id)).scalar()
    verified = db.query(func.count(Parcel.id)).filter(Parcel.verification_status == "VERIFIED").scalar()
    conflict = db.query(func.count(Parcel.id)).filter(Parcel.verification_status == "CONFLICT").scalar()
    pending = db.query(func.count(Parcel.id)).filter(Parcel.verification_status == "PENDING").scalar()
    
    critical_parcels = db.query(func.count(Parcel.id)).filter(Parcel.risk_level == "CRITICAL").scalar()
    high_risk = db.query(func.count(Parcel.id)).filter(Parcel.risk_level == "HIGH").scalar()
    
    total_anomalies = db.query(func.count(Anomaly.id)).scalar()
    critical_anomalies = db.query(func.count(Anomaly.id)).filter(Anomaly.severity == "CRITICAL").scalar()
    
    total_docs = db.query(func.count(Document.id)).scalar()
    processed_docs = db.query(func.count(Document.id)).filter(Document.processed_status == "PROCESSED").scalar()
    
    total_area = db.query(func.sum(Parcel.area)).scalar() or 0
    
    # Risk distribution
    risk_dist = db.query(Parcel.risk_level, func.count(Parcel.id)).group_by(Parcel.risk_level).all()
    
    # Land type distribution
    land_type_dist = db.query(Parcel.land_type, func.count(Parcel.id)).group_by(Parcel.land_type).all()
    
    # District distribution (top 10)
    district_dist = db.query(Parcel.district, func.count(Parcel.id)).group_by(Parcel.district).order_by(func.count(Parcel.id).desc()).limit(10).all()

    # Recent anomalies
    recent_anomalies = db.query(Anomaly).order_by(Anomaly.detected_at.desc()).limit(5).all()
    recent_anomaly_list = []
    for a in recent_anomalies:
        parcel = db.query(Parcel).filter(Parcel.id == a.parcel_id).first()
        recent_anomaly_list.append({
            "id": a.id,
            "parcel_id": a.parcel_id,
            "survey_number": parcel.survey_number if parcel else "Unknown",
            "severity": a.severity,
            "message": a.message,
            "detected_at": a.detected_at.isoformat() if a.detected_at else None,
        })

    return {
        "parcels": {
            "total": total_parcels,
            "verified": verified,
            "conflict": conflict,
            "pending": pending,
            "critical_risk": critical_parcels,
            "high_risk": high_risk,
            "total_area_hectares": round(total_area, 2),
        },
        "anomalies": {
            "total": total_anomalies,
            "critical": critical_anomalies,
        },
        "documents": {
            "total": total_docs,
            "processed": processed_docs,
        },
        "risk_distribution": {r: c for r, c in risk_dist},
        "land_type_distribution": {l: c for l, c in land_type_dist},
        "district_distribution": {d: c for d, c in district_dist},
        "recent_anomalies": recent_anomaly_list,
    }
