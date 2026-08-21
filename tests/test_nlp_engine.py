import pytest
from secureflow.engines.scam_nlp_engine import ScamContextNLPEngine

@pytest.fixture
def nlp_engine():
    return ScamContextNLPEngine()

def test_nlp_engine_loads_model(nlp_engine):
    """Verify NLP engine loads trained model artifact."""
    assert nlp_engine.is_loaded is True, "NLP Engine failed to load trained model artifact"
    assert nlp_engine.model is not None

def test_nlp_engine_structured_evidence_contract(nlp_engine):
    """Verify output adheres strictly to structured evidence format and contains NO BLOCK decision."""
    res = nlp_engine.analyze(
        "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
        claimed_merchant="BESCOM Power"
    )

    assert "signal" in res
    assert "risk_score" in res
    assert "severity" in res
    assert "indicators_detected" in res
    assert "evidence" in res

    # MANDATE: Never return financial actions
    for forbidden_key in ["BLOCK", "HOLD", "ALLOW", "VERIFY", "action"]:
        assert forbidden_key not in res, f"NLP Engine must NOT return policy action '{forbidden_key}'"
        assert res["signal"] not in ["BLOCK", "HOLD", "ALLOW", "VERIFY"]

def test_legitimate_payment_note_assessment(nlp_engine):
    """Verify legitimate payment note returns low risk evidence."""
    res = nlp_engine.analyze("Sending my share for dinner yesterday via UPI. Thanks!", claimed_merchant="Amit Sharma")

    assert res["signal"] == "normal_payment_context"
    assert res["severity"] == "low"
    assert res["risk_score"] < 0.30
    assert res["indicators_detected"]["urgency"] is False
    assert res["indicators_detected"]["threats"] is False

def test_fake_electricity_disconnection_scam(nlp_engine):
    """Verify fake electricity disconnection scam message returns high risk indicators."""
    res = nlp_engine.analyze(
        "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
        claimed_merchant="BESCOM Electricity"
    )

    assert res["signal"] == "scam_context_detected"
    assert res["severity"] == "high"
    assert res["risk_score"] >= 0.70
    assert res["indicators_detected"]["urgency"] is True
    assert res["indicators_detected"]["impersonation"] is True
    assert res["indicators_detected"]["claimed_organization"] == "BESCOM Electricity"

def test_fake_bank_kyc_phishing_scam(nlp_engine):
    """Verify fake bank KYC threat message returns high risk indicators."""
    res = nlp_engine.analyze(
        "DEAR CUSTOMER, your account is suspended due to missing KYC. Click link immediately or legal action will be taken.",
        claimed_merchant="State Bank of India"
    )

    assert res["signal"] == "scam_context_detected"
    assert res["severity"] == "high"
    assert res["indicators_detected"]["threats"] is True
    assert res["indicators_detected"]["urgency"] is True

def test_empty_or_none_message(nlp_engine):
    """Verify graceful handling of empty or None message."""
    res_none = nlp_engine.analyze(None)
    assert res_none["severity"] == "low"
    assert res_none["signal"] == "no_text_context"

    res_empty = nlp_engine.analyze("")
    assert res_empty["severity"] == "low"
