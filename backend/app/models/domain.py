import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="VIEWER") # ADMIN, OFFICER, RESEARCHER, VERIFIER, VIEWER
    created_at = Column(DateTime, default=datetime.utcnow)

class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(String, primary_key=True, default=generate_uuid)
    survey_number = Column(String, index=True)
    khasra_number = Column(String, nullable=True)
    khata_number = Column(String, nullable=True)
    district = Column(String, index=True)
    village = Column(String, index=True)
    area = Column(Float)
    area_unit = Column(String)
    land_type = Column(String) # Agricultural, Residential, Commercial, Government
    geojson_geometry = Column(JSON) # Store geometry as GeoJSON directly
    risk_score = Column(Float, default=0.0, index=True)
    risk_level = Column(String, default="LOW")
    verification_status = Column(String, default="PENDING", index=True) # PENDING, VERIFIED, CONFLICT
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owners = relationship("Owner", secondary="parcel_owners", back_populates="parcels")
    transactions = relationship("Transaction", back_populates="parcel")
    anomalies = relationship("Anomaly", back_populates="parcel")

class Owner(Base):
    __tablename__ = "owners"
    id = Column(String, primary_key=True, default=generate_uuid)
    full_name = Column(String, index=True)
    contact_info = Column(String, nullable=True)
    is_government = Column(Boolean, default=False)
    
    parcels = relationship("Parcel", secondary="parcel_owners", back_populates="owners")

class ParcelOwner(Base):
    __tablename__ = "parcel_owners"
    parcel_id = Column(String, ForeignKey("parcels.id"), primary_key=True)
    owner_id = Column(String, ForeignKey("owners.id"), primary_key=True)
    share_percentage = Column(Float, default=100.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=generate_uuid)
    parcel_id = Column(String, ForeignKey("parcels.id"))
    transaction_type = Column(String) # SALE, INHERITANCE, GIFT, SUBDIVISION
    transaction_date = Column(DateTime)
    mutation_number = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    
    from_owner_id = Column(String, ForeignKey("owners.id"), nullable=True)
    to_owner_id = Column(String, ForeignKey("owners.id"), nullable=True)
    
    parcel = relationship("Parcel", back_populates="transactions")
    document = relationship("Document")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String)
    file_path = Column(String)
    mime_type = Column(String)
    document_type = Column(String) # SALE_DEED, MUTATION_RECORD, ENCUMBRANCE_CERT
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_status = Column(String, default="PENDING") # PENDING, PROCESSED, FAILED
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    document_hash = Column(String)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(String, primary_key=True, default=generate_uuid)
    parcel_id = Column(String, ForeignKey("parcels.id"))
    rule_id = Column(String)
    severity = Column(String) # INFO, LOW, MEDIUM, HIGH, CRITICAL
    message = Column(String)
    evidence = Column(JSON)
    confidence = Column(Float)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    parcel = relationship("Parcel", back_populates="anomalies")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    event_type = Column(String)
    record_id = Column(String)
    actor = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data_hash = Column(String)
    previous_hash = Column(String, nullable=True)
    current_hash = Column(String)

class Policy(Base):
    __tablename__ = "policies"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    content = Column(Text)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
