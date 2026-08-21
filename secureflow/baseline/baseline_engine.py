from typing import Dict, Any
from secureflow.baseline.baseline_policy import BaselinePolicyEngine

class BaselineProtectionEngine:
    """Wrapper component for executing conventional baseline risk evaluations."""

    def __init__(self):
        self.policy = BaselinePolicyEngine()

    def analyze_payment(self, payment_request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates raw payment request against baseline rule engine."""
        return self.policy.evaluate_payment(payment_request)
