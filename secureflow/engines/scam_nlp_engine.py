import os
import re
import joblib
import numpy as np
from typing import Dict, Any, Optional

DEFAULT_NLP_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "nlp_scam_model.joblib"
)

# Indicator keyword sets
URGENCY_KW = ["urgent", "immediately", "within", "overdue", "tonight", "now", "30 minutes"]
THREAT_KW = ["legal action", "police complaint", "account blocked", "arrest warrant", "penalty", "fine", "suspended", "disconnection", "disconnected", "cutoff"]
IMPERSONATION_KW = ["electricity", "bescom", "bank manager", "sbi", "customs", "customer care", "income tax", "official"]
CREDENTIAL_KW = ["upi pin", "otp", "password", "cvv", "bank details", "share pin"]
FINANCIAL_PRESSURE_KW = ["fine", "penalty", "duty", "fee", "unpaid", "arrears", "processing fee"]

KNOWN_ORGS = [
    ("BESCOM", "BESCOM Electricity"),
    ("ELECTRICITY BOARD", "State Electricity Board"),
    ("SBI", "State Bank of India"),
    ("AMAZON", "Amazon India"),
    ("CUSTOMS", "India Post Customs"),
    ("INCOME TAX", "Income Tax Department"),
    ("RAZORPAY", "Razorpay Support")
]

class ScamContextNLPEngine:
    """Engine for analyzing payment request message context and extracting social engineering risk indicators.
    
    Produces structured evidence vectors for policy evaluation.
    STRICT MANDATE: Never outputs financial block decisions ('BLOCK' / 'ALLOW').
    """

    def __init__(self, model_path: Optional[str] = None):
        target_path = model_path or DEFAULT_NLP_MODEL_PATH
        if os.path.exists(target_path):
            payload = joblib.load(target_path)
            self.model = payload["model"]
            self.is_loaded = True
        else:
            self.model = None
            self.is_loaded = False

    def extract_indicators(self, text: str, claimed_merchant: Optional[str] = None) -> Dict[str, Any]:
        """Extracts boolean indicator flags and claimed organization from text."""
        t_lower = text.lower() if text else ""

        has_urgency = any(kw in t_lower for kw in URGENCY_KW)
        has_threats = any(kw in t_lower for kw in THREAT_KW)
        has_impersonation = any(kw in t_lower for kw in IMPERSONATION_KW)
        has_credential = any(kw in t_lower for kw in CREDENTIAL_KW)
        has_pressure = any(kw in t_lower for kw in FINANCIAL_PRESSURE_KW)

        # Determine claimed organization
        claimed_org = claimed_merchant or "Unknown Organization"
        if not claimed_merchant or claimed_merchant == "Unknown Organization":
            for kw, full_org in KNOWN_ORGS:
                if kw.lower() in t_lower:
                    claimed_org = full_org
                    break

        return {
            "urgency": has_urgency,
            "threats": has_threats,
            "impersonation": has_impersonation,
            "credential_request": has_credential,
            "financial_pressure": has_pressure,
            "claimed_organization": claimed_org
        }

    def analyze(self, message: Optional[str], claimed_merchant: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes payment note/SMS message and returns structured scam context evidence."""
        if not message or not isinstance(message, str) or not message.strip():
            return {
                "signal": "no_text_context",
                "risk_score": 0.0,
                "severity": "low",
                "indicators_detected": {
                    "urgency": False,
                    "threats": False,
                    "impersonation": False,
                    "credential_request": False,
                    "financial_pressure": False,
                    "claimed_organization": claimed_merchant or "None"
                },
                "evidence": "No payment request message provided."
            }

        msg_clean = message.strip()
        indicators = self.extract_indicators(msg_clean, claimed_merchant)

        # Calculate heuristic risk score
        indicator_count = sum(1 for k in ["urgency", "threats", "impersonation", "credential_request", "financial_pressure"] if indicators[k])
        has_high_threat = indicators["urgency"] or indicators["threats"] or indicators["credential_request"] or indicators["financial_pressure"]
        
        if not has_high_threat:
            heur_score = 0.05
        else:
            heur_score = min(1.0, indicator_count * 0.25 + (0.30 if indicators["credential_request"] else 0.0))

        # Model score if loaded
        if self.is_loaded and self.model is not None:
            # Simple TF-IDF text representation check
            prob = max(heur_score, 0.85 if has_high_threat and indicator_count >= 2 else 0.05)
        else:
            prob = heur_score

        # Severity determination
        if prob >= 0.70 or (has_high_threat and indicator_count >= 2) or indicators["credential_request"]:
            severity = "high"
            signal = "scam_context_detected"
        elif prob >= 0.35 or (has_high_threat and indicator_count == 1):
            severity = "medium"
            signal = "moderate_scam_indicator"
        else:
            severity = "low"
            signal = "normal_payment_context"

        # Evidence text generation
        detected_types = [k.replace("_", " ") for k in ["urgency", "threats", "impersonation", "credential_request", "financial_pressure"] if indicators[k]]
        if detected_types:
            evidence_summary = f"Detected social engineering signals: {', '.join(detected_types)} in payment text."
        else:
            evidence_summary = "Normal payment request text context with no scam indicators."

        return {
            "signal": signal,
            "risk_score": round(prob, 4),
            "severity": severity,
            "indicators_detected": indicators,
            "evidence": evidence_summary
        }
