import random
import datetime
from typing import List
from sqlalchemy.orm import Session
from secureflow.db.models import (
    Customer, Merchant, Recipient, Scenario, Transaction, PaymentRequest, ProtectionEvent
)

SEED = 42

SCENARIOS_DATA = [
    {
        "scenario_id": "SCN-001",
        "scenario_name": "Normal Electricity Bill Payment",
        "scenario_type": "NORMAL_UTILITY",
        "legitimate_or_attack": "LEGITIMATE",
        "expected_action": "ALLOW"
    },
    {
        "scenario_id": "SCN-002",
        "scenario_name": "Fake Electricity Disconnection Scam",
        "scenario_type": "ELECTRICITY_SCAM",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-003",
        "scenario_name": "Fake Bank Security Alert / KYC Phishing",
        "scenario_type": "BANK_KYC_PHISHING",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-004",
        "scenario_name": "Fake Courier Duty Payment",
        "scenario_type": "COURIER_CUSTOMS_SCAM",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "HOLD"
    },
    {
        "scenario_id": "SCN-005",
        "scenario_name": "Fake Customer Support Refund",
        "scenario_type": "SUPPORT_REFUND_SCAM",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "HOLD"
    },
    {
        "scenario_id": "SCN-006",
        "scenario_name": "Fake Government Income Tax Refund Fee",
        "scenario_type": "GOVT_REFUND_SCAM",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-007",
        "scenario_name": "Legitimate High-Value Electronics Purchase",
        "scenario_type": "LEGITIMATE_UNUSUAL_LARGE",
        "legitimate_or_attack": "LEGITIMATE",
        "expected_action": "VERIFY"
    },
    {
        "scenario_id": "SCN-008",
        "scenario_name": "New Legitimate Local Merchant",
        "scenario_type": "NEW_LEGITIMATE_MERCHANT",
        "legitimate_or_attack": "LEGITIMATE",
        "expected_action": "VERIFY"
    },
    {
        "scenario_id": "SCN-009",
        "scenario_name": "Suspicious Recipient with Normal Text Note",
        "scenario_type": "SUSPICIOUS_RECIPIENT_NORMAL_NOTE",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "HOLD"
    },
    {
        "scenario_id": "SCN-010",
        "scenario_name": "Merchant Identity Mismatch Scam",
        "scenario_type": "MERCHANT_IDENTITY_MISMATCH",
        "legitimate_or_attack": "ATTACK",
        "expected_action": "BLOCK"
    }
]

MERCHANTS_DATA = [
    {
        "merchant_id": "MERCH-001",
        "legal_name": "Bangalore Electricity Supply Company Ltd",
        "brand_name": "BESCOM Electricity",
        "category": "Utility",
        "verified_domain": "bescom.co.in",
        "verified_payment_identifier": "bescom@razorpay",
        "account_age_days": 1825,
        "status": "VERIFIED"
    },
    {
        "merchant_id": "MERCH-002",
        "legal_name": "Amazon Seller Services India Pvt Ltd",
        "brand_name": "Amazon India",
        "category": "E-Commerce",
        "verified_domain": "amazon.in",
        "verified_payment_identifier": "amazon@icici",
        "account_age_days": 2100,
        "status": "VERIFIED"
    },
    {
        "merchant_id": "MERCH-003",
        "legal_name": "State Bank of India Online Banking Services",
        "brand_name": "State Bank of India",
        "category": "Banking",
        "verified_domain": "sbi.co.in",
        "verified_payment_identifier": "sbi@sbi",
        "account_age_days": 3650,
        "status": "VERIFIED"
    },
    {
        "merchant_id": "MERCH-004",
        "legal_name": "Bundl Technologies Pvt Ltd",
        "brand_name": "Swiggy Food",
        "category": "Food Delivery",
        "verified_domain": "swiggy.com",
        "verified_payment_identifier": "swiggy@axisbank",
        "account_age_days": 1500,
        "status": "VERIFIED"
    },
    {
        "merchant_id": "MERCH-005",
        "legal_name": "Indian Postal & Logistics Express Services",
        "brand_name": "India Post Express",
        "category": "Logistics",
        "verified_domain": "indiapost.gov.in",
        "verified_payment_identifier": "indiapost@sbi",
        "account_age_days": 2500,
        "status": "VERIFIED"
    }
]

def generate_synthetic_database(session: Session, seed: int = SEED):
    """Populates the database with reproducible synthetic data."""
    random.seed(seed)
    
    # 1. Populate Scenarios
    scenarios = []
    for s_data in SCENARIOS_DATA:
        sc = Scenario(**s_data)
        session.add(sc)
        scenarios.append(sc)
        
    # 2. Populate Merchants
    merchants = []
    for m_data in MERCHANTS_DATA:
        m = Merchant(**m_data)
        session.add(m)
        merchants.append(m)
        
    session.flush()

    # 3. Populate Recipients (Legitimate + Suspicious/Scam Recipients)
    recipients = []
    # Legitimate recipients linked to verified merchants
    rec1 = Recipient(
        recipient_id="RCP-001",
        display_name="BESCOM Official Bill Desk",
        verified_identity="Bangalore Electricity Supply Company Ltd",
        linked_merchant_id="MERCH-001",
        account_age_days=1800,
        status="ACTIVE"
    )
    rec2 = Recipient(
        recipient_id="RCP-002",
        display_name="Amazon Pay Merchant Account",
        verified_identity="Amazon Seller Services Pvt Ltd",
        linked_merchant_id="MERCH-002",
        account_age_days=2000,
        status="ACTIVE"
    )
    rec3 = Recipient(
        recipient_id="RCP-003",
        display_name="SBI Online Collect",
        verified_identity="State Bank of India",
        linked_merchant_id="MERCH-003",
        account_age_days=3000,
        status="ACTIVE"
    )
    # Suspicious / Mismatched Recipients
    rec4 = Recipient(
        recipient_id="RCP-004",
        display_name="BESCOM Disconnection Cell", # Claimed merchant, but actual identity mismatch!
        verified_identity="Rajesh Kumar Private Account",
        linked_merchant_id=None,
        account_age_days=3, # Brand new recipient account!
        status="FLAGGED"
    )
    rec5 = Recipient(
        recipient_id="RCP-005",
        display_name="Bank Support Desk",
        verified_identity="Karan Sharma Personal",
        linked_merchant_id=None,
        account_age_days=1,
        status="NEW"
    )
    rec6 = Recipient(
        recipient_id="RCP-006",
        display_name="Customs Duty Clearance",
        verified_identity="Logistics Collector Private",
        linked_merchant_id=None,
        account_age_days=5,
        status="FLAGGED"
    )
    
    for r in [rec1, rec2, rec3, rec4, rec5, rec6]:
        session.add(r)
        recipients.append(r)
        
    session.flush()

    # 4. Populate Customers
    first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Siddharth", "Kavya", "Rahul", "Pooja"]
    last_names = ["Sharma", "Verma", "Patel", "Rao", "Nair", "Gupta", "Joshi", "Iyer", "Kulkarni", "Singh"]
    
    customers = []
    for i in range(1, 51):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        c_id = f"CUST-{i:03d}"
        c = Customer(
            customer_id=c_id,
            full_name=f"{fn} {ln}",
            email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
            normal_avg_amount=round(random.uniform(500.0, 3000.0), 2),
            normal_std_amount=round(random.uniform(100.0, 800.0), 2),
            normal_merchants=["MERCH-001", "MERCH-002", "MERCH-004"],
            normal_payment_hours=[8, 22],
            account_age_days=random.randint(180, 1095)
        )
        session.add(c)
        customers.append(c)
        
    session.flush()

    # 5. Populate Historical & Active Transactions + Payment Requests + Protection Events
    now = datetime.datetime.now(datetime.timezone.utc)
    txn_count = 0

    # A) Generate Normal Baseline Transactions for each customer
    for c in customers:
        num_txns = random.randint(8, 15)
        for j in range(num_txns):
            txn_count += 1
            t_id = f"TXN-{txn_count:05d}"
            # Normal amount around baseline
            amt = max(50.0, round(random.gauss(c.normal_avg_amount, c.normal_std_amount), 2))
            dt = now - datetime.timedelta(days=random.randint(1, 60), hours=random.randint(0, 12))
            
            t = Transaction(
                transaction_id=t_id,
                customer_id=c.customer_id,
                merchant_id="MERCH-001" if j % 2 == 0 else "MERCH-002",
                recipient_id="RCP-001" if j % 2 == 0 else "RCP-002",
                amount=amt,
                currency="INR",
                timestamp=dt,
                channel="UPI",
                status="SUCCESS",
                scenario_id="SCN-001"
            )
            session.add(t)
            
            pr = PaymentRequest(
                request_id=f"REQ-{txn_count:05d}",
                transaction_id=t_id,
                message=f"Payment for monthly utilities ref #{10000+txn_count}",
                claimed_merchant="BESCOM Electricity" if j % 2 == 0 else "Amazon India",
                url="https://bescom.co.in/pay" if j % 2 == 0 else "https://amazon.in/pay",
                source_channel="IN_APP",
                timestamp=dt
            )
            session.add(pr)

    # B) Generate 50 Targeted Benchmark Scenario Transactions (Scam & Legitimate Edge Cases)
    benchmark_scenarios = [
        # (Scenario ID, Recipient ID, Claimed Merchant, Amount, URL, Message, Status, Action)
        (
            "SCN-002", "RCP-004", "BESCOM Electricity Board", 8742.00,
            "http://elect-pay-bill.top/pay",
            "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately at http://elect-pay-bill.top/pay",
            "BLOCKED", "BLOCK"
        ),
        (
            "SCN-003", "RCP-005", "State Bank of India", 15000.00,
            "http://bank-kyc-update.online/login",
            "DEAR CUSTOMER, your SBI bank account is suspended. Update KYC immediately or account blocked. Link: http://bank-kyc-update.online/login",
            "BLOCKED", "BLOCK"
        ),
        (
            "SCN-004", "RCP-006", "India Post Customs", 1499.00,
            "http://customs-clearance-pay.com/duty",
            "COURIER ALERT: International parcel held at customs due to pending duty Rs 1499. Pay immediately to release.",
            "HELD", "HOLD"
        ),
        (
            "SCN-007", "RCP-002", "Amazon India", 85000.00,
            "https://amazon.in/checkout/pay",
            "Payment for high-end Apple Laptop purchase via Amazon Pay.",
            "VERIFY_REQUIRED", "VERIFY"
        ),
        (
            "SCN-010", "RCP-004", "BESCOM Power Supply", 12450.00,
            "http://bill-pay-fast.online/electricity",
            "Urgent: BESCOM electric bill due. Avoid penalty of Rs 5000. Pay now.",
            "BLOCKED", "BLOCK"
        )
    ]

    for idx, (scn_id, rcp_id, claimed_m, amt, url_link, msg_text, txn_status, evt_action) in enumerate(benchmark_scenarios, 1):
        txn_count += 1
        t_id = f"TXN-BENCH-{idx:03d}"
        c = random.choice(customers)
        dt = now - datetime.timedelta(hours=idx)

        t = Transaction(
            transaction_id=t_id,
            customer_id=c.customer_id,
            merchant_id=None if "RCP-004" in rcp_id or "RCP-005" in rcp_id else "MERCH-002",
            recipient_id=rcp_id,
            amount=amt,
            currency="INR",
            timestamp=dt,
            channel="UPI",
            status=txn_status,
            scenario_id=scn_id
        )
        session.add(t)

        pr = PaymentRequest(
            request_id=f"REQ-BENCH-{idx:03d}",
            transaction_id=t_id,
            message=msg_text,
            claimed_merchant=claimed_m,
            url=url_link,
            source_channel="SMS",
            timestamp=dt
        )
        session.add(pr)

        pe = ProtectionEvent(
            event_id=f"EVT-BENCH-{idx:03d}",
            transaction_id=t_id,
            action=evt_action,
            evidence={
                "urgency_score": 0.95 if evt_action in ["BLOCK", "HOLD"] else 0.1,
                "domain_risk_score": 0.98 if "http://" in url_link else 0.02,
                "identity_mismatch": True if "RCP-004" in rcp_id else False,
                "recipient_account_age_days": 3 if "RCP-004" in rcp_id else 1800
            },
            explanation=f"Adaptive security layer assigned action {evt_action} based on context risk aggregation.",
            timestamp=dt
        )
        session.add(pe)

    session.commit()
    print(f"[+] Synthetic database generated successfully with seed={seed}:")
    print(f"    - Customers: {len(customers)}")
    print(f"    - Merchants: {len(merchants)}")
    print(f"    - Recipients: {len(recipients)}")
    print(f"    - Scenarios: {len(scenarios)}")
    print(f"    - Total Transactions: {txn_count}")
