from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class OwnerBase(BaseModel):
    id: str
    full_name: str
    contact_info: Optional[str] = None
    is_government: bool

class AnomalyBase(BaseModel):
    id: str
    rule_id: str
    severity: str
    message: str
    confidence: float
    evidence: Dict[str, Any]
    detected_at: datetime

class ParcelBase(BaseModel):
    id: str
    survey_number: str
    district: str
    village: str
    area: float
    area_unit: str
    land_type: str
    risk_score: float
    risk_level: str
    verification_status: str

class ParcelDetail(ParcelBase):
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    created_at: datetime
    geojson_geometry: Optional[Dict[str, Any]] = None
    owners: List[OwnerBase] = []
    anomalies: List[AnomalyBase] = []

    class Config:
        from_attributes = True

class Feature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Dict[str, Any]

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]
