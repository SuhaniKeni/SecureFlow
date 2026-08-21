import os
import json
import random
from typing import List, Dict, Any

UNSEEN_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "unseen_eval_scenarios.json"
)

# Completely Unseen Phishing Domains & TLDs (Not present in development/400-scenario dataset)
UNSEEN_DOMAINS = [
    "http://city-utility-settlement.online/pay",
    "http://municipal-water-clearance.top/bill",
    "http://traffic-challan-portal.tech/pay",
    "http://insurance-policy-dividend.live/claim",
    "http://sec-account-restore.info/verify",
    "http://express-courier-tax.site/duty",
    "http://state-tax-settlement.net/claim"
]

# Legitimate Domains (Standard verified)
LEGIT_DOMAINS = [
    "https://bescom.co.in/pay",
    "https://amazon.in/checkout/pay",
    "https://sbi.co.in/portal/pay",
    "https://swiggy.com/checkout"
]

# Unseen Scam Note Vocabulary & Phrasing Structure
UNSEEN_SCAM_NOTES = [
    "NOTICE: Service access scheduled for interruption due to pending dues Rs {amt}. Complete settlement ref #{ref}.",
    "TRAFFIC VIOLATION: E-challan #{ref} issued. Immediate online payment of Rs {amt} required to avoid court summons.",
    "INSURANCE UPDATE: Policy maturity bonus approved ref #{ref}. Pay processing administrative fee Rs {amt} to credit.",
    "SECURITY ALERT: Account access restricted ref #{ref}. Re-verify security credentials immediately via portal link.",
    "TAX ADVISORY: Administrative surcharge Rs {amt} pending ref #{ref}. Submit payment to complete filing."
]

# Legitimate Notes (Diverse wording)
UNSEEN_LEGIT_NOTES = [
    "Annual vehicle insurance renewal premium ref #{ref}",
    "Payment for office equipment purchase ref #{ref}",
    "Routine monthly utility bill settlement ref #{ref}",
    "Local merchant payment for renovation supplies #{ref}",
    "Online course subscription fee ref #{ref}"
]

CUSTOMERS = [f"CUST-{i:03d}" for i in range(1, 51)]

def generate_unseen_evaluation_dataset(seed: int = 100, target_count: int = 150) -> List[Dict[str, Any]]:
    """Generates 150 unseen evaluation scenarios with distinct phrasing, domains, and categories."""
    random.seed(seed)
    scenarios = []
    sc_id = 0

    # 1. Unseen Utility Threat Scenarios (25 scenarios)
    for _ in range(25):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(1500.0, 9500.0), 2)
        ref = random.randint(100000, 999999)
        scenarios.append({
            "scenario_id": f"UNSEEN-{sc_id:04d}",
            "scenario_name": "Unseen Category: Utility Interruption Scam",
            "category": "Unseen_Category_Utility",
            "is_seen_category": False,
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-004",
                "claimed_merchant": "City Municipal Utility",
                "payment_note": random.choice(UNSEEN_SCAM_NOTES[:1]).format(amt=amt, ref=ref),
                "url": UNSEEN_DOMAINS[0],
                "channel": "UPI"
            }
        })

    # 2. Unseen Government Challan / Tax Scenarios (25 scenarios)
    for _ in range(25):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(500.0, 4500.0), 2)
        ref = random.randint(100000, 999999)
        scenarios.append({
            "scenario_id": f"UNSEEN-{sc_id:04d}",
            "scenario_name": "Unseen Category: Traffic E-Challan Scam",
            "category": "Unseen_Category_Challan",
            "is_seen_category": False,
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-005",
                "claimed_merchant": "Traffic Police E-Challan",
                "payment_note": random.choice(UNSEEN_SCAM_NOTES[1:2]).format(amt=amt, ref=ref),
                "url": UNSEEN_DOMAINS[2],
                "channel": "UPI"
            }
        })

    # 3. Unseen Insurance Dividend Bait Scenarios (25 scenarios)
    for _ in range(25):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(1200.0, 8500.0), 2)
        ref = random.randint(100000, 999999)
        scenarios.append({
            "scenario_id": f"UNSEEN-{sc_id:04d}",
            "scenario_name": "Unseen Category: Insurance Bonus Scam",
            "category": "Unseen_Category_Insurance",
            "is_seen_category": False,
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-006",
                "claimed_merchant": "Life Insurance Care",
                "payment_note": random.choice(UNSEEN_SCAM_NOTES[2:3]).format(amt=amt, ref=ref),
                "url": UNSEEN_DOMAINS[3],
                "channel": "UPI"
            }
        })

    # 4. Legitimate Unusual Purchases (35 scenarios)
    for _ in range(35):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(25000.0, 75000.0), 2)
        ref = random.randint(100000, 999999)
        scenarios.append({
            "scenario_id": f"UNSEEN-{sc_id:04d}",
            "scenario_name": "Legitimate High-Value Purchase",
            "category": "Legitimate_Unusual",
            "is_seen_category": True,
            "expected_action": "VERIFY",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-002",
                "claimed_merchant": "Amazon India",
                "payment_note": random.choice(UNSEEN_LEGIT_NOTES[:2]).format(ref=ref),
                "url": LEGIT_DOMAINS[1],
                "channel": "UPI"
            }
        })

    # 5. Legitimate Routine Payments (40 scenarios)
    for _ in range(40):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(300.0, 3500.0), 2)
        ref = random.randint(100000, 999999)
        scenarios.append({
            "scenario_id": f"UNSEEN-{sc_id:04d}",
            "scenario_name": "Legitimate Routine Settlement",
            "category": "Legitimate_Routine",
            "is_seen_category": True,
            "expected_action": "ALLOW",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-001",
                "claimed_merchant": "BESCOM Electricity",
                "payment_note": random.choice(UNSEEN_LEGIT_NOTES[2:]).format(ref=ref),
                "url": LEGIT_DOMAINS[0],
                "channel": random.choice(["UPI", "CARD", "NETBANKING"])
            }
        })

    os.makedirs(os.path.dirname(UNSEEN_DATASET_PATH), exist_ok=True)
    with open(UNSEEN_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)

    return scenarios

if __name__ == "__main__":
    data = generate_unseen_evaluation_dataset()
    print(f"[+] Unseen evaluation dataset generated successfully: {len(data)} scenarios saved to {UNSEEN_DATASET_PATH}")
