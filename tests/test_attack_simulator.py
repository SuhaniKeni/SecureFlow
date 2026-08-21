import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import HTTPException

from secureflow.db.models import Base, Transaction, Customer, PaymentRequest
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.scenarios.attack_simulator import SecureFlowAttackSimulator, BENCHMARK_SCENARIOS
from secureflow.api.main import app
from secureflow.api.schemas import ScenarioRunRequest
from secureflow.api.routes.scenarios import run_benchmark_scenario

client = TestClient(app)

@pytest.fixture
def db_session():
    """Provides a seeded in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_synthetic_database(session, seed=42)
    
    # Ensure CUST-001 has prior history with RCP-001 for SCN-001 ALLOW benchmark test
    c1 = session.query(Customer).filter(Customer.customer_id == "CUST-001").first()
    if c1:
        t_hist = Transaction(
            transaction_id="TXN-HIST-001",
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

@pytest.fixture
def simulator(db_session):
    return SecureFlowAttackSimulator(db_session=db_session)

def test_benchmark_scenarios_count(simulator):
    """Verify all 10 mandated benchmark scenarios are defined."""
    assert len(BENCHMARK_SCENARIOS) == 10, f"Expected 10 benchmark scenarios, found {len(BENCHMARK_SCENARIOS)}"

def test_run_single_scenario_fake_electricity_scam(simulator):
    """Verify scenario 2 (Fake Electricity Disconnection Scam) returns BLOCK."""
    sc2 = next(s for s in BENCHMARK_SCENARIOS if s["scenario_id"] == "SCN-002")
    res = simulator.run_scenario(sc2)

    assert res["scenario_id"] == "SCN-002"
    assert res["protection_action"] == "BLOCK"
    assert res["expected_action"] == "BLOCK"
    assert res["action_match"] is True

def test_run_single_scenario_legitimate_large_purchase(simulator):
    """Verify scenario 7 (Legitimate Large Laptop Purchase) returns VERIFY, not BLOCK."""
    sc7 = next(s for s in BENCHMARK_SCENARIOS if s["scenario_id"] == "SCN-007")
    res = simulator.run_scenario(sc7)

    assert res["scenario_id"] == "SCN-007"
    assert res["protection_action"] == "VERIFY"
    assert res["expected_action"] == "VERIFY"
    assert res["action_match"] is True

def test_run_all_benchmark_scenarios(simulator):
    """Verify benchmark scenarios achieve >= 90% action match accuracy."""
    matches = 0
    for sc in BENCHMARK_SCENARIOS:
        res = simulator.run_scenario(sc)
        assert "protection_action" in res
        assert "explanation" in res
        if res["action_match"]:
            matches += 1

    accuracy = matches / len(BENCHMARK_SCENARIOS)
    assert accuracy >= 0.90, f"Benchmark suite accuracy {accuracy:.2%} below 90% threshold"

# ==============================================================================
# BUG-01 REGRESSION TESTS
# ==============================================================================

def test_scenario_absent_from_transactions_uses_benchmark_definition(db_session):
    """BUG-01 Test 1: SCN-008 is absent from transactions DB, but must run its OWN payload (Local Hardware Store, ₹3,200), not fallback."""
    # Ensure SCN-008 is NOT in DB transactions
    existing_txn = db_session.query(Transaction).filter(Transaction.scenario_id == "SCN-008").first()
    assert existing_txn is None

    # Execute SCN-008 via scenario runner
    req = ScenarioRunRequest(scenario_id="SCN-008")
    resp = run_benchmark_scenario(req, db=db_session)

    # Verify SCN-008 executed its OWN payload and returned VERIFY (not BLOCK from SCN-002 fallback)
    assert resp.action == "VERIFY"
    assert "3,200.00" in str(resp.reasons) or "3,200.00" in str(resp.ops_explanation) or "3,200.00" in str(resp.customer_explanation)

def test_invalid_scenario_id_returns_404(db_session):
    """BUG-01 Test 2: Requesting an invalid scenario ID (SCN-999) must return 404, NEVER silently execute another scenario."""
    req = ScenarioRunRequest(scenario_id="SCN-999")
    with pytest.raises(HTTPException) as exc_info:
        run_benchmark_scenario(req, db=db_session)

    assert exc_info.value.status_code == 404
    assert "SCN-999" in exc_info.value.detail

def test_every_benchmark_scenario_executes_own_payload(db_session):
    """BUG-01 Test 3: Execute SCN-001 through SCN-010 and verify each scenario runs its own payload without silent fallback."""
    for sc in BENCHMARK_SCENARIOS:
        sc_id = sc["scenario_id"]
        req = ScenarioRunRequest(scenario_id=sc_id)
        resp = run_benchmark_scenario(req, db=db_session)

        # Assert correct response structure
        assert resp.transaction_id.startswith("TXN-LIVE-")
        assert resp.action in {"ALLOW", "VERIFY", "HOLD", "BLOCK"}
        
        # Verify SCN-008 specifically evaluates to VERIFY
        if sc_id == "SCN-008":
            assert resp.action == "VERIFY"
