from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from secureflow.db.database import get_db_session
from secureflow.db.models import Merchant, Customer, Transaction
from secureflow.api.schemas import MerchantResponse, CustomerHistoryResponse

router = APIRouter(tags=["Entities"])

@router.get("/merchants/{merchant_id}", response_model=MerchantResponse)
def get_merchant_by_id(merchant_id: str, db: Session = Depends(get_db_session)):
    """Retrieves verified merchant profile by merchant ID."""
    m = db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()
    if not m:
        raise HTTPException(status_code=404, detail=f"Merchant '{merchant_id}' not found.")

    return MerchantResponse(
        merchant_id=m.merchant_id,
        legal_name=m.legal_name,
        brand_name=m.brand_name,
        category=m.category,
        verified_domain=m.verified_domain,
        verified_payment_identifier=m.verified_payment_identifier,
        account_age_days=m.account_age_days,
        status=m.status
    )

@router.get("/customers/{customer_id}/history", response_model=CustomerHistoryResponse)
def get_customer_history(customer_id: str, db: Session = Depends(get_db_session)):
    """Retrieves customer baseline profile and historical transaction log."""
    c = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")

    txns = db.query(Transaction).filter(Transaction.customer_id == customer_id).order_by(Transaction.timestamp.desc()).all()
    
    history_list = []
    for t in txns:
        history_list.append({
            "transaction_id": t.transaction_id,
            "amount": t.amount,
            "recipient_id": t.recipient_id,
            "recipient_name": t.recipient.display_name if t.recipient else "Recipient",
            "status": t.status,
            "timestamp": t.timestamp.isoformat()
        })

    return CustomerHistoryResponse(
        customer_id=c.customer_id,
        full_name=c.full_name,
        email=c.email,
        normal_avg_amount=c.normal_avg_amount,
        normal_std_amount=c.normal_std_amount,
        account_age_days=c.account_age_days,
        total_transactions=len(history_list),
        transaction_history=history_list
    )
