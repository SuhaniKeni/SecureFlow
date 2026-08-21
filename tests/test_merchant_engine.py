import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from secureflow.db.models import Base, Recipient, Merchant
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.engines.merchant_engine import MerchantConsistencyEngine

@pytest.fixture
def db_session():
    """Provides a seeded in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_synthetic_database(session, seed=42)
    yield session
    session.close()

@pytest.fixture
def merchant_engine(db_session):
    return MerchantConsistencyEngine(db_session=db_session)

def test_merchant_engine_structured_evidence_contract(merchant_engine):
    """Verify output adheres strictly to structured evidence format and contains NO BLOCK decision."""
    res = merchant_engine.analyze_consistency(
        claimed_merchant="BESCOM Electricity",
        recipient_id="RCP-001"
    )

    assert "signal" in res
    assert "risk_score" in res
    assert "severity" in res
    assert "consistency_details" in res
    assert "evidence" in res

    # MANDATE: Never return financial actions
    for forbidden_key in ["BLOCK", "HOLD", "ALLOW", "VERIFY", "action"]:
        assert forbidden_key not in res, f"Merchant Engine must NOT return policy action '{forbidden_key}'"
        assert res["signal"] not in ["BLOCK", "HOLD", "ALLOW", "VERIFY"]

def test_verified_merchant_identity_match(merchant_engine):
    """Verify legitimate payment to verified merchant returns merchant_identity_match."""
    res = merchant_engine.analyze_consistency(
        claimed_merchant="BESCOM Electricity",
        recipient_id="RCP-001",
        destination_url="https://bescom.co.in/pay"
    )

    assert res["signal"] == "merchant_identity_match"
    assert res["severity"] == "low"
    assert res["consistency_details"]["is_verified_merchant"] is True
    assert res["consistency_details"]["domain_match"] is True

def test_merchant_identity_mismatch_scam(merchant_engine):
    """Verify claimed utility name but recipient being unverified private individual returns high risk mismatch."""
    res = merchant_engine.analyze_consistency(
        claimed_merchant="BESCOM Electricity Board",
        recipient_id="RCP-004", # Rajesh Kumar Private Account
        destination_url="http://elect-pay-bill.top/pay"
    )

    assert res["signal"] == "merchant_identity_mismatch"
    assert res["severity"] == "high"
    assert res["risk_score"] >= 0.90
    assert res["consistency_details"]["domain_match"] is False
    assert res["consistency_details"]["is_verified_merchant"] is False
    assert "Rajesh Kumar" in res["evidence"]

def test_domain_mismatch_detection(merchant_engine):
    """Verify phishing URL domain mismatch for verified merchant."""
    res = merchant_engine.analyze_consistency(
        claimed_merchant="Amazon India",
        recipient_id="RCP-002",
        destination_url="http://razorpay-reward-claim.xyz/collect" # Fake domain
    )

    assert res["consistency_details"]["domain_match"] is False

def test_unregistered_recipient(merchant_engine):
    """Verify handling of unknown/unregistered recipient ID."""
    res = merchant_engine.analyze_consistency(
        claimed_merchant="State Bank of India",
        recipient_id="RCP-UNKNOWN-999"
    )

    assert res["signal"] == "unregistered_recipient"
    assert res["severity"] == "high"
