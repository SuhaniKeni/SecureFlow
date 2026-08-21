import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from secureflow.db.models import Base
from secureflow.db.database import get_db_session
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.api.main import app

# Use StaticPool with sqlite:///:memory: so all connections share the same in-memory DB schema during tests
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db_session] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    generate_synthetic_database(session, seed=42)
    session.close()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_payment_fake_electricity_scam():
    payload = {
        "customer_id": "CUST-001",
        "amount": 8742.00,
        "recipient_id": "RCP-004",
        "claimed_merchant": "BESCOM Electricity Board",
        "payment_note": "URGENT: Disconnection notice tonight at 9.30pm. Pay overdue bill Rs 8742",
        "url": "http://elect-pay-bill.top/pay",
        "channel": "UPI"
    }
    response = client.post("/payments/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "BLOCK"
    assert "reasons" in data
    assert "customer_explanation" in data
    assert data["customer_explanation"]["what_action_was_taken"] == "BLOCK"

def test_credential_rejection_security_guardrail():
    payload = {
        "customer_id": "CUST-001",
        "amount": 1000.0,
        "recipient_id": "RCP-001",
        "upi_pin": "1234" # FORBIDDEN CREDENTIAL FIELD
    }
    response = client.post("/payments/analyze", json=payload)
    assert response.status_code in [400, 422]

def test_simulate_payment():
    payload = {
        "scenario_id": "SCN-002",
        "customer_id": "CUST-001",
        "amount": 8742.00,
        "recipient_id": "RCP-004",
        "claimed_merchant": "BESCOM Electricity",
        "payment_note": "URGENT: Disconnection notice",
        "url": "http://elect-pay-bill.top/pay"
    }
    response = client.post("/payments/simulate", json=payload)
    assert response.status_code == 200
    assert "action" in response.json()

def test_get_payment_by_id():
    response = client.get("/payments/TXN-BENCH-001")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "TXN-BENCH-001"

def test_get_payment_by_id_not_found():
    response = client.get("/payments/TXN-NONEXISTENT-999")
    assert response.status_code == 404

def test_list_protection_events():
    response = client.get("/protection-events?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_protection_event_by_id():
    response = client.get("/protection-events/EVT-BENCH-001")
    assert response.status_code == 200
    assert response.json()["event_id"] == "EVT-BENCH-001"

def test_get_merchant_by_id():
    response = client.get("/merchants/MERCH-001")
    assert response.status_code == 200
    assert response.json()["brand_name"] == "BESCOM Electricity"

def test_get_customer_history():
    response = client.get("/customers/CUST-001/history")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "CUST-001"
    assert data["total_transactions"] > 0

def test_run_benchmark_scenario():
    payload = {"scenario_id": "SCN-002"}
    response = client.post("/scenarios/run", json=payload)
    assert response.status_code == 200
    assert response.json()["action"] == "BLOCK"
