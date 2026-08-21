import pytest
from secureflow.aggregation.evidence_aggregator import EvidenceAggregator
from secureflow.policy.decision_engine import ProtectionDecisionEngine

@pytest.fixture
def aggregator():
    return EvidenceAggregator()

@pytest.fixture
def decision_engine():
    return ProtectionDecisionEngine()

def test_decision_engine_output_schema_contract(decision_engine):
    """Verify Protection Decision Engine result schema contains all 5 required fields + audit trail."""
    bundle = {
        "overall_severity": "high",
        "has_critical_indicators": True,
        "evidence_items": [
            {"signal_type": "merchant_identity_mismatch", "source": "merchant_consistency_engine", "description": "Claimed BESCOM mismatch", "severity": "high"},
            {"signal_type": "suspicious_destination", "source": "url_intelligence_engine", "description": "Phishing link detected", "severity": "high"},
            {"signal_type": "scam_context_detected", "source": "scam_nlp_engine", "description": "Urgent disconnection threat", "severity": "high"}
        ]
    }

    res = decision_engine.evaluate_protection_policy(bundle)

    assert "action" in res
    assert "reasons" in res
    assert "supporting_evidence" in res
    assert "recommended_next_step" in res
    assert "prevention_recommendation" in res
    assert "audit_trail" in res

    assert res["action"] in ["ALLOW", "VERIFY", "HOLD", "BLOCK"]
    assert len(res["reasons"]) > 0
    assert "policy_rule_triggered" in res["audit_trail"]

def test_rule_block_fake_electricity_disconnection_scam(decision_engine):
    """Verify strong malicious scam (SCN-002) triggers BLOCK action."""
    bundle = {
        "overall_severity": "high",
        "has_critical_indicators": True,
        "evidence_items": [
            {"signal_type": "merchant_identity_mismatch", "source": "merchant_consistency_engine", "description": "Identity mismatch", "severity": "high"},
            {"signal_type": "suspicious_destination", "source": "url_intelligence_engine", "description": "Phishing URL", "severity": "high"},
            {"signal_type": "scam_context_detected", "source": "scam_nlp_engine", "description": "Disconnection threat", "severity": "high"}
        ]
    }

    res = decision_engine.evaluate_protection_policy(bundle)
    assert res["action"] == "BLOCK"
    assert res["audit_trail"]["policy_rule_triggered"] == "RULE_BLOCK_MALICIOUS_DESTINATION_AND_IDENTITY_MISMATCH"

def test_rule_hold_significant_concern(decision_engine):
    """Verify significant but uncertain mismatch (SCN-004) triggers HOLD action."""
    bundle = {
        "overall_severity": "high",
        "has_critical_indicators": True,
        "evidence_items": [
            {"signal_type": "merchant_identity_mismatch", "source": "merchant_consistency_engine", "description": "Identity mismatch", "severity": "high"}
        ]
    }

    res = decision_engine.evaluate_protection_policy(bundle)
    assert res["action"] == "HOLD"
    assert res["audit_trail"]["policy_rule_triggered"] == "RULE_HOLD_SIGNIFICANT_UNCERTAIN_CONCERN"

def test_rule_verify_legitimate_unusual_large_purchase(decision_engine):
    """Verify high-amount unusual purchase (SCN-007) triggers VERIFY, NOT BLOCK!"""
    bundle = {
        "overall_severity": "medium",
        "has_critical_indicators": False,
        "evidence_items": [
            {"signal_type": "unusual_amount_pattern", "source": "customer_behavior_engine", "description": "Amount above mean", "severity": "medium"}
        ]
    }

    res = decision_engine.evaluate_protection_policy(bundle)
    assert res["action"] == "VERIFY"
    assert res["action"] != "BLOCK"
    assert res["audit_trail"]["policy_rule_triggered"] == "RULE_VERIFY_MODERATE_CONCERN"

def test_rule_allow_normal_transaction(decision_engine):
    """Verify clean transaction (SCN-001) triggers ALLOW action."""
    bundle = {
        "overall_severity": "low",
        "has_critical_indicators": False,
        "evidence_items": []
    }

    res = decision_engine.evaluate_protection_policy(bundle)
    assert res["action"] == "ALLOW"
    assert res["audit_trail"]["policy_rule_triggered"] == "RULE_ALLOW_NORMAL_CONTEXT"

def test_deterministic_reproducibility(decision_engine):
    """Verify policy evaluation is 100% deterministic over 10 consecutive executions."""
    bundle = {
        "overall_severity": "high",
        "has_critical_indicators": True,
        "evidence_items": [
            {"signal_type": "merchant_identity_mismatch", "source": "merchant_consistency_engine", "description": "Identity mismatch", "severity": "high"},
            {"signal_type": "suspicious_destination", "source": "url_intelligence_engine", "description": "Phishing URL", "severity": "high"},
            {"signal_type": "scam_context_detected", "source": "scam_nlp_engine", "description": "Disconnection threat", "severity": "high"}
        ]
    }

    first_res = decision_engine.evaluate_protection_policy(bundle)
    for _ in range(10):
        res = decision_engine.evaluate_protection_policy(bundle)
        assert res["action"] == first_res["action"]
        assert res["audit_trail"]["policy_rule_triggered"] == first_res["audit_trail"]["policy_rule_triggered"]
