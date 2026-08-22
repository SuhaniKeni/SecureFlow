import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.agents.schemas import AgentExecutionRequest
from secureflow.agents.orchestrator import SecurityOrchestrator
from secureflow.api.schemas import PaymentAnalysisRequest, SecurityPipelineResponse

router = APIRouter(prefix="/security", tags=["Agentic Security Pipeline"])

@router.post("/analyze", response_model=SecurityPipelineResponse, status_code=status.HTTP_200_OK)
def analyze_payment_security_pipeline(
    payload: PaymentAnalysisRequest,
    db: Session = Depends(get_db_session)
):
    """Executes full end-to-end SecureFlow Agentic Security Pipeline.
    
    Flow:
      Detection Engines -> Merchant Security Agent -> Investigation Agent -> Evidence Synthesis -> Deterministic Policy -> Response Agent.
    """
    transaction_id = f"TXN-LIVE-{uuid.uuid4().hex[:10].upper()}"
    
    agent_request = AgentExecutionRequest(
        agent_id="security_orchestrator",
        transaction_id=transaction_id,
        customer_id=payload.customer_id,
        amount=payload.amount,
        recipient_id=payload.recipient_id,
        claimed_merchant=payload.claimed_merchant,
        payment_note=payload.payment_note,
        url=payload.url,
        channel=payload.channel
    )

    orchestrator = SecurityOrchestrator(db_session=db)
    result = orchestrator.run_pipeline(agent_request, db_session=db)

    return SecurityPipelineResponse(
        transaction_id=result["transaction_id"],
        execution_id=result["execution_id"],
        action=result["action"],
        customer_explanation=result["customer_explanation"],
        ops_explanation=result["ops_explanation"],
        evidence_bundle=result["evidence_bundle"],
        protection_response=result["protection_response"],
        execution_trace=result["execution_trace"],
        total_latency_ms=result["total_latency_ms"],
        audit_trail=result["audit_trail"]
    )
