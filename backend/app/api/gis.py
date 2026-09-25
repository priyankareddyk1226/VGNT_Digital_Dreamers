from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.gis.engine import GISEngine
from app.schemas.domain import FeatureCollection

router = APIRouter()

@router.get("/parcels", response_model=FeatureCollection)
def get_gis_parcels(db: Session = Depends(get_db)):
    """Returns a GeoJSON FeatureCollection of all parcels for the Map"""
    return GISEngine.get_parcel_feature_collection(db)
