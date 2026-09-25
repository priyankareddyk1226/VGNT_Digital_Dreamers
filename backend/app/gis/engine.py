import geopandas as gpd
from shapely.geometry import shape, mapping
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.domain import Parcel

class GISEngine:
    @staticmethod
    def get_parcel_feature_collection(db: Session, limit: int = 1000) -> Dict[str, Any]:
        """Fetch parcels as a GeoJSON FeatureCollection"""
        parcels = db.query(Parcel).filter(Parcel.geojson_geometry.isnot(None)).limit(limit).all()
        features = []
        for p in parcels:
            feature = {
                "type": "Feature",
                "properties": {
                    "id": p.id,
                    "survey_number": p.survey_number,
                    "risk_score": p.risk_score,
                    "risk_level": p.risk_level,
                    "district": p.district,
                    "village": p.village
                },
                "geometry": p.geojson_geometry
            }
            features.append(feature)
            
        return {
            "type": "FeatureCollection",
            "features": features
        }

    @staticmethod
    def calculate_overlap(geometry1: Dict[str, Any], geometry2: Dict[str, Any]) -> float:
        """Calculate overlap percentage between two GeoJSON geometries"""
        s1 = shape(geometry1)
        s2 = shape(geometry2)
        if not s1.intersects(s2):
            return 0.0
        
        intersection_area = s1.intersection(s2).area
        min_area = min(s1.area, s2.area)
        
        if min_area == 0:
            return 0.0
            
        return (intersection_area / min_area) * 100.0
