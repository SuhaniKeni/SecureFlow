import os
import sys
sys.path.insert(0, '.')
import json
import datetime
from sqlalchemy.orm import Session

from secureflow.db.database import SessionLocal, engine, init_db
from secureflow.db.models import Transaction, PaymentRequest, ProtectionEvent, Customer, Merchant, Recipient
from secureflow.scenarios.attack_simulator import BENCHMARK_SCENARIOS, SecureFlowAttackSimulator
from secureflow.api.schemas import PaymentAnalysisRequest
from secureflow.api.routes.payments import analyze_payment

def run_end_to_end_verification() -> bool:
    print("=======================================================================")
    print(" SECUREFLOW: END-TO-END SYSTEM INTEGRATION VERIFICATION (Stage 5.18)")
    print("=======================================================================")

    db = SessionLocal()
    init_db(engine)

    simulator = SecureFlowAttackSimulator(db_session=db)

    print(f"\n[1/4] Verifying Database Connection & Synthetic Baseline Entities...")
    cust_count = db.query(Customer).count()
    merch_count = db.query(Merchant).count()
    rcp_count = db.query(Recipient).count()
    txn_count = db.query(Transaction).count()

    print(f"      - Synthetic Customers: {cust_count}")
    print(f"      - Synthetic Merchants: {merch_count}")
    print(f"      - Synthetic Recipients: {rcp_count}")
    print(f"      - Database Transactions: {txn_count}")

    assert cust_count > 0, "Database check failed: 0 customers found"
    assert merch_count > 0, "Database check failed: 0 merchants found"

    print("\n[2/4] Executing Complete 12-Step Pipeline Across All 10 Benchmark Scenarios...")
    passed_scenarios = 0

    for idx, sc in enumerate(BENCHMARK_SCENARIOS, 1):
        inp = sc["input"]
        exp_action = sc["expected_action"]

        # Create PaymentAnalysisRequest schema
        req = PaymentAnalysisRequest(
            customer_id=inp["customer_id"],
            amount=inp["amount"],
            recipient_id=inp["recipient_id"],
            claimed_merchant=inp.get("claimed_merchant"),
            payment_note=inp.get("payment_note"),
            url=inp.get("url"),
            channel=inp.get("channel", "UPI")
        )

        # Run complete API endpoint analysis
        resp = analyze_payment(req, db=db)

        action = resp.action
        reasons = resp.reasons
        cust_expl = resp.customer_explanation
        ops_expl = resp.ops_explanation
        bundle = resp.evidence_bundle
        t_id = resp.transaction_id

        # Verify DB Audit Log Persistence
        saved_txn = db.query(Transaction).filter(Transaction.transaction_id == t_id).first()
        saved_evt = db.query(ProtectionEvent).filter(ProtectionEvent.transaction_id == t_id).first()

        assert saved_txn is not None, f"DB audit failure: Transaction {t_id} not saved"
        assert saved_evt is not None, f"DB audit failure: ProtectionEvent for {t_id} not saved"
        assert saved_evt.action == action, f"DB audit mismatch: {saved_evt.action} != {action}"

        is_match = (action == exp_action)
        if is_match:
            passed_scenarios += 1

        print(f"      Scenario {idx:02d}: {sc['scenario_name'][:45]:<45} | Exp: {exp_action:<6} | Actual: {action:<6} | DB Audit: SAVED | {'PASS' if is_match else 'FAIL'}")

    db.close()

    print("\n[3/4] Verifying Frontend Production Bundle Integration...")
    dist_html = "frontend/dist/index.html"
    dist_js = "frontend/dist/assets"
    assert os.path.exists(dist_html), "Frontend bundle missing: index.html not found in dist/"
    assert os.path.exists(dist_js), "Frontend bundle missing: dist/assets/ not found"
    print("      - Frontend production build dist/ bundle verified.")

    print("\n[4/4] Final Verification Summary:")
    print(f"      - Benchmark Scenarios Evaluated: {len(BENCHMARK_SCENARIOS)}")
    print(f"      - Benchmark Scenario Action Matches: {passed_scenarios}/{len(BENCHMARK_SCENARIOS)} ({passed_scenarios/len(BENCHMARK_SCENARIOS)*100:.1f}%)")
    print(f"      - End-to-End Database Audit Trail: PERSISTED & AUDITABLE")
    print("=======================================================================")

    return passed_scenarios == len(BENCHMARK_SCENARIOS)

if __name__ == "__main__":
    success = run_end_to_end_verification()
    if not success:
        sys.exit(1)
