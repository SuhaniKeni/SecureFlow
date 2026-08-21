import difflib
import pandas as pd
from sqlalchemy.orm import Session
from secureflow.db.models import Transaction, PaymentRequest, Recipient, Merchant

def compute_string_similarity(a: str, b: str) -> float:
    """Computes normalized string similarity ratio between 0.0 and 1.0."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def compute_merchant_features(session: Session) -> pd.DataFrame:
    """Computes merchant identity consistency features and mismatch indicators."""
    query = session.query(Transaction, PaymentRequest, Recipient).join(
        PaymentRequest, Transaction.transaction_id == PaymentRequest.transaction_id
    ).join(
        Recipient, Transaction.recipient_id == Recipient.recipient_id
    )

    records = []
    for txn, req, rcp in query.all():
        claimed = req.claimed_merchant or ""
        actual_identity = rcp.verified_identity or rcp.display_name or ""

        similarity = compute_string_similarity(claimed, actual_identity)
        # Mismatch if claimed merchant is specific (e.g. Electricity/Bank) but recipient identity is completely different
        is_mismatch = 1 if (similarity < 0.4 and claimed != "") else 0

        linked_merchant = rcp.linked_merchant
        is_verified = 1 if (linked_merchant and linked_merchant.status == "VERIFIED") else 0
        account_age = rcp.account_age_days

        records.append({
            "transaction_id": txn.transaction_id,
            "claimed_merchant": claimed,
            "actual_recipient_identity": actual_identity,
            "identity_similarity_score": round(similarity, 4),
            "is_identity_mismatch": is_mismatch,
            "recipient_account_age_days": account_age,
            "is_new_recipient": 1 if account_age < 30 else 0,
            "is_merchant_verified": is_verified
        })

    return pd.DataFrame(records)
