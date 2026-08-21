import os
import json
import random
from typing import List, Dict, Any

EVAL_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "expanded_eval_scenarios.json"
)

# Lists for realistic procedural generation
LEGIT_MERCHANTS = [
    ("BESCOM Electricity", "RCP-001", "https://bescom.co.in/pay"),
    ("Amazon India", "RCP-002", "https://amazon.in/checkout/pay"),
    ("State Bank of India", "RCP-003", "https://sbi.co.in/portal/pay"),
    ("Swiggy Food Delivery", "RCP-001", "https://swiggy.com/checkout"),
    ("India Post Express", "RCP-003", "https://indiapost.gov.in/pay")
]

SUSPICIOUS_DOMAINS = [
    "http://elect-pay-bill.top/pay",
    "http://bank-kyc-update.online/login",
    "http://customs-clearance-pay.com/duty",
    "http://refund-support-portal.site/fee",
    "http://incometax-refund-gov.in.net/claim",
    "http://bill-pay-fast.online/electricity",
    "http://verify-account-now.info/sbi"
]

SCAM_NOTES = [
    "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs {amt} immediately",
    "DEAR CUSTOMER, your account is suspended due to missing KYC. Update immediately at link or legal action taken.",
    "COURIER ALERT: International parcel held at customs due to unpaid duty Rs {amt}. Pay immediately to release.",
    "Dear User, customer support refund of Rs 5000 is approved. Pay processing fee of Rs {amt} at refund portal.",
    "URGENT: Income tax refund pending. Pay service tax Rs {amt} immediately or account blocked.",
    "Urgent: Electric bill due. Avoid penalty of Rs 5000. Pay now at link."
]

LEGIT_NOTES = [
    "Monthly electricity bill payment ref #{ref}",
    "Payment for shopping order #{ref} via UPI",
    "Quarterly fee payment ref #{ref}",
    "Local hardware purchase tools",
    "Routine grocery order payment",
    "Payment for laptop order #{ref}"
]

CUSTOMERS = [f"CUST-{i:03d}" for i in range(1, 51)]

def generate_expanded_evaluation_dataset(seed: int = 42, target_count: int = 400) -> List[Dict[str, Any]]:
    """Generates a reproducible evaluation dataset of synthetic test scenarios across 8 categories."""
    random.seed(seed)
    scenarios = []
    sc_id = 0

    # A. Normal Legitimate Payments (80 scenarios)
    for _ in range(80):
        sc_id += 1
        m_name, r_id, url = random.choice(LEGIT_MERCHANTS[:3])
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(200.0, 2500.0), 2)
        ref = random.randint(10000, 99999)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": f"Normal Payment: {m_name}",
            "category": "A_Normal_Legitimate",
            "expected_action": "ALLOW",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": r_id,
                "claimed_merchant": m_name,
                "payment_note": random.choice(LEGIT_NOTES).format(ref=ref),
                "url": url,
                "channel": random.choice(["UPI", "CARD", "NETBANKING"])
            }
        })

    # B. Legitimate But Unusual Payments (50 scenarios)
    for _ in range(50):
        sc_id += 1
        m_name, r_id, url = random.choice(LEGIT_MERCHANTS[:3])
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(45000.0, 95000.0), 2) # High value
        ref = random.randint(10000, 99999)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": f"High-Value Legitimate: {m_name}",
            "category": "B_Legitimate_Unusual",
            "expected_action": "VERIFY",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": r_id,
                "claimed_merchant": m_name,
                "payment_note": f"High-value purchase ref #{ref} at {m_name}",
                "url": url,
                "channel": "UPI"
            }
        })

    # C. Clear Social-Engineering Attacks (60 scenarios)
    for _ in range(60):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(1500.0, 12000.0), 2)
        url = random.choice(SUSPICIOUS_DOMAINS)
        note_tpl = random.choice(SCAM_NOTES)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Social Engineering Disconnection Scam",
            "category": "C_Social_Engineering_Attack",
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-004", # Mismatched recipient
                "claimed_merchant": "BESCOM Electricity Board",
                "payment_note": note_tpl.format(amt=amt),
                "url": url,
                "channel": "UPI"
            }
        })

    # D. Merchant Impersonation (50 scenarios)
    for _ in range(50):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(3000.0, 25000.0), 2)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Merchant Identity Impersonation",
            "category": "D_Merchant_Impersonation",
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-005", # Personal account claiming corporate bank
                "claimed_merchant": "State Bank of India",
                "payment_note": "DEAR CUSTOMER, your account is suspended. Pay fee immediately to unlock.",
                "url": "http://bank-kyc-update.online/login",
                "channel": "UPI"
            }
        })

    # E. Suspicious Destination (50 scenarios)
    for _ in range(50):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(800.0, 8000.0), 2)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Suspicious Phishing Destination",
            "category": "E_Suspicious_Destination",
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-006",
                "claimed_merchant": "India Post Express",
                "payment_note": "International parcel duty clearance payment",
                "url": random.choice(SUSPICIOUS_DOMAINS),
                "channel": "UPI"
            }
        })

    # F. Recipient Anomalies (40 scenarios)
    for _ in range(40):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(2000.0, 15000.0), 2)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Unverified Recipient Anomaly",
            "category": "F_Recipient_Anomalies",
            "expected_action": "VERIFY",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-003", # New local merchant
                "claimed_merchant": "Local General Store",
                "payment_note": "Payment for supplies",
                "url": "https://sbi.co.in/portal/pay",
                "channel": "UPI"
            }
        })

    # G. Conflicting Signals (40 scenarios)
    for _ in range(40):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(4000.0, 18000.0), 2)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Conflicting Merchant Identity & URL",
            "category": "G_Conflicting_Signals",
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-004", # Mismatched personal payee
                "claimed_merchant": "City Power Supply",
                "payment_note": "Monthly bill payment",
                "url": "http://elect-pay-bill.top/pay",
                "channel": "UPI"
            }
        })

    # H. Ambiguous Cases (30 scenarios)
    for _ in range(30):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(300.0, 3500.0), 2)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Ambiguous Payment Request",
            "category": "H_Ambiguous_Cases",
            "expected_action": "HOLD",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-005",
                "claimed_merchant": "Customer Service Portal",
                "payment_note": "Customer support fee Rs 199",
                "url": "http://refund-support-portal.site/fee",
                "channel": "UPI"
            }
        })

    os.makedirs(os.path.dirname(EVAL_DATASET_PATH), exist_ok=True)
    with open(EVAL_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)

    return scenarios

if __name__ == "__main__":
    data = generate_expanded_evaluation_dataset()
    print(f"[+] Expanded synthetic evaluation dataset generated successfully: {len(data)} scenarios saved to {EVAL_DATASET_PATH}")
