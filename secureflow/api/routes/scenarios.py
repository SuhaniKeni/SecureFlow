from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.db.models import Scenario, Transaction
from secureflow.api.schemas import ScenarioRunRequest, PaymentAnalysisRequest, PaymentAnalysisResponse
from secureflow.api.routes.payments import analyze_payment

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.post("/run", response_model=PaymentAnalysisResponse)
def run_benchmark_scenario(
    payload: ScenarioRunRequest,
    db: Session = Depends(get_db_session)
):
    """Executes a benchmark attack or legitimate test scenario by scenario ID."""
    sc = db.query(Scenario).filter(Scenario.scenario_id == payload.scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail=f"Scenario '{payload.scenario_id}' not found.")

    # Find benchmark transaction linked to this scenario
    txn = db.query(Transaction).filter(Transaction.scenario_id == payload.scenario_id).first()
    if not txn:
        # Fallback benchmark mapping
        req = PaymentAnalysisRequest(
            customer_id="CUST-001",
            amount=8742.00,
            recipient_id="RCP-004",
            claimed_merchant="BESCOM Electricity",
            payment_note="URGENT: Disconnection notice",
            url="http://elect-pay-bill.top/pay"
        )
        return analyze_payment(req, db)

    req_obj = txn.payment_request
    req = PaymentAnalysisRequest(
        customer_id=txn.customer_id,
        amount=txn.amount,
        recipient_id=txn.recipient_id,
        claimed_merchant=req_obj.claimed_merchant if req_obj else "Payee",
        payment_note=req_obj.message if req_obj else None,
        url=req_obj.url if req_obj else None,
        channel=txn.channel or "UPI"
    )
    return analyze_payment(req, db)
