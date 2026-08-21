from typing import Dict, Any, List

SUSPICIOUS_TLDS = [".top", ".online", ".site", ".info", ".xyz", ".club", ".live", ".tech", ".in.net"]
SCAM_KEYWORDS = ["disconnected", "suspended", "customs duty", "income tax refund", "e-challan", "police summons", "penalty"]
KNOWN_RECIPIENTS = {"RCP-001", "RCP-002"}

class BaselinePolicyEngine:
    """Conventional Rule-Based Payment Protection Baseline Engine.
    
    Operates independently of SecureFlow ML models and evidence aggregators.
    """

    def evaluate_payment(self, payment_request: Dict[str, Any]) -> Dict[str, Any]:
        amount = float(payment_request.get("amount", 0.0))
        recipient_id = str(payment_request.get("recipient_id", ""))
        claimed_merchant = str(payment_request.get("claimed_merchant", "")).lower()
        payment_note = str(payment_request.get("payment_note", "")).lower()
        url = str(payment_request.get("url", "")).lower()

        reasons = []

        # Check 1: Suspicious URL / TLD
        has_suspicious_tld = any(tld in url for tld in SUSPICIOUS_TLDS)
        
        # Check 2: Scam keyword presence in payment note
        has_scam_kw = any(kw in payment_note for kw in SCAM_KEYWORDS)

        # Baseline Rule 1: BLOCK if suspicious domain or scam threat keyword detected
        if has_suspicious_tld or has_scam_kw:
            reasons.append("Conventional Baseline Rule: Suspicious domain or scam keyword detected.")
            return {
                "action": "BLOCK",
                "reasons": reasons,
                "engine": "BaselineRuleEngine"
            }

        # Baseline Rule 2: VERIFY if high-value transaction or new recipient
        is_new_recipient = recipient_id not in KNOWN_RECIPIENTS
        if (amount > 10000.0 and is_new_recipient) or (amount > 50000.0):
            reasons.append("Conventional Baseline Rule: High-value payment or unverified recipient.")
            return {
                "action": "VERIFY",
                "reasons": reasons,
                "engine": "BaselineRuleEngine"
            }

        # Baseline Rule 3: ALLOW
        return {
            "action": "ALLOW",
            "reasons": ["Conventional Baseline Rule: Transaction within normal thresholds."],
            "engine": "BaselineRuleEngine"
        }
