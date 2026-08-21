import pytest
from secureflow.explanations.explanation_engine import ExplanationEngine

@pytest.fixture
def explanation_engine():
    return ExplanationEngine()

def test_explanation_engine_schema_contract(explanation_engine):
    """Verify output contains both Customer and Ops explanation sections with all 5 required fields."""
    evidence_bundle = {
        "overall_severity": "high",
        "evidence_items": [
            {"signal_type": "merchant_identity_mismatch", "source": "merchant_consistency_engine", "description": "Identity mismatch", "severity": "high"}
        ]
    }
    tx_ctx = {"amount": 8742.0, "timestamp": "2026-08-21T12:00:00Z"}
    m_info = {"claimed_merchant": "BESCOM Electricity", "actual_recipient_name": "Rajesh Kumar"}

    res = explanation_engine.generate_explanation(
        protection_action="BLOCK",
        evidence_bundle=evidence_bundle,
        transaction_context=tx_ctx,
        merchant_info=m_info
    )

    assert "customer_explanation" in res
    assert "ops_explanation" in res
    assert "grounding_check_passed" in res

    cust = res["customer_explanation"]
    ops = res["ops_explanation"]

    required_keys = ["what_happened", "why", "what_action_was_taken", "what_should_happen_next", "how_to_prevent_recurrence"]
    for k in required_keys:
        assert k in cust, f"Missing key '{k}' in customer_explanation"
        assert k in ops, f"Missing key '{k}' in ops_explanation"

def test_action_preservation_mandate(explanation_engine):
    """Verify protection action is strictly preserved and cannot be mutated."""
    evidence_bundle = {"overall_severity": "high", "evidence_items": []}
    tx_ctx = {"amount": 500.0}
    m_info = {"claimed_merchant": "Amazon"}

    res_block = explanation_engine.generate_explanation("BLOCK", evidence_bundle, tx_ctx, m_info)
    assert res_block["customer_explanation"]["what_action_was_taken"] == "BLOCK"

    res_hold = explanation_engine.generate_explanation("HOLD", evidence_bundle, tx_ctx, m_info)
    assert res_hold["customer_explanation"]["what_action_was_taken"] == "HOLD"

    res_verify = explanation_engine.generate_explanation("VERIFY", evidence_bundle, tx_ctx, m_info)
    assert res_verify["customer_explanation"]["what_action_was_taken"] == "VERIFY"

    res_allow = explanation_engine.generate_explanation("ALLOW", evidence_bundle, tx_ctx, m_info)
    assert res_allow["customer_explanation"]["what_action_was_taken"] == "ALLOW"

def test_no_raw_probabilities_in_customer_view(explanation_engine):
    """Verify raw probability floats are sanitized from customer-facing text."""
    evidence_bundle = {
        "overall_severity": "high",
        "evidence_items": [
            {"signal_type": "suspicious_destination", "description": "Phishing risk 0.9625", "severity": "high"}
        ]
    }
    tx_ctx = {"amount": 1000.0}
    m_info = {"claimed_merchant": "Payee"}

    res = explanation_engine.generate_explanation("BLOCK", evidence_bundle, tx_ctx, m_info)
    cust_why = res["customer_explanation"]["why"]

    # Customer explanation should be clean and non-alarming
    assert "0.9625" not in cust_why

def test_factual_grounding_validation(explanation_engine):
    """Verify explanation is factually grounded in evidence bundle."""
    evidence_bundle = {
        "overall_severity": "high",
        "evidence_items": [
            {"signal_type": "scam_context_detected", "description": "Disconnection threat in message", "severity": "high"}
        ]
    }
    tx_ctx = {"amount": 8742.0}
    m_info = {"claimed_merchant": "BESCOM Power"}

    res = explanation_engine.generate_explanation("BLOCK", evidence_bundle, tx_ctx, m_info)
    assert res["grounding_check_passed"] is True
