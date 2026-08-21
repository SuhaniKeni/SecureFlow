import os
import json
import random
from typing import List, Dict, Any

EVAL_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "expanded_eval_scenarios.json"
)

# Diverse Legitimate Domains & Subdomains
LEGIT_DOMAINS = [
    "https://bescom.co.in/pay",
    "https://pay.bescom.co.in/quickpay",
    "https://amazon.in/checkout/pay",
    "https://checkout.amazon.in/order",
    "https://sbi.co.in/portal/pay",
    "https://retail.onlinesbi.sbi/pay",
    "https://swiggy.com/checkout",
    "https://indiapost.gov.in/pay",
    "https://customs.indiapost.gov.in/duty"
]

# Diverse Phishing & Suspicious Domains (Preventing 10-domain shortcut)
SUSPICIOUS_DOMAINS = [
    "http://elect-pay-bill.top/pay",
    "http://bescom-disconnection-notice.site/pay",
    "http://electricity-bill-clearance.online/bill",
    "http://bank-kyc-update.online/login",
    "http://sbi-account-verify.info/login",
    "http://statebank-kyc-portal.xyz/update",
    "http://customs-clearance-pay.com/duty",
    "http://indiapost-duty-refund.club/pay",
    "http://refund-support-portal.site/fee",
    "http://customercare-refund-pay.live/claim",
    "http://incometax-refund-gov.in.net/claim",
    "http://tax-refund-approval.info/pay",
    "http://bill-pay-fast.online/electricity",
    "http://urgent-pay-bill.site/utility",
    "http://fast-checkout-pay.top/merchant",
    "http://quick-verify-payment.online/sbi"
]

# Diverse Scam Messages
SCAM_NOTE_TEMPLATES = [
    "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs {amt} immediately",
    "DEAR CUSTOMER, your account is suspended due to missing KYC. Update immediately at link or legal action taken.",
    "COURIER ALERT: International parcel held at customs due to unpaid duty Rs {amt}. Pay immediately to release.",
    "Dear User, customer support refund of Rs 5000 is approved. Pay processing fee of Rs {amt} at refund portal.",
    "URGENT: Income tax refund pending. Pay service tax Rs {amt} immediately or account blocked.",
    "Urgent: Electric bill due ref #{ref}. Avoid penalty of Rs 5000. Pay now at link.",
    "FINAL WARNING: Outstanding power bill Rs {amt}. Disconnection scheduled within 2 hours. Pay immediately.",
    "BANK NOTICE: Unusual activity detected. Verify identity ref #{ref} immediately or debit card blocked.",
    "PARCEL DELAY: Unpaid customs duty fee Rs {amt} for shipment #{ref}. Release package online."
]

# Diverse Legitimate Notes
LEGIT_NOTE_TEMPLATES = [
    "Monthly electricity bill payment ref #{ref}",
    "Payment for shopping order #{ref} via UPI",
    "Quarterly maintenance fee payment ref #{ref}",
    "Local hardware purchase tools and materials",
    "Routine grocery order payment #{ref}",
    "Payment for laptop order #{ref}",
    "Monthly broadband bill payment ref #{ref}",
    "Mobile recharge plan renewal ref #{ref}",
    "Dining order checkout payment ref #{ref}"
]

CUSTOMERS = [f"CUST-{i:03d}" for i in range(1, 51)]
RECIPIENTS = ["RCP-001", "RCP-002", "RCP-003", "RCP-004", "RCP-005", "RCP-006"]
MERCHANTS = [
    "BESCOM Electricity", "Amazon India", "State Bank of India",
    "Swiggy Food Delivery", "India Post Express", "Local Hardware Store",
    "City Power Supply", "Customer Service Portal"
]

def generate_expanded_evaluation_dataset(seed: int = 42, target_count: int = 400) -> List[Dict[str, Any]]:
    """Generates a non-leaking, realistic 400-scenario evaluation dataset across 8 categories."""
    random.seed(seed)
    scenarios = []
    sc_id = 0

    # A. Normal Legitimate Payments (80 scenarios)
    for _ in range(80):
        sc_id += 1
        m_name = random.choice(MERCHANTS[:5])
        r_id = random.choice(["RCP-001", "RCP-002", "RCP-003"])
        url = random.choice(LEGIT_DOMAINS)
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(150.0, 4500.0), 2)
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
                "payment_note": random.choice(LEGIT_NOTE_TEMPLATES).format(ref=ref),
                "url": url,
                "channel": random.choice(["UPI", "CARD", "NETBANKING"])
            }
        })

    # B. Legitimate But Unusual Payments (50 scenarios)
    for _ in range(50):
        sc_id += 1
        m_name = random.choice(MERCHANTS[:5])
        r_id = random.choice(["RCP-001", "RCP-002", "RCP-003"])
        url = random.choice(LEGIT_DOMAINS)
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(12000.0, 85000.0), 2) # Overlapping high value
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
        amt = round(random.uniform(1200.0, 15000.0), 2) # Overlapping amount
        url = random.choice(SUSPICIOUS_DOMAINS)
        ref = random.randint(10000, 99999)
        note_tpl = random.choice(SCAM_NOTE_TEMPLATES)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Social Engineering Disconnection Scam",
            "category": "C_Social_Engineering_Attack",
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": random.choice(["RCP-004", "RCP-005"]),
                "claimed_merchant": "BESCOM Electricity Board",
                "payment_note": note_tpl.format(amt=amt, ref=ref),
                "url": url,
                "channel": "UPI"
            }
        })

    # D. Merchant Impersonation (50 scenarios)
    for _ in range(50):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(2500.0, 35000.0), 2)
        ref = random.randint(10000, 99999)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Merchant Identity Impersonation",
            "category": "D_Merchant_Impersonation",
            "expected_action": "BLOCK",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-005", # Personal payee claiming corporate bank
                "claimed_merchant": "State Bank of India",
                "payment_note": f"DEAR CUSTOMER, SBI account #{ref} suspended. Pay fee immediately to unlock.",
                "url": random.choice([u for u in SUSPICIOUS_DOMAINS if "sbi" in u or "bank" in u or "verify" in u]),
                "channel": "UPI"
            }
        })

    # E. Suspicious Destination (50 scenarios)
    for _ in range(50):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(500.0, 9500.0), 2)
        ref = random.randint(10000, 99999)
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
                "payment_note": f"International parcel duty clearance payment ref #{ref}",
                "url": random.choice(SUSPICIOUS_DOMAINS),
                "channel": "UPI"
            }
        })

    # F. Recipient Anomalies (40 scenarios)
    for _ in range(40):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(1500.0, 18000.0), 2)
        ref = random.randint(10000, 99999)
        scenarios.append({
            "scenario_id": f"EVAL-{sc_id:04d}",
            "scenario_name": "Unverified Recipient Anomaly",
            "category": "F_Recipient_Anomalies",
            "expected_action": "VERIFY",
            "input": {
                "customer_id": c_id,
                "amount": amt,
                "recipient_id": "RCP-003", # New local merchant
                "claimed_merchant": "Local Hardware Store",
                "payment_note": f"Payment for supplies ref #{ref}",
                "url": "https://sbi.co.in/portal/pay",
                "channel": "UPI"
            }
        })

    # G. Conflicting Signals (40 scenarios)
    for _ in range(40):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(3000.0, 22000.0), 2)
        ref = random.randint(10000, 99999)
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
                "payment_note": f"Monthly bill payment ref #{ref}",
                "url": random.choice([u for u in SUSPICIOUS_DOMAINS if "elect" in u or "bill" in u]),
                "channel": "UPI"
            }
        })

    # H. Ambiguous Cases (30 scenarios)
    for _ in range(30):
        sc_id += 1
        c_id = random.choice(CUSTOMERS)
        amt = round(random.uniform(200.0, 4500.0), 2)
        ref = random.randint(10000, 99999)
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
                "payment_note": f"Customer support fee Rs {amt} ref #{ref}",
                "url": random.choice([u for u in SUSPICIOUS_DOMAINS if "refund" in u or "support" in u]),
                "channel": "UPI"
            }
        })

    os.makedirs(os.path.dirname(EVAL_DATASET_PATH), exist_ok=True)
    with open(EVAL_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)

    return scenarios

if __name__ == "__main__":
    data = generate_expanded_evaluation_dataset()
    print(f"[+] Expanded synthetic evaluation dataset regenerated successfully: {len(data)} scenarios saved to {EVAL_DATASET_PATH}")
