from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.domain import Parcel, Policy
import json, re

router = APIRouter()

# Hardcoded policy knowledge base for RAG-style AI assistant
POLICY_KNOWLEDGE = [
    {
        "id": "land-ceiling",
        "title": "Land Ceiling Act",
        "content": """The Land Ceiling Act limits the maximum agricultural land a person or family can hold. 
        In most states, this is between 10-54 acres depending on land type and family size. 
        Violations trigger automatic flagging for investigation. Key thresholds: 
        - Dry land: up to 54 acres per family
        - Irrigated land: up to 27 acres per family  
        - Double-crop irrigated: up to 18 acres per family
        Excess land is subject to acquisition by the state government."""
    },
    {
        "id": "mutation-process",
        "title": "Land Mutation Process",
        "content": """Land mutation (Intkal/Dakhil Kharij) is the process of updating land records when ownership changes. 
        Required documents: Sale deed, NOC from relevant authority, ID proof, existing Patta/ROR (Record of Rights).
        Process: Apply at Tehsil/Mandal office → Field verification → Revenue officer approval → Record update.
        Timeline: 30-90 days depending on state. Online mutation available in Telangana (Dharani Portal), 
        Maharashtra (Mahabhulekh), AP (Meebhoomi)."""
    },
    {
        "id": "encumbrance-cert",
        "title": "Encumbrance Certificate",
        "content": """Encumbrance Certificate (EC) records all registered transactions on a property. 
        It proves the property is free from mortgages, liens, and legal disputes. 
        Required for: home loans, property purchase, mutation. 
        Available from Sub-Registrar office or online portals (KAVERI in Karnataka, EC Online in Telangana).
        Form 15: property has transactions. Form 16: no encumbrance found."""
    },
    {
        "id": "benami-prohibition",
        "title": "Benami Transactions Prohibition",
        "content": """The Prohibition of Benami Property Transactions Act 1988 (amended 2016) prohibits 
        holding property in the name of another person (benamidar). Penalties include up to 7 years 
        imprisonment and 25% fine on fair market value. 
        Common flags: price significantly below market value, third-party payments, no clear consideration.
        Enforcement: Income Tax Department's Benami Prohibition Unit."""
    },
    {
        "id": "forest-land",
        "title": "Forest Land Regulations",
        "content": """Forest (Conservation) Act 1980 prohibits diversion of forest land for non-forest use 
        without central government approval. Land within 10km of forest boundary requires special clearance.
        Violations lead to demolition orders and criminal prosecution.
        The Forest Rights Act 2006 recognizes tribal rights over forest land."""
    },
    {
        "id": "stamp-duty",
        "title": "Stamp Duty & Registration",
        "content": """Stamp duty is levied on property registration. Rates vary by state: 
        Telangana: 4% (urban), 1% (rural). Maharashtra: 5%. Karnataka: 3-5%. AP: 4%.
        Sub-registrar registration is mandatory for property > Rs. 100.
        Circle rate (guidance value) is the minimum value for stamp duty calculation.
        Undervaluation is detected by comparing sale price vs circle rate."""
    },
    {
        "id": "digitization",
        "title": "Land Record Digitization Schemes",
        "content": """DILRMP (Digital India Land Records Modernization Programme) aims to digitize all land records.
        Completed in: Telangana (Dharani), Gujarat (e-Dhara), Karnataka (Bhoomi), AP (Meebhoomi).
        Cadastral maps being digitized under SVAMITVA scheme for rural areas.
        Aadhaar seeding of land records underway to prevent duplication."""
    },
    {
        "id": "anomaly-detection",
        "title": "Anomaly Detection in Land Records",
        "content": """Common land record anomalies detected by AI systems:
        1. Overlapping ownership (same survey number, multiple owners)
        2. Rapid successive transfers (land flipping)
        3. Price anomalies (sale price < 50% of circle rate)
        4. Boundary disputes (GPS mismatch with records)
        5. Missing mutation after sale deed registration
        6. Encroachment on government/forest land
        7. Benami indicators (third-party payments, proxy ownership)"""
    },
]

@router.post("/query")
def ai_query(request: dict, db: Session = Depends(get_db)):
    """Keyword-based RAG AI assistant for land governance queries."""
    query = request.get("query", "").lower().strip()
    if not query:
        return {"answer": "Please provide a query.", "sources": [], "parcels": []}
    
    # Simple keyword matching RAG
    scored_docs = []
    query_words = set(re.findall(r'\w+', query))
    
    for doc in POLICY_KNOWLEDGE:
        doc_words = set(re.findall(r'\w+', doc["title"].lower() + " " + doc["content"].lower()))
        score = len(query_words & doc_words)
        if score > 0:
            scored_docs.append((score, doc))
    
    scored_docs.sort(key=lambda x: -x[0])
    top_docs = [d for _, d in scored_docs[:3]]
    
    # Build answer
    if top_docs:
        primary = top_docs[0]
        answer_parts = [f"**{primary['title']}**\n\n{primary['content']}"]
        if len(top_docs) > 1:
            answer_parts.append(f"\n\n**Related: {top_docs[1]['title']}**\n{top_docs[1]['content'][:300]}...")
    else:
        answer_parts = [
            "I couldn't find specific policy information for your query. "
            "Please try rephrasing or ask about: land ceiling, mutation, encumbrance certificates, "
            "benami transactions, stamp duty, forest land, or land record digitization."
        ]
    
    # Check if query is about a specific parcel
    parcel_mentions = []
    survey_match = re.search(r'(SY-\w+|survey\s+(?:number\s+)?(\w+))', query, re.IGNORECASE)
    if survey_match:
        parcels = db.query(Parcel).filter(
            Parcel.survey_number.ilike(f"%{survey_match.group(0)[:10]}%")
        ).limit(3).all()
        parcel_mentions = [
            {"id": p.id, "survey_number": p.survey_number, "district": p.district, "risk_level": p.risk_level}
            for p in parcels
        ]
    
    return {
        "answer": "\n".join(answer_parts),
        "sources": [{"id": d["id"], "title": d["title"]} for d in top_docs],
        "parcels": parcel_mentions,
        "query": query,
    }

@router.get("/policies")
def list_policies():
    """List all available policy documents."""
    return [{"id": p["id"], "title": p["title"], "preview": p["content"][:150] + "..."} for p in POLICY_KNOWLEDGE]
