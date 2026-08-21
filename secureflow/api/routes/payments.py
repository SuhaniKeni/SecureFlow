import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.db.models import Transaction, PaymentRequest, ProtectionEvent, Recipient, Customer
from secureflow.engines.url_intel_engine import URLIntelligenceEngine
from secureflow.engines.scam_nlp_engine import ScamContextNLPEngine
from secureflow.engines.behavior_engine import CustomerBehaviorEngine
from secureflow.engines.merchant_engine import MerchantConsistencyEngine
from secureflow.aggregation.evidence_aggregator import EvidenceAggregator
from secureflow.policy.decision_engine import ProtectionDecisionEngine
from secureflow.explanations.explanation_engine import ExplanationEngine
from secureflow.api.schemas import PaymentAnalysisRequest, PaymentSimulationRequest, PaymentAnalysisResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

# Lazy engine initializations
url_engine = URLIntelligenceEngine()
nlp_engine = ScamContextNLPEngine()
behavior_engine = CustomerBehaviorEngine()
merchant_engine = MerchantConsistencyEngine()
aggregator = EvidenceAggregator()
decision_engine = ProtectionDecisionEngine()
explanation_engine = ExplanationEngine()

@router.post("/analyze", response_model=PaymentAnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_payment(
    payload: PaymentAnalysisRequest,
    db: Session = Depends(get_db_session)
):
    """Executes end-to-end adaptive security evaluation across all 4 detection engines."""
    # 1. Run 4 Detection Engines
    url_ev = url_engine.analyze(payload.url)
    nlp_ev = nlp_engine.analyze(payload.payment_note, claimed_merchant=payload.claimed_merchant)
    behavior_ev = behavior_engine.analyze_transaction(
        customer_id=payload.customer_id,
        amount=payload.amount,
        recipient_id=payload.recipient_id,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        db_session=db
    )
    merchant_ev = merchant_engine.analyze_consistency(
        claimed_merchant=payload.claimed_merchant,
        recipient_id=payload.recipient_id,
        destination_url=payload.url,
        db_session=db
    )

    # 2. Evidence Fusion & Aggregation
    bundle = aggregator.aggregate(
        url_evidence=url_ev,
        nlp_evidence=nlp_ev,
        behavior_evidence=behavior_ev,
        merchant_evidence=merchant_ev
    )

    # 3. Deterministic Policy Decision Engine
    decision = decision_engine.evaluate_protection_policy(bundle)

    # 4. Generate Dual-Mode Explanations
    tx_ctx = {"amount": payload.amount, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    m_info = {"claimed_merchant": payload.claimed_merchant, "actual_recipient_name": merchant_ev["consistency_details"].get("actual_recipient_name")}
    
    explanations = explanation_engine.generate_explanation(
        protection_action=decision["action"],
        evidence_bundle=bundle,
        transaction_context=tx_ctx,
        merchant_info=m_info
    )

    # 5. Persist Transaction & Protection Event Audit Trail
    t_id = f"TXN-LIVE-{uuid.uuid4().hex[:10].upper()}"
    new_txn = Transaction(
        transaction_id=t_id,
        customer_id=payload.customer_id,
        recipient_id=payload.recipient_id,
        amount=payload.amount,
        currency="INR",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        channel=payload.channel,
        status="SUCCESS" if decision["action"] == "ALLOW" else ("HELD" if decision["action"] == "HOLD" else ("BLOCKED" if decision["action"] == "BLOCK" else "VERIFY_REQUIRED"))
    )
    db.add(new_txn)

    new_req = PaymentRequest(
        request_id=f"REQ-{uuid.uuid4().hex[:10].upper()}",
        transaction_id=t_id,
        message=payload.payment_note or "Payment request",
        claimed_merchant=payload.claimed_merchant or "Payee",
        url=payload.url,
        source_channel=payload.channel
    )
    db.add(new_req)

    new_evt = ProtectionEvent(
        event_id=f"EVT-{uuid.uuid4().hex[:10].upper()}",
        transaction_id=t_id,
        action=decision["action"],
        evidence=bundle,
        explanation=explanations["customer_explanation"]["why"]
    )
    db.add(new_evt)
    db.commit()

    return PaymentAnalysisResponse(
        transaction_id=t_id,
        action=decision["action"],
        reasons=decision["reasons"],
        customer_explanation=explanations["customer_explanation"],
        ops_explanation=explanations["ops_explanation"],
        evidence_bundle=bundle,
        recommended_next_step=decision["recommended_next_step"],
        prevention_recommendation=decision["prevention_recommendation"],
        audit_trail=decision["audit_trail"]
    )

@router.post("/simulate", response_model=PaymentAnalysisResponse)
def simulate_payment(
    payload: PaymentSimulationRequest,
    db: Session = Depends(get_db_session)
):
    """Sandbox simulation endpoint for customer payment UI testing."""
    req = PaymentAnalysisRequest(
        customer_id=payload.customer_id or "CUST-001",
        amount=payload.amount or 8742.00,
        recipient_id=payload.recipient_id or "RCP-004",
        claimed_merchant=payload.claimed_merchant or "BESCOM Electricity",
        payment_note=payload.payment_note or "URGENT: Electricity disconnection notice",
        url=payload.url or "http://elect-pay-bill.top/pay"
    )
    return analyze_payment(req, db)

@router.get("/{transaction_id}")
def get_payment_by_id(transaction_id: str, db: Session = Depends(get_db_session)):
    """Retrieves payment details by transaction ID."""
    txn = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")

    req = txn.payment_request
    rcp = txn.recipient

    return {
        "transaction_id": txn.transaction_id,
        "customer_id": txn.customer_id,
        "amount": txn.amount,
        "currency": txn.currency,
        "status": txn.status,
        "timestamp": txn.timestamp.isoformat(),
        "recipient": {
            "recipient_id": rcp.recipient_id,
            "display_name": rcp.display_name,
            "verified_identity": rcp.verified_identity
        },
        "payment_request": {
            "claimed_merchant": req.claimed_merchant if req else None,
            "message": req.message if req else None,
            "url": req.url if req else None
        }
    }
