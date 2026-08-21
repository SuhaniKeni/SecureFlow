import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from secureflow.db.models import Base, Transaction, Customer
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.scenarios.attack_simulator import SecureFlowAttackSimulator, BENCHMARK_SCENARIOS

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
