from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.domain import Parcel
from app.schemas.domain import ParcelBase, ParcelDetail

router = APIRouter()

@router.get("/", response_model=List[ParcelBase])
def get_parcels(skip: int = 0, limit: int = 100, district: str = None, risk_level: str = None, db: Session = Depends(get_db)):
    query = db.query(Parcel)
    if district:
        query = query.filter(Parcel.district == district)
    if risk_level:
        query = query.filter(Parcel.risk_level == risk_level)
        
    return query.offset(skip).limit(limit).all()

@router.get("/{parcel_id}", response_model=ParcelDetail)
def get_parcel(parcel_id: str, db: Session = Depends(get_db)):
    parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel
