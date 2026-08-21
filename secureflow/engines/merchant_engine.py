import os
import difflib
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from secureflow.db.models import Merchant, Recipient

def token_jaccard_similarity(str1: str, str2: str) -> float:
    """Calculates token-based Jaccard similarity between two strings."""
    if not str1 or not str2:
        return 0.0
    tokens1 = set(re_tokenize(str1))
    tokens2 = set(re_tokenize(str2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)

def re_tokenize(text: str) -> List[str]:
    import re
    return [t.lower() for t in re.findall(r'\b\w+\b', text) if len(t) > 1]

class MerchantConsistencyEngine:
    """Engine for verifying merchant and recipient identity consistency.
    
    Evaluates claimed merchant names, legal entity names, brand names, verified domains, 
    payment handles, and recipient account age.
    STRICT MANDATE: Never outputs financial block decisions ('BLOCK' / 'ALLOW').
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.session = db_session

    def analyze_consistency(
        self,
        claimed_merchant: Optional[str],
        recipient_id: str,
        destination_url: Optional[str] = None,
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Analyzes recipient identity, domain consistency, and claimed merchant alignment."""
        session = db_session or self.session
        if not session:
            return self._heuristic_fallback(claimed_merchant, recipient_id, destination_url)

        # 1. Fetch Recipient & Linked Merchant Profile
        recipient = session.query(Recipient).filter(Recipient.recipient_id == recipient_id).first()
        if not recipient:
            return {
                "signal": "unregistered_recipient",
                "risk_score": 0.70,
                "severity": "high",
                "consistency_details": {
                    "claimed_merchant": claimed_merchant or "Unknown",
                    "actual_recipient_name": "Unregistered Account",
                    "domain_match": False,
                    "is_verified_merchant": False,
                    "recipient_account_age_days": 0
                },
                "evidence": f"Recipient ID '{recipient_id}' is not registered in the system."
            }

        linked_merchant = recipient.linked_merchant
        actual_recipient_name = recipient.verified_identity or recipient.display_name or ""
        claimed_name = claimed_merchant or ""

        # 2. Multi-factor Entity Resolution
        # Token Jaccard + String Sequence Ratio
        seq_ratio = difflib.SequenceMatcher(None, claimed_name.lower(), actual_recipient_name.lower()).ratio()
        token_sim = token_jaccard_similarity(claimed_name, actual_recipient_name)
        combined_identity_score = max(seq_ratio, token_sim)

        # Check if claimed merchant matches linked merchant brand or legal name
        is_linked_match = False
        if linked_merchant:
            m_brand_sim = token_jaccard_similarity(claimed_name, linked_merchant.brand_name)
            m_legal_sim = token_jaccard_similarity(claimed_name, linked_merchant.legal_name)
            is_linked_match = (m_brand_sim > 0.4 or m_legal_sim > 0.4)

        # 3. Domain Consistency Verification
        domain_match = True
        domain_evidence_str = ""
        if destination_url and linked_merchant:
            verified_dom = linked_merchant.verified_domain.lower()
            dest_url_lower = destination_url.lower()
            if verified_dom not in dest_url_lower:
                domain_match = False
                domain_evidence_str = f" Destination URL domain does not match official domain '{verified_dom}'."
        elif destination_url and not linked_merchant:
            domain_match = False
            domain_evidence_str = " Payment destination URL is unverified for this personal recipient."

        # 4. Account Age & Status Assessment
        account_age = recipient.account_age_days
        is_new_recipient = account_age < 30
        is_verified = (linked_merchant is not None) and (linked_merchant.status == "VERIFIED")

        # 5. Inconsistency Detection & Signal Mapping
        if claimed_name and not is_linked_match and combined_identity_score < 0.35 and not is_verified:
            # High severity mismatch: Claimed utility/brand but funds go to unverified private individual
            signal = "merchant_identity_mismatch"
            severity = "high"
            risk_score = 0.95
            evidence_summary = (
                f"Claimed merchant '{claimed_name}' does not match actual account holder '{actual_recipient_name}' "
                f"(Account age: {account_age} days, Unverified destination).{domain_evidence_str}"
            )
        elif not domain_match:
            signal = "domain_mismatch"
            severity = "high" if not is_verified else "medium"
            risk_score = 0.80 if not is_verified else 0.50
            evidence_summary = f"Payment link domain mismatch detected for claimed merchant '{claimed_name}'.{domain_evidence_str}"
        elif is_new_recipient and not is_verified:
            signal = "newly_observed_recipient"
            severity = "medium"
            risk_score = 0.55
            evidence_summary = f"Recipient '{actual_recipient_name}' is a newly created account ({account_age} days old)."
        elif not is_verified:
            signal = "unverified_destination"
            severity = "medium"
            risk_score = 0.40
            evidence_summary = f"Recipient '{actual_recipient_name}' is not a verified business merchant."
        else:
            signal = "merchant_identity_match"
            severity = "low"
            risk_score = 0.05
            evidence_summary = f"Recipient '{actual_recipient_name}' matches verified merchant '{linked_merchant.brand_name}'."

        return {
            "signal": signal,
            "risk_score": round(risk_score, 4),
            "severity": severity,
            "consistency_details": {
                "claimed_merchant": claimed_name,
                "actual_recipient_name": actual_recipient_name,
                "registered_legal_name": linked_merchant.legal_name if linked_merchant else None,
                "brand_name": linked_merchant.brand_name if linked_merchant else None,
                "verified_domain": linked_merchant.verified_domain if linked_merchant else None,
                "domain_match": domain_match,
                "is_verified_merchant": is_verified,
                "recipient_account_age_days": account_age,
                "identity_similarity_score": round(combined_identity_score, 4)
            },
            "evidence": evidence_summary
        }

    def _heuristic_fallback(
        self,
        claimed_merchant: Optional[str],
        recipient_id: str,
        destination_url: Optional[str]
    ) -> Dict[str, Any]:
        """Fallback evaluation if database session is unavailable."""
        return {
            "signal": "unverified_destination",
            "risk_score": 0.50,
            "severity": "medium",
            "consistency_details": {
                "claimed_merchant": claimed_merchant or "Unknown",
                "actual_recipient_name": recipient_id,
                "domain_match": True if destination_url and "https" in destination_url else False,
                "is_verified_merchant": False,
                "recipient_account_age_days": 30
            },
            "evidence": f"Recipient '{recipient_id}' evaluated using fallback identity parameters."
        }
