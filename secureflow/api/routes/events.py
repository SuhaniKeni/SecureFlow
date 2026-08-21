from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.db.models import ProtectionEvent, Transaction
from secureflow.api.schemas import ProtectionEventSummary

router = APIRouter(prefix="/protection-events", tags=["Protection Events"])

@router.get("", response_model=List[ProtectionEventSummary])
def list_protection_events(
    action: Optional[str] = Query(None, description="Filter by action: ALLOW, VERIFY, HOLD, BLOCK"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session)
):
    """Lists historical protection events for Risk Operations Dashboard."""
    query = db.query(ProtectionEvent)
    if action:
        query = query.filter(ProtectionEvent.action == action.upper())

    events = query.order_by(ProtectionEvent.timestamp.desc()).offset(offset).limit(limit).all()
    
    res = []
    for evt in events:
        res.append(ProtectionEventSummary(
            event_id=evt.event_id,
            transaction_id=evt.transaction_id,
            action=evt.action,
            evidence=evt.evidence if isinstance(evt.evidence, dict) else {},
            explanation=evt.explanation,
            timestamp=evt.timestamp.isoformat()
        ))
    return res

@router.get("/{event_id}", response_model=ProtectionEventSummary)
def get_protection_event_by_id(event_id: str, db: Session = Depends(get_db_session)):
    """Retrieves full forensic details of a single protection event by ID."""
    evt = db.query(ProtectionEvent).filter(ProtectionEvent.event_id == event_id).first()
    if not evt:
        raise HTTPException(status_code=404, detail=f"Protection event '{event_id}' not found.")

    return ProtectionEventSummary(
        event_id=evt.event_id,
        transaction_id=evt.transaction_id,
        action=evt.action,
        evidence=evt.evidence if isinstance(evt.evidence, dict) else {},
        explanation=evt.explanation,
        timestamp=evt.timestamp.isoformat()
    )
