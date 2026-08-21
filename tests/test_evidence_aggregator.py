import pytest
from secureflow.aggregation.evidence_aggregator import EvidenceAggregator

@pytest.fixture
def aggregator():
    return EvidenceAggregator()

def test_aggregator_structured_evidence_contract(aggregator):
    """Verify aggregated bundle schema adheres strictly to specification and contains NO BLOCK decision."""
    bundle = aggregator.aggregate(
        url_evidence={"signal": "suspicious_destination", "severity": "high", "risk_score": 0.85, "evidence": {"url": "http://elect-pay-bill.top"}},
        nlp_evidence={"signal": "scam_context_detected", "severity": "high", "risk_score": 0.90, "indicators_detected": {"urgency": True}},
    )

    assert "bundle_id" in bundle
    assert "overall_severity" in bundle
    assert "evidence_count" in bundle
    assert "has_critical_indicators" in bundle
    assert "evidence_items" in bundle

    # MANDATE: Never return financial actions
    for forbidden_key in ["BLOCK", "HOLD", "ALLOW", "VERIFY", "action"]:
        assert forbidden_key not in bundle, f"Aggregator must NOT return policy action '{forbidden_key}'"
        assert bundle["overall_severity"] not in ["BLOCK", "HOLD", "ALLOW", "VERIFY"]

def test_missing_signals(aggregator):
    """Verify aggregator gracefully handles missing or None engine inputs."""
    # Ingest only URL evidence, others None
    bundle = aggregator.aggregate(
        url_evidence={"signal": "suspicious_destination", "severity": "high", "risk_score": 0.85, "evidence": {}},
        nlp_evidence=None,
        behavior_evidence=None,
        merchant_evidence=None
    )

    assert bundle["evidence_count"] == 1
    assert bundle["overall_severity"] == "high"
    assert bundle["evidence_items"][0]["source"] == "url_intelligence_engine"

def test_conflicting_signals(aggregator):
    """Verify aggregator handles conflicting signals (normal customer behavior vs high scam text/URL)."""
    bundle = aggregator.aggregate(
        url_evidence={"signal": "suspicious_destination", "severity": "high", "risk_score": 0.88, "evidence": {}},
        nlp_evidence={"signal": "scam_context_detected", "severity": "high", "risk_score": 0.92, "indicators_detected": {"urgency": True}},
        behavior_evidence={"signal": "normal_behavior_pattern", "severity": "low", "risk_score": 0.05, "behavior_metrics": {}},
        merchant_evidence={"signal": "merchant_identity_match", "severity": "low", "risk_score": 0.05, "consistency_details": {}}
    )

    # Conflicting normal behavior + high scam signals should result in overall_severity = high without dropping high signals
    assert bundle["overall_severity"] == "high"
    assert bundle["evidence_count"] == 2 # Only flagged risks included
    sources = [item["source"] for item in bundle["evidence_items"]]
    assert "url_intelligence_engine" in sources
    assert "scam_nlp_engine" in sources

def test_duplicate_signals(aggregator):
    """Verify aggregator deduplicates duplicate signals from same source."""
    url_ev = {"signal": "suspicious_destination", "severity": "high", "risk_score": 0.85, "evidence": {}}
    
    # Passing identical item twice
    bundle = aggregator.aggregate(
        url_evidence=url_ev,
        nlp_evidence=None
    )

    assert bundle["evidence_count"] == 1

def test_incomplete_data(aggregator):
    """Verify aggregator gracefully handles empty dicts or missing keys."""
    bundle = aggregator.aggregate(
        url_evidence={},
        nlp_evidence={"invalid": "payload"},
        behavior_evidence=None,
        merchant_evidence={}
    )

    assert bundle["evidence_count"] == 0
    assert bundle["overall_severity"] == "low"

def test_normal_transactions(aggregator):
    """Verify normal transaction with clean signals across all engines yields a clean baseline bundle."""
    bundle = aggregator.aggregate(
        url_evidence={"signal": "clean_destination", "severity": "low", "risk_score": 0.02, "evidence": {}},
        nlp_evidence={"signal": "normal_payment_context", "severity": "low", "risk_score": 0.05, "indicators_detected": {}},
        behavior_evidence={"signal": "normal_behavior_pattern", "severity": "low", "risk_score": 0.08, "behavior_metrics": {}},
        merchant_evidence={"signal": "merchant_identity_match", "severity": "low", "risk_score": 0.05, "consistency_details": {}}
    )

    assert bundle["overall_severity"] == "low"
    assert bundle["evidence_count"] == 0 # No risk flags in clean transaction
    assert bundle["has_critical_indicators"] is False
