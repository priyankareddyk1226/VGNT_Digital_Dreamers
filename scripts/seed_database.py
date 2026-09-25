import os
import sys
import random
import json
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.database import SessionLocal, engine, Base
from app.models.domain import User, Parcel, Owner, ParcelOwner, Transaction, Anomaly, Policy
import app.models.domain

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(Parcel).count() > 0:
        print("Database already seeded. Skipping.")
        return

    print("Seeding synthetic data...")

    # Create admin user
    admin = User(
        username="admin",
        email="admin@bharatland.gov.in",
        hashed_password="hashed_password_demo",
        role="ADMIN"
    )
    db.add(admin)

    # Generate Owners
    owners = []
    first_names = ["Ramesh", "Suresh", "Lakshmi", "Priya", "Anil", "Sunita", "Rajesh", "Kavita", "Govind", "Meena"]
    last_names = ["Kumar", "Sharma", "Reddy", "Patel", "Singh", "Rao", "Naidu", "Verma", "Das", "Yadav"]
    
    for i in range(300):
        owner = Owner(
            full_name=f"{random.choice(first_names)} {random.choice(last_names)}",
            contact_info=f"contact_{i}@synthetic.demo",
            is_government=False
        )
        owners.append(owner)
        db.add(owner)
    
    gov_owner = Owner(
        full_name="State Government",
        is_government=True
    )
    owners.append(gov_owner)
    db.add(gov_owner)

    db.commit()

    # Generate Parcels
    districts = ["Hyderabad", "Ranga Reddy", "Medchal", "Sangareddy"]
    villages = ["Madhapur", "Gachibowli", "Kondapur", "Shamshabad", "Miyapur"]
    
    parcels = []
    
    # Create the WOW case P-0001
    p0001 = Parcel(
        id="P-0001",
        survey_number="SY-101-WOW",
        district="Hyderabad",
        village="Madhapur",
        area=2.5,
        area_unit="Acres",
        land_type="Commercial",
        risk_score=87.0,
        risk_level="HIGH",
        verification_status="CONFLICT",
        geojson_geometry={
            "type": "Polygon",
            "coordinates": [[[78.38, 17.44], [78.39, 17.44], [78.39, 17.45], [78.38, 17.45], [78.38, 17.44]]]
        }
    )
    db.add(p0001)
    parcels.append(p0001)
    
    # Assign owners to P-0001
    db.add(ParcelOwner(parcel_id=p0001.id, owner_id=owners[0].id, share_percentage=100.0))
    
    # Create Anomalies for P-0001
    anomalies = [
        Anomaly(parcel_id=p0001.id, rule_id="RULE-LR-007", severity="HIGH", message="Spatial overlap with P-0002 by 12.4%", confidence=0.95, evidence={"overlap_area": 0.31}),
        Anomaly(parcel_id=p0001.id, rule_id="RULE-LR-004", severity="HIGH", message="Mutation date differs from registration date by 3 years.", confidence=0.99, evidence={}),
        Anomaly(parcel_id=p0001.id, rule_id="RULE-LR-010", severity="MEDIUM", message="OCR confidence for survey number is 71%.", confidence=0.8, evidence={}),
        Anomaly(parcel_id=p0001.id, rule_id="RULE-LR-008", severity="CRITICAL", message="Ownership chain contains an unresolved transition.", confidence=0.9, evidence={})
    ]
    db.add_all(anomalies)

    # Generate 1000 standard parcels (starting from 2 to 1000)
    for i in range(2, 1001):
        parcel = Parcel(
            id=f"P-{str(i).zfill(4)}",
            survey_number=f"SY-{random.randint(100, 999)}",
            district=random.choice(districts),
            village=random.choice(villages),
            area=round(random.uniform(0.1, 10.0), 2),
            area_unit="Acres",
            land_type=random.choice(["Agricultural", "Residential", "Commercial"]),
            risk_score=random.uniform(0, 30) if random.random() > 0.1 else random.uniform(50, 90),
            verification_status=random.choice(["VERIFIED", "PENDING"])
        )
        if parcel.risk_score > 80:
            parcel.risk_level = "CRITICAL"
        elif parcel.risk_score > 60:
            parcel.risk_level = "HIGH"
        elif parcel.risk_score > 30:
            parcel.risk_level = "MEDIUM"
        else:
            parcel.risk_level = "LOW"
            
        parcels.append(parcel)
        db.add(parcel)
        
        # Add owner
        db.add(ParcelOwner(parcel_id=parcel.id, owner_id=random.choice(owners).id, share_percentage=100.0))

    db.commit()
    
    # Generate Policies
    policy = Policy(
        title="Land Mutation Guidelines 2024",
        content="This is a synthetic policy document. According to the guidelines, mutation must happen within 30 days of registration...",
        category="Guidelines"
    )
    db.add(policy)
    db.commit()

    print(f"Seeded {len(parcels)} parcels, {len(owners)} owners, and 1 policy.")
    
if __name__ == "__main__":
    seed_data()
