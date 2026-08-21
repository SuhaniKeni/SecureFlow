import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from secureflow.db.models import (
    Base, Customer, Merchant, Recipient, Scenario, Transaction, PaymentRequest, ProtectionEvent
)
from secureflow.db.synthetic_generator import generate_synthetic_database

@pytest.fixture
def in_memory_db():
    """Provides a fresh, isolated in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_database_initialization_and_table_counts(in_memory_db):
    """Verify all 7 database entities are seeded correctly."""
    generate_synthetic_database(in_memory_db, seed=42)

    customers_count = in_memory_db.query(Customer).count()
    merchants_count = in_memory_db.query(Merchant).count()
    recipients_count = in_memory_db.query(Recipient).count()
    scenarios_count = in_memory_db.query(Scenario).count()
    txns_count = in_memory_db.query(Transaction).count()
    requests_count = in_memory_db.query(PaymentRequest).count()
    events_count = in_memory_db.query(ProtectionEvent).count()

    assert customers_count == 50, f"Expected 50 customers, got {customers_count}"
    assert merchants_count == 5, f"Expected 5 merchants, got {merchants_count}"
    assert recipients_count == 6, f"Expected 6 recipients, got {recipients_count}"
    assert scenarios_count == 10, f"Expected 10 scenarios, got {scenarios_count}"
    assert txns_count >= 500, f"Expected >= 500 transactions, got {txns_count}"
    assert requests_count == txns_count, "Every transaction must have an associated PaymentRequest"
    assert events_count >= 5, "Protection events must be recorded for benchmark scenarios"

def test_reproducibility_with_fixed_seed(in_memory_db):
    """Verify generator output is 100% deterministic with seed=42."""
    generate_synthetic_database(in_memory_db, seed=42)
    c1 = in_memory_db.query(Customer).order_by(Customer.customer_id).first()
    t1 = in_memory_db.query(Transaction).order_by(Transaction.transaction_id).first()

    # Second database session with same seed
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine2)
    Session2 = sessionmaker(bind=engine2)
    session2 = Session2()
    generate_synthetic_database(session2, seed=42)

    c2 = session2.query(Customer).order_by(Customer.customer_id).first()
    t2 = session2.query(Transaction).order_by(Transaction.transaction_id).first()

    assert c1.full_name == c2.full_name, "Customer generation must be reproducible"
    assert c1.normal_avg_amount == c2.normal_avg_amount, "Customer baseline stats must match"
    assert t1.amount == t2.amount, "Transaction generation must be reproducible"
    session2.close()

def test_foreign_key_referential_integrity(in_memory_db):
    """Verify relational integrity across transactions, customers, recipients, and scenarios."""
    generate_synthetic_database(in_memory_db, seed=42)

    txns = in_memory_db.query(Transaction).all()
    for t in txns:
        assert t.customer is not None, f"Transaction {t.transaction_id} missing Customer relation"
        assert t.recipient is not None, f"Transaction {t.transaction_id} missing Recipient relation"
        assert t.payment_request is not None, f"Transaction {t.transaction_id} missing PaymentRequest relation"
        assert t.scenario is not None, f"Transaction {t.transaction_id} missing Scenario relation"

def test_scam_vs_legitimate_scenario_distribution(in_memory_db):
    """Verify non-trivial separability across scam and legitimate benchmark scenarios."""
    generate_synthetic_database(in_memory_db, seed=42)

    scam_txns = in_memory_db.query(Transaction).filter(Transaction.status.in_(["BLOCKED", "HELD"])).all()
    legit_txns = in_memory_db.query(Transaction).filter(Transaction.status == "SUCCESS").all()

    assert len(scam_txns) > 0, "Must contain flagged/blocked scam transactions"
    assert len(legit_txns) > 0, "Must contain successful normal transactions"

    for t in scam_txns:
        pr = t.payment_request
        # Verify scam requests contain messages/URLs or recipient identity mismatches
        assert (pr.url is not None) or (t.recipient.linked_merchant_id is None)
