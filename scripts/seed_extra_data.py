"""Seed additional demo data: anomalies and audit events for all 1000 parcels."""
import sys, os, random, hashlib
from datetime import datetime, timedelta

# Set correct DB path before importing app modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "land_intelligence.db")
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))
from app.database import SessionLocal
from app.models.domain import Parcel, Anomaly, AuditEvent

db = SessionLocal()

# ─── Generate more anomalies ─────────────────────────────────────
RULES = [
    ("RULE-001", "Rapid successive transfers detected — possible land flipping"),
    ("RULE-002", "Sale price significantly below circle rate — undervaluation indicator"),
    ("RULE-003", "Overlapping ownership claim with adjacent parcel"),
    ("RULE-004", "Missing mutation record after registered sale deed"),
    ("RULE-005", "Boundary overlap with government/forest land"),
    ("RULE-006", "Multiple ownership changes within 90 days — benami indicator"),
    ("RULE-007", "Area mismatch between revenue records and GIS measurement"),
    ("RULE-008", "Encroachment detected — construction beyond approved boundary"),
    ("RULE-009", "Land use violation — agricultural land used for commercial purpose"),
    ("RULE-010", "Duplicate survey number detected across villages"),
]

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SEVERITY_WEIGHTS = [0.05, 0.15, 0.30, 0.30, 0.20]

parcels = db.query(Parcel).all()
existing_anomaly_count = db.query(Anomaly).count()

print(f"Found {len(parcels)} parcels, {existing_anomaly_count} existing anomalies")

new_anomalies = 0
for parcel in parcels:
    # ~30% chance of having an anomaly
    if random.random() < 0.30:
        num_anomalies = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        rules_used = random.sample(RULES, min(num_anomalies, len(RULES)))
        for rule_id, message in rules_used:
            severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
            confidence = round(random.uniform(0.55, 0.99), 2)
            days_ago = random.randint(1, 180)
            
            anomaly = Anomaly(
                parcel_id=parcel.id,
                rule_id=rule_id,
                severity=severity,
                message=message,
                evidence={"parcel_id": parcel.id, "survey_number": parcel.survey_number, "rule": rule_id},
                confidence=confidence,
                detected_at=datetime.utcnow() - timedelta(days=days_ago),
            )
            db.add(anomaly)
            new_anomalies += 1

db.commit()
print(f"Created {new_anomalies} new anomalies")

# ─── Generate audit events with cryptographic chain ──────────────
AUDIT_ACTIONS = [
    ("PARCEL_CREATED", "CREATE", "System Seed"),
    ("PARCEL_VERIFIED", "VERIFY", "Revenue Officer Sharma"),
    ("ANOMALY_DETECTED", "FLAG", "ML Pipeline v2.1"),
    ("DOCUMENT_PROCESSED", "OCR", "OCR Engine"),
    ("OWNERSHIP_CHANGED", "MUTATION", "Tehsildar Reddy"),
    ("RISK_RECALCULATED", "COMPUTE", "Risk Engine v3.0"),
    ("BOUNDARY_UPDATED", "GIS_UPDATE", "GIS Surveyor Patel"),
    ("VERIFICATION_REQUESTED", "REQUEST", "District Collector"),
]

previous_hash = None
new_events = 0

for parcel in random.sample(parcels, min(200, len(parcels))):
    num_events = random.choices([1, 2, 3, 4], weights=[0.4, 0.3, 0.2, 0.1])[0]
    for _ in range(num_events):
        event_type, action, actor = random.choice(AUDIT_ACTIONS)
        days_ago = random.randint(1, 365)
        
        data_hash = hashlib.sha256(
            f"{parcel.id}:{event_type}:{datetime.utcnow().isoformat()}:{random.random()}".encode()
        ).hexdigest()
        
        payload = f"{event_type}:{parcel.id}:{actor}:{action}:{data_hash}:{previous_hash}"
        current_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        event = AuditEvent(
            event_type=event_type,
            record_id=parcel.id,
            actor=actor,
            action=action,
            timestamp=datetime.utcnow() - timedelta(days=days_ago),
            data_hash=data_hash,
            previous_hash=previous_hash,
            current_hash=current_hash,
        )
        db.add(event)
        previous_hash = current_hash
        new_events += 1

db.commit()
db.close()
print(f"Created {new_events} audit events")
print("Done!")
