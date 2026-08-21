from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.db.models import Scenario, Transaction
from secureflow.api.schemas import ScenarioRunRequest, PaymentAnalysisRequest, PaymentAnalysisResponse
from secureflow.api.routes.payments import analyze_payment
from secureflow.scenarios.attack_simulator import BENCHMARK_SCENARIOS

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

# Dynamically construct lookup map from BENCHMARK_SCENARIOS
BENCHMARK_MAP = {
    sc["scenario_id"].strip().upper(): sc["input"]
    for sc in BENCHMARK_SCENARIOS
}

@router.post("/run", response_model=PaymentAnalysisResponse)
def run_benchmark_scenario(
    payload: ScenarioRunRequest,
    db: Session = Depends(get_db_session)
):
    """Executes a benchmark attack or legitimate test scenario by scenario ID."""
    sc_id = payload.scenario_id.strip().upper()

    # 1. Search in historical Transaction database table
    txn = db.query(Transaction).filter(Transaction.scenario_id == sc_id).first()
    if txn:
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

    # 2. Search in BENCHMARK_SCENARIOS definitions
    if sc_id in BENCHMARK_MAP:
        inp = BENCHMARK_MAP[sc_id]
        req = PaymentAnalysisRequest(
            customer_id=inp["customer_id"],
            amount=inp["amount"],
            recipient_id=inp["recipient_id"],
            claimed_merchant=inp.get("claimed_merchant"),
            payment_note=inp.get("payment_note"),
            url=inp.get("url"),
            channel=inp.get("channel", "UPI")
        )
        return analyze_payment(req, db)

    # 3. Search in Scenario entity table
    sc = db.query(Scenario).filter(Scenario.scenario_id == sc_id).first()
    if sc and hasattr(sc, "input_data") and sc.input_data:
        inp = sc.input_data
        req = PaymentAnalysisRequest(
            customer_id=inp.get("customer_id", "CUST-001"),
            amount=inp.get("amount", 1000.00),
            recipient_id=inp.get("recipient_id", "RCP-001"),
            claimed_merchant=inp.get("claimed_merchant"),
            payment_note=inp.get("payment_note"),
            url=inp.get("url"),
            channel=inp.get("channel", "UPI")
        )
        return analyze_payment(req, db)

    # 4. If scenario ID is not found in any source -> Raise HTTP 404 (NO SILENT FALLBACK TO ANOTHER SCENARIO)
    raise HTTPException(
        status_code=404,
        detail=f"Scenario '{payload.scenario_id}' not found."
    )
