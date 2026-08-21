import os
import pytest
from secureflow.engines.url_intel_engine import URLIntelligenceEngine

@pytest.fixture
def url_engine():
    return URLIntelligenceEngine()

def test_url_engine_loads_model(url_engine):
    """Verify URL engine loads trained model artifact."""
    assert url_engine.is_loaded is True, "URL Engine failed to load trained model artifact"
    assert url_engine.model is not None

def test_url_engine_structured_evidence_contract(url_engine):
    """Verify output adheres strictly to structured evidence format and contains NO BLOCK decision."""
    res = url_engine.analyze("http://elect-pay-bill.top/pay")

    # Contract verification
    assert "signal" in res
    assert "risk_score" in res
    assert "severity" in res
    assert "evidence" in res

    # MANDATE: Never return financial actions
    for forbidden_key in ["BLOCK", "HOLD", "ALLOW", "VERIFY", "action"]:
        assert forbidden_key not in res, f"URL Engine must NOT return policy action '{forbidden_key}'"
        assert res["signal"] not in ["BLOCK", "HOLD", "ALLOW", "VERIFY"]

def test_legitimate_url_assessment(url_engine):
    """Verify legitimate payment destination returns low risk evidence."""
    res = url_engine.analyze("https://razorpay.com/payment-link/pl_12345")

    assert res["signal"] == "clean_destination"
    assert res["severity"] == "low"
    assert res["risk_score"] < 0.30
    assert res["evidence"]["has_https"] is True
    assert res["evidence"]["is_ip"] is False

def test_suspicious_phishing_url_assessment(url_engine):
    """Verify suspicious phishing URL returns high risk evidence."""
    res = url_engine.analyze("http://elect-pay-bill.top/pay")

    assert res["signal"] == "suspicious_destination"
    assert res["severity"] == "high"
    assert res["risk_score"] >= 0.70
    assert res["evidence"]["typosquatted_keyword_detected"] is True or res["evidence"]["has_https"] is False

def test_empty_or_none_url(url_engine):
    """Verify graceful handling of None or empty URL."""
    res_none = url_engine.analyze(None)
    assert res_none["severity"] == "low"
    assert res_none["signal"] == "no_destination_url"

    res_empty = url_engine.analyze("")
    assert res_empty["severity"] == "low"
