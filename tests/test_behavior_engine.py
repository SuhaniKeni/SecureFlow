import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from secureflow.db.models import Base, Customer
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.engines.behavior_engine import CustomerBehaviorEngine

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
def behavior_engine(db_session):
    return CustomerBehaviorEngine(db_session=db_session)

def test_behavior_engine_structured_evidence_contract(behavior_engine, db_session):
    """Verify output adheres strictly to structured evidence format and contains NO BLOCK decision."""
    c = db_session.query(Customer).first()
    res = behavior_engine.analyze_transaction(
        customer_id=c.customer_id,
        amount=1500.0,
        recipient_id="RCP-001"
    )

    assert "signal" in res
    assert "risk_score" in res
    assert "severity" in res
    assert "behavior_metrics" in res
    assert "evidence" in res

    # MANDATE: Never return financial actions
    for forbidden_key in ["BLOCK", "HOLD", "ALLOW", "VERIFY", "action"]:
        assert forbidden_key not in res, f"Behavior Engine must NOT return policy action '{forbidden_key}'"
        assert res["signal"] not in ["BLOCK", "HOLD", "ALLOW", "VERIFY"]

def test_normal_behavior_transaction(behavior_engine, db_session):
    """Verify standard amount with existing recipient yields normal behavior signal."""
    c = db_session.query(Customer).first()
    res = behavior_engine.analyze_transaction(
        customer_id=c.customer_id,
        amount=c.normal_avg_amount,
        recipient_id="RCP-001"
    )

    assert res["signal"] == "normal_behavior_pattern"
    assert res["severity"] == "low"
    assert abs(res["behavior_metrics"]["amount_zscore"]) < 1.0

def test_legitimate_unusual_high_amount(behavior_engine, db_session):
    """Verify high-amount unusual transaction yields medium severity without declaring fraud."""
    c = db_session.query(Customer).first()
    high_amount = c.normal_avg_amount + (4 * c.normal_std_amount)

    res = behavior_engine.analyze_transaction(
        customer_id=c.customer_id,
        amount=high_amount,
        recipient_id="RCP-002"
    )

    # High amount should trigger unusual pattern signal and medium severity, NOT high/fraud
    assert res["severity"] == "medium"
    assert res["behavior_metrics"]["amount_zscore"] > 3.0
    assert "substantially above" in res["evidence"] or "deviation" in res["evidence"]

def test_new_recipient_and_timing_anomaly(behavior_engine, db_session):
    """Verify new recipient and off-hours timing detection."""
    c = db_session.query(Customer).first()
    late_night = datetime.datetime(2026, 8, 21, 3, 15, 0) # 3:15 AM off-hours

    res = behavior_engine.analyze_transaction(
        customer_id=c.customer_id,
        amount=c.normal_avg_amount,
        recipient_id="RCP-NEW-UNKNOWN",
        timestamp=late_night
    )

    assert res["behavior_metrics"]["is_new_recipient"] is True
    assert res["behavior_metrics"]["hour_anomaly"] is True

def test_unknown_customer_fallback(behavior_engine):
    """Verify graceful handling of non-existent customer profile."""
    res = behavior_engine.analyze_transaction(
        customer_id="CUST-999-NONEXISTENT",
        amount=5000.0,
        recipient_id="RCP-001"
    )

    assert res["signal"] == "new_customer_no_history"
    assert res["severity"] == "medium"
