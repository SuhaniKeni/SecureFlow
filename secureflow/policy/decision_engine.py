import uuid
import datetime
from typing import Dict, Any, List

class ProtectionDecisionEngine:
    """Core Protection Decision Engine for SecureFlow.
    
    Evaluates aggregated Evidence Bundles against auditable, deterministic policy rules.
    Actions: ALLOW, VERIFY, HOLD, BLOCK.
    
    STRICT MANDATE:
      - LLMs are NOT allowed to determine payment actions.
      - Decision rules are 100% deterministic, auditable, and reproducible.
      - Raw probabilities are NEVER shown in customer-facing fields.
      - Produces full audit trail logs.
    """

    def evaluate_protection_policy(self, evidence_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates Evidence Bundle against explicit policy rules and outputs protection action."""
        if not evidence_bundle or not isinstance(evidence_bundle, dict):
            return self._default_allow_result("Empty or invalid evidence bundle.")

        items = evidence_bundle.get("evidence_items", [])
        signals = set(item.get("signal_type") for item in items)
        sources = set(item.get("source") for item in items)
        overall_severity = evidence_bundle.get("overall_severity", "low")
        has_critical = evidence_bundle.get("has_critical_indicators", False)

        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Extract human-readable reasons from evidence descriptions without raw probabilities
        reasons = []
        for item in items:
            desc = item.get("description", "")
            if desc and desc not in reasons:
                reasons.append(desc)

        # POLICY RULE 1: BLOCK (Strong malicious evidence + identity mismatch / phishing)
        if (
            ("merchant_identity_mismatch" in signals or "suspicious_destination" in signals)
            and ("scam_context_detected" in signals or "unregistered_recipient" in signals)
        ) or (has_critical and "merchant_identity_mismatch" in signals and "suspicious_destination" in signals):

            return {
                "decision_id": decision_id,
                "action": "BLOCK",
                "reasons": reasons if reasons else ["Payment destination identity could not be verified."],
                "supporting_evidence": items,
                "recommended_next_step": "Do not proceed with this payment. Verify payee details through official public channels.",
                "prevention_recommendation": "Place recipient account and payment domain under enhanced security monitoring.",
                "audit_trail": {
                    "timestamp": timestamp_utc,
                    "policy_rule_triggered": "RULE_BLOCK_MALICIOUS_DESTINATION_AND_IDENTITY_MISMATCH",
                    "overall_severity": overall_severity,
                    "evidence_count": len(items)
                }
            }

        # POLICY RULE 2: HOLD (Significant concern with inconclusive / uncertain evidence)
        if (
            ("merchant_identity_mismatch" in signals)
            or ("domain_mismatch" in signals and "scam_context_detected" in signals)
            or ("high_behavioral_deviation" in signals and "scam_context_detected" in signals)
        ):

            return {
                "decision_id": decision_id,
                "action": "HOLD",
                "reasons": reasons if reasons else ["This payment is temporarily under review due to recipient mismatch."],
                "supporting_evidence": items,
                "recommended_next_step": "Verify recipient identity and confirm invoice source before retrying payment.",
                "prevention_recommendation": "Flag payment for manual review in Risk Operations Dashboard.",
                "audit_trail": {
                    "timestamp": timestamp_utc,
                    "policy_rule_triggered": "RULE_HOLD_SIGNIFICANT_UNCERTAIN_CONCERN",
                    "overall_severity": overall_severity,
                    "evidence_count": len(items)
                }
            }

        # POLICY RULE 3: VERIFY (Moderate concern: unusual amount, new recipient, or moderate scam text)
        if (
            ("unusual_amount_pattern" in signals)
            or ("newly_observed_recipient" in signals)
            or ("unverified_destination" in signals)
            or ("moderate_scam_indicator" in signals)
            or ("high_behavioral_deviation" in signals)
        ):

            return {
                "decision_id": decision_id,
                "action": "VERIFY",
                "reasons": reasons if reasons else ["Additional verification required before completing this payment."],
                "supporting_evidence": items,
                "recommended_next_step": "We need to verify this payment before it can be completed. Confirm recipient details.",
                "prevention_recommendation": "Prompt customer for explicit two-step payment authorization.",
                "audit_trail": {
                    "timestamp": timestamp_utc,
                    "policy_rule_triggered": "RULE_VERIFY_MODERATE_CONCERN",
                    "overall_severity": overall_severity,
                    "evidence_count": len(items)
                }
            }

        # POLICY RULE 4: ALLOW (Normal payment context)
        return {
            "decision_id": decision_id,
            "action": "ALLOW",
            "reasons": ["Normal payment context."],
            "supporting_evidence": [],
            "recommended_next_step": "Payment successful. No further action required.",
            "prevention_recommendation": "Standard transaction processing.",
            "audit_trail": {
                "timestamp": timestamp_utc,
                "policy_rule_triggered": "RULE_ALLOW_NORMAL_CONTEXT",
                "overall_severity": "low",
                "evidence_count": len(items)
            }
        }

    def _default_allow_result(self, note: str) -> Dict[str, Any]:
        """Default fallback allow payload for clean or empty inputs."""
        return {
            "decision_id": f"DEC-{uuid.uuid4().hex[:8].upper()}",
            "action": "ALLOW",
            "reasons": ["Normal payment context."],
            "supporting_evidence": [],
            "recommended_next_step": "Payment successful.",
            "prevention_recommendation": "Standard transaction processing.",
            "audit_trail": {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "policy_rule_triggered": "RULE_ALLOW_DEFAULT",
                "overall_severity": "low",
                "evidence_count": 0
            }
        }
