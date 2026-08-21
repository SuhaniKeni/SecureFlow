import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from secureflow.engines.url_intel_engine import URLIntelligenceEngine
from secureflow.engines.scam_nlp_engine import ScamContextNLPEngine
from secureflow.engines.behavior_engine import CustomerBehaviorEngine
from secureflow.engines.merchant_engine import MerchantConsistencyEngine
from secureflow.aggregation.evidence_aggregator import EvidenceAggregator
from secureflow.policy.decision_engine import ProtectionDecisionEngine
from secureflow.explanations.explanation_engine import ExplanationEngine

BENCHMARK_SCENARIOS = [
    {
        "scenario_id": "SCN-001",
        "scenario_name": "1. Legitimate Recurring Electricity Payment",
        "category": "Legitimate Normal",
        "input": {
            "customer_id": "CUST-001",
            "amount": 1450.00,
            "recipient_id": "RCP-001",
            "claimed_merchant": "BESCOM Electricity",
            "payment_note": "Monthly electricity bill payment ref #400192839",
            "url": "https://bescom.co.in/pay",
            "channel": "UPI"
        },
        "expected_action": "ALLOW"
    },
    {
        "scenario_id": "SCN-002",
        "scenario_name": "2. Fake Electricity Disconnection Payment Scam",
        "category": "Social Engineering Attack",
        "input": {
            "customer_id": "CUST-001",
            "amount": 8742.00,
            "recipient_id": "RCP-004",
            "claimed_merchant": "BESCOM Electricity Board",
            "payment_note": "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
            "url": "http://elect-pay-bill.top/pay",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-003",
        "scenario_name": "3. Fake Bank Security Alert / KYC Phishing",
        "category": "Phishing Attack",
        "input": {
            "customer_id": "CUST-002",
            "amount": 15000.00,
            "recipient_id": "RCP-005",
            "claimed_merchant": "State Bank of India",
            "payment_note": "DEAR CUSTOMER, your account is suspended due to missing KYC. Update immediately or legal action will be taken.",
            "url": "http://bank-kyc-update.online/login",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-004",
        "scenario_name": "4. Fake Courier Duty / Customs Payment",
        "category": "Impersonation Attack",
        "input": {
            "customer_id": "CUST-003",
            "amount": 1499.00,
            "recipient_id": "RCP-006",
            "claimed_merchant": "India Post Express",
            "payment_note": "COURIER ALERT: International parcel held at customs due to unpaid duty Rs 1499. Pay immediately to release.",
            "url": "http://customs-clearance-pay.com/duty",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-005",
        "scenario_name": "5. Fake Customer-Support Refund Fee Scam",
        "category": "Refund Bait Attack",
        "input": {
            "customer_id": "CUST-004",
            "amount": 199.00,
            "recipient_id": "RCP-005",
            "claimed_merchant": "Customer Care Refund Portal",
            "payment_note": "Dear User, customer support refund of Rs 4999 is approved. Pay processing fee of Rs 199 at refund portal.",
            "url": "http://refund-support-portal.site/fee",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-006",
        "scenario_name": "6. Fake Government Income Tax Refund Fee",
        "category": "Government Impersonation",
        "input": {
            "customer_id": "CUST-005",
            "amount": 850.00,
            "recipient_id": "RCP-005",
            "claimed_merchant": "Income Tax Refund Cell",
            "payment_note": "URGENT: Income tax refund Rs 14,200 pending. Pay service tax Rs 850 immediately or account blocked.",
            "url": "http://incometax-refund-gov.in.net/claim",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-007",
        "scenario_name": "7. Legitimate High-Value Laptop Purchase",
        "category": "Legitimate Unusual",
        "input": {
            "customer_id": "CUST-001",
            "amount": 85000.00,
            "recipient_id": "RCP-002",
            "claimed_merchant": "Amazon India",
            "payment_note": "Payment for Apple Laptop order #940182 via Amazon Pay",
            "url": "https://amazon.in/checkout/pay",
            "channel": "UPI"
        },
        "expected_action": "VERIFY"
    },
    {
        "scenario_id": "SCN-008",
        "scenario_name": "8. New Legitimate Local Merchant",
        "category": "Legitimate New Merchant",
        "input": {
            "customer_id": "CUST-002",
            "amount": 3200.00,
            "recipient_id": "RCP-003",
            "claimed_merchant": "Local Hardware Store",
            "payment_note": "Purchase of construction tools",
            "url": "https://sbi.co.in/portal/pay",
            "channel": "UPI"
        },
        "expected_action": "VERIFY"
    },
    {
        "scenario_id": "SCN-009",
        "scenario_name": "9. Suspicious Recipient with Legitimate-Looking Request",
        "category": "Disguised Fraud",
        "input": {
            "customer_id": "CUST-003",
            "amount": 4500.00,
            "recipient_id": "RCP-004",
            "claimed_merchant": "City Power Supply",
            "payment_note": "Payment for monthly electricity charges",
            "url": "http://elect-pay-bill.top/pay",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    },
    {
        "scenario_id": "SCN-010",
        "scenario_name": "10. Merchant Identity Mismatch Scam",
        "category": "Identity Impersonation",
        "input": {
            "customer_id": "CUST-001",
            "amount": 12450.00,
            "recipient_id": "RCP-004",
            "claimed_merchant": "BESCOM Power Supply",
            "payment_note": "Urgent: BESCOM electric bill due. Avoid penalty of Rs 5000. Pay now.",
            "url": "http://bill-pay-fast.online/electricity",
            "channel": "UPI"
        },
        "expected_action": "BLOCK"
    }
]

class SecureFlowAttackSimulator:
    """Benchmark runner for executing controlled attack and legitimate test scenarios."""

    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.url_engine = URLIntelligenceEngine()
        self.nlp_engine = ScamContextNLPEngine()
        self.behavior_engine = CustomerBehaviorEngine(db_session=db_session)
        self.merchant_engine = MerchantConsistencyEngine(db_session=db_session)
        self.aggregator = EvidenceAggregator()
        self.decision_engine = ProtectionDecisionEngine()
        self.explanation_engine = ExplanationEngine()

    def run_scenario(self, scenario_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single scenario and returns complete evaluation trace."""
        inp = scenario_dict["input"]
        exp_action = scenario_dict["expected_action"]

        # 1. Feature Engines Evaluation
        url_ev = self.url_engine.analyze(inp.get("url"))
        nlp_ev = self.nlp_engine.analyze(inp.get("payment_note"), claimed_merchant=inp.get("claimed_merchant"))
        behavior_ev = self.behavior_engine.analyze_transaction(
            customer_id=inp["customer_id"],
            amount=inp["amount"],
            recipient_id=inp["recipient_id"],
            db_session=self.db
        )
        merchant_ev = self.merchant_engine.analyze_consistency(
            claimed_merchant=inp.get("claimed_merchant"),
            recipient_id=inp["recipient_id"],
            destination_url=inp.get("url"),
            db_session=self.db
        )

        # 2. Evidence Fusion
        bundle = self.aggregator.aggregate(
            url_evidence=url_ev,
            nlp_evidence=nlp_ev,
            behavior_evidence=behavior_ev,
            merchant_evidence=merchant_ev
        )

        # 3. Decision Policy
        decision = self.decision_engine.evaluate_protection_policy(bundle)

        # 4. Explanations
        tx_ctx = {"amount": inp["amount"]}
        m_info = {
            "claimed_merchant": inp.get("claimed_merchant"),
            "actual_recipient_name": merchant_ev["consistency_details"].get("actual_recipient_name")
        }
        explanations = self.explanation_engine.generate_explanation(
            protection_action=decision["action"],
            evidence_bundle=bundle,
            transaction_context=tx_ctx,
            merchant_info=m_info
        )

        actual_action = decision["action"]
        is_match = (actual_action == exp_action)

        return {
            "scenario_id": scenario_dict["scenario_id"],
            "scenario_name": scenario_dict["scenario_name"],
            "category": scenario_dict["category"],
            "input": inp,
            "detected_evidence": bundle,
            "protection_action": actual_action,
            "expected_action": exp_action,
            "action_match": is_match,
            "explanation": explanations,
            "reasons": decision["reasons"],
            "recommended_next_step": decision["recommended_next_step"],
            "prevention_recommendation": decision["prevention_recommendation"]
        }

    def run_all_benchmark_scenarios() -> Dict[str, Any]:
        """Executes all 10 benchmark scenarios and calculates suite accuracy."""
        results = []
        matches = 0
        for sc in BENCHMARK_SCENARIOS:
            res = self.run_scenario(sc)
            results.append(res)
            if res["action_match"]:
                matches += 1

        accuracy = round(matches / len(BENCHMARK_SCENARIOS), 4)

        return {
            "total_scenarios": len(BENCHMARK_SCENARIOS),
            "matched_actions": matches,
            "benchmark_accuracy": accuracy,
            "scenario_results": results
        }
