import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from secureflow.db.models import Base, Transaction, PaymentRequest, ProtectionEvent
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.scenarios.attack_simulator import BENCHMARK_SCENARIOS
from secureflow.api.schemas import PaymentAnalysisRequest
from secureflow.api.routes.payments import analyze_payment

@pytest.fixture
def db_session():
    """Provides a seeded in-memory SQLite session for end-to-end testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_synthetic_database(session, seed=42)

    # Ensure CUST-001 has prior history with RCP-001 for SCN-001 ALLOW benchmark test
    t_hist = Transaction(
        transaction_id="TXN-E2E-HIST-001",
        customer_id="CUST-001",
        recipient_id="RCP-001",
        amount=1450.00,
        status="SUCCESS"
    )
    session.add(t_hist)
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_full_12_step_end_to_end_pipeline_integration(db_session):
    """Verifies complete 12-step integration flow from API request to DB audit log across all 10 scenarios."""
    for sc in BENCHMARK_SCENARIOS:
        inp = sc["input"]
        exp_action = sc["expected_action"]

        req = PaymentAnalysisRequest(
            customer_id=inp["customer_id"],
            amount=inp["amount"],
            recipient_id=inp["recipient_id"],
            claimed_merchant=inp.get("claimed_merchant"),
            payment_note=inp.get("payment_note"),
            url=inp.get("url"),
            channel=inp.get("channel", "UPI")
        )

        # 1. API Execution (Runs 4 Engines + Aggregator + Policy Engine + Explanation Engine)
        resp = analyze_payment(req, db=db_session)

        # 2. Response Validation
        assert resp.action == exp_action, f"End-to-End Mismatch for {sc['scenario_id']}: Expected {exp_action}, Got {resp.action}"
        assert resp.transaction_id.startswith("TXN-LIVE-")
        assert len(resp.reasons) > 0
        assert "what_happened" in resp.customer_explanation
        assert "what_action_was_taken" in resp.ops_explanation
        assert "bundle_id" in resp.evidence_bundle

        # 3. Database Audit Trail Persistence Verification
        t_id = resp.transaction_id
        saved_txn = db_session.query(Transaction).filter(Transaction.transaction_id == t_id).first()
        saved_req = db_session.query(PaymentRequest).filter(PaymentRequest.transaction_id == t_id).first()
        saved_evt = db_session.query(ProtectionEvent).filter(ProtectionEvent.transaction_id == t_id).first()

        assert saved_txn is not None, f"DB audit error: Transaction {t_id} missing"
        assert saved_req is not None, f"DB audit error: PaymentRequest {t_id} missing"
        assert saved_evt is not None, f"DB audit error: ProtectionEvent {t_id} missing"
        assert saved_evt.action == exp_action
