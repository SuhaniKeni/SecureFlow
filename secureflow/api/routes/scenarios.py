from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.db.models import Scenario, Transaction
from secureflow.api.schemas import ScenarioRunRequest, PaymentAnalysisRequest, PaymentAnalysisResponse
from secureflow.api.routes.payments import analyze_payment

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

BENCHMARK_SCENARIO_PAYLOADS = {
    "SCN-001": PaymentAnalysisRequest(customer_id="CUST-001", amount=1450.00, recipient_id="RCP-001", claimed_merchant="BESCOM Electricity", payment_note="Monthly electricity bill payment ref #10492", url="https://bescom.co.in/pay", channel="UPI"),
    "SCN-002": PaymentAnalysisRequest(customer_id="CUST-001", amount=8742.00, recipient_id="RCP-004", claimed_merchant="BESCOM Electricity Board", payment_note="URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately", url="http://elect-pay-bill.top/pay", channel="UPI"),
    "SCN-003": PaymentAnalysisRequest(customer_id="CUST-001", amount=15000.00, recipient_id="RCP-004", claimed_merchant="HDFC Bank Online", payment_note="IMPORTANT: Your HDFC Bank account will be suspended. Update KYC details immediately", url="http://bank-kyc-update.online/hdfc", channel="UPI"),
    "SCN-004": PaymentAnalysisRequest(customer_id="CUST-001", amount=1499.00, recipient_id="RCP-004", claimed_merchant="India Post Courier", payment_note="Package delivery on hold due to missing customs clearance fee", url="http://customs-clearance-pay.com/track", channel="UPI"),
    "SCN-005": PaymentAnalysisRequest(customer_id="CUST-001", amount=199.00, recipient_id="RCP-004", claimed_merchant="Customer Support Portal", payment_note="Pay Rs 199 registration charge for instant Rs 15,000 refund processing", url="http://refund-support-portal.site/verify", channel="UPI"),
    "SCN-006": PaymentAnalysisRequest(customer_id="CUST-001", amount=850.00, recipient_id="RCP-004", claimed_merchant="Income Tax Department", payment_note="Income tax refund approved. Pay fee to release Rs 45,000 credit", url="http://incometax-refund-gov.in.net/pay", channel="UPI"),
    "SCN-007": PaymentAnalysisRequest(customer_id="CUST-001", amount=85000.00, recipient_id="RCP-002", claimed_merchant="Amazon India", payment_note="Payment for Apple Laptop order #940182 via Amazon Pay", url="https://amazon.in/checkout/pay", channel="UPI"),
    "SCN-008": PaymentAnalysisRequest(customer_id="CUST-002", amount=3200.00, recipient_id="RCP-003", claimed_merchant="Local Hardware Store", payment_note="Purchase of construction tools", url="https://sbi.co.in/portal/pay", channel="UPI"),
    "SCN-009": PaymentAnalysisRequest(customer_id="CUST-001", amount=4500.00, recipient_id="RCP-004", claimed_merchant="City Municipal Utility", payment_note="Water bill clearance", url="http://elect-pay-bill.top/pay", channel="UPI"),
    "SCN-010": PaymentAnalysisRequest(customer_id="CUST-001", amount=12450.00, recipient_id="RCP-004", claimed_merchant="BESCOM Electricity", payment_note="Electricity tariff clearance", url="https://bescom.co.in/pay", channel="UPI"),
}

@router.post("/run", response_model=PaymentAnalysisResponse)
def run_benchmark_scenario(
    payload: ScenarioRunRequest,
    db: Session = Depends(get_db_session)
):
    """Executes a benchmark attack or legitimate test scenario by scenario ID."""
    sc_id = payload.scenario_id.upper()
    
    # Check if exact benchmark mapping exists
    if sc_id in BENCHMARK_SCENARIO_PAYLOADS:
        return analyze_payment(BENCHMARK_SCENARIO_PAYLOADS[sc_id], db)

    # Fallback to DB transaction lookup if present
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

    # Check scenario entity
    sc = db.query(Scenario).filter(Scenario.scenario_id == sc_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail=f"Scenario '{sc_id}' not found.")

    # Ultimate fallback payload
    default_req = PaymentAnalysisRequest(
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        claimed_merchant="BESCOM Electricity",
        payment_note="URGENT: Disconnection notice",
        url="http://elect-pay-bill.top/pay"
    )
    return analyze_payment(default_req, db)
