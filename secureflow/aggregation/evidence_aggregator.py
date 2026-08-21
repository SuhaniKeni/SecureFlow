import uuid
import datetime
from typing import Dict, Any, List, Optional

class EvidenceAggregator:
    """Aggregates structured evidence signals from multiple security engines into a normalized Evidence Bundle.
    
    Inputs:
      - url_evidence (URLIntelligenceEngine)
      - nlp_evidence (ScamContextNLPEngine)
      - behavior_evidence (CustomerBehaviorEngine)
      - merchant_evidence (MerchantConsistencyEngine)
      
    STRICT MANDATE:
      - Normalizes evidence signals into a unified schema.
      - Keeps internal confidence values isolated in metadata (not exposed in customer-facing descriptions).
      - NEVER makes final payment decisions ('ALLOW' / 'VERIFY' / 'HOLD' / 'BLOCK').
    """

    def aggregate(
        self,
        url_evidence: Optional[Dict[str, Any]] = None,
        nlp_evidence: Optional[Dict[str, Any]] = None,
        behavior_evidence: Optional[Dict[str, Any]] = None,
        merchant_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Normalizes and aggregates all available engine signals into one Evidence Bundle."""
        items: List[Dict[str, Any]] = []

        # 1. Process URL Evidence
        if url_evidence and isinstance(url_evidence, dict) and "signal" in url_evidence:
            sig = url_evidence.get("signal", "no_destination_url")
            if sig not in ["no_destination_url", "clean_destination"]:
                items.append({
                    "signal_type": sig,
                    "source": "url_intelligence_engine",
                    "description": f"Payment destination URL domain exhibits security risk signals.",
                    "severity": url_evidence.get("severity", "low"),
                    "confidence": float(url_evidence.get("risk_score", 0.0)),
                    "supporting_data": url_evidence.get("evidence", {})
                })

        # 2. Process NLP Scam Context Evidence
        if nlp_evidence and isinstance(nlp_evidence, dict) and "signal" in nlp_evidence:
            sig = nlp_evidence.get("signal", "normal_payment_context")
            if sig not in ["normal_payment_context", "no_text_context"]:
                items.append({
                    "signal_type": sig,
                    "source": "scam_nlp_engine",
                    "description": nlp_evidence.get("evidence", "Social engineering scam keywords detected in message."),
                    "severity": nlp_evidence.get("severity", "low"),
                    "confidence": float(nlp_evidence.get("risk_score", 0.0)),
                    "supporting_data": nlp_evidence.get("indicators_detected", {})
                })

        # 3. Process Customer Behavior Evidence
        if behavior_evidence and isinstance(behavior_evidence, dict) and "signal" in behavior_evidence:
            sig = behavior_evidence.get("signal", "normal_behavior_pattern")
            if sig not in ["normal_behavior_pattern"]:
                items.append({
                    "signal_type": sig,
                    "source": "customer_behavior_engine",
                    "description": behavior_evidence.get("evidence", "Transaction deviates from customer historical baseline."),
                    "severity": behavior_evidence.get("severity", "low"),
                    "confidence": float(behavior_evidence.get("risk_score", 0.0)),
                    "supporting_data": behavior_evidence.get("behavior_metrics", {})
                })

        # 4. Process Merchant & Recipient Consistency Evidence
        if merchant_evidence and isinstance(merchant_evidence, dict) and "signal" in merchant_evidence:
            sig = merchant_evidence.get("signal", "merchant_identity_match")
            if sig not in ["merchant_identity_match"]:
                items.append({
                    "signal_type": sig,
                    "source": "merchant_consistency_engine",
                    "description": merchant_evidence.get("evidence", "Recipient identity inconsistency detected."),
                    "severity": merchant_evidence.get("severity", "low"),
                    "confidence": float(merchant_evidence.get("risk_score", 0.0)),
                    "supporting_data": merchant_evidence.get("consistency_details", {})
                })

        # 5. Deduplicate Items by (signal_type, source)
        deduped_items = []
        seen_keys = set()
        for item in items:
            key = (item["signal_type"], item["source"])
            if key not in seen_keys:
                seen_keys.add(key)
                deduped_items.append(item)

        # 6. Overall Severity & Critical Indicators Determination
        if any(item["severity"] == "high" for item in deduped_items):
            overall_severity = "high"
        elif any(item["severity"] == "medium" for item in deduped_items):
            overall_severity = "medium"
        else:
            overall_severity = "low"

        has_critical = any(
            item["signal_type"] in ["merchant_identity_mismatch", "suspicious_destination", "scam_context_detected"]
            for item in deduped_items
        )

        return {
            "bundle_id": f"BDL-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "overall_severity": overall_severity,
            "evidence_count": len(deduped_items),
            "has_critical_indicators": has_critical,
            "evidence_items": deduped_items
        }
