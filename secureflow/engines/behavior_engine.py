import os
import numpy as np
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from secureflow.db.models import Customer, Transaction, Recipient

class CustomerBehaviorEngine:
    """Engine for comparing current payment transactions against customer historical baselines.
    
    Uses interpretable statistical anomaly methods (z-scores, recipient history, velocity bounds).
    Preserves legitimate unusual behavior without treating every statistical anomaly as fraud.
    STRICT MANDATE: Never outputs financial block decisions ('BLOCK' / 'ALLOW').
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.session = db_session

    def analyze_transaction(
        self,
        customer_id: str,
        amount: float,
        recipient_id: str,
        merchant_category: Optional[str] = None,
        timestamp=None,
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Compares transaction against customer profile baseline and outputs structured behavioral evidence."""
        session = db_session or self.session
        if not session:
            # Fallback inline statistical evaluation if DB session not passed
            return self._heuristic_fallback(amount, recipient_id)

        # 1. Fetch Customer Profile
        customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            return {
                "signal": "new_customer_no_history",
                "risk_score": 0.30,
                "severity": "medium",
                "behavior_metrics": {
                    "amount_zscore": 0.0,
                    "is_new_recipient": True,
                    "hour_anomaly": False,
                    "velocity_1h": 1,
                    "category_deviation": False
                },
                "evidence": f"New customer profile '{customer_id}' with no prior historical transaction baseline."
            }

        # 2. Historical Amount Baseline & Z-Score
        mean_amt = customer.normal_avg_amount if customer.normal_avg_amount > 0 else 1000.0
        std_amt = customer.normal_std_amount if customer.normal_std_amount > 0 else 300.0
        z_score = (amount - mean_amt) / std_amt

        # 3. Recipient Novelty Check
        prior_txns = session.query(Transaction).filter(
            Transaction.customer_id == customer_id
        ).all()

        prior_recipients = set(t.recipient_id for t in prior_txns)
        is_new_recipient = recipient_id not in prior_recipients

        # 4. Timing Anomaly Check
        t_hour = timestamp.hour if timestamp else 12
        normal_hours = customer.normal_payment_hours or [0, 23]
        is_hour_anomaly = (t_hour < normal_hours[0] or t_hour > normal_hours[1])

        # Velocity tracking (transactions in past 1 hour and past 24 hours)
        def to_naive(dt):
            return dt.replace(tzinfo=None) if (dt and hasattr(dt, "tzinfo") and dt.tzinfo) else dt

        ts_naive = to_naive(timestamp)
        if ts_naive:
            v1h = sum(1 for t in prior_txns if abs((ts_naive - to_naive(t.timestamp)).total_seconds()) <= 3600)
            v24h = sum(1 for t in prior_txns if abs((ts_naive - to_naive(t.timestamp)).total_seconds()) <= 86400)
        else:
            v1h = 1
            v24h = len(prior_txns)

        # Calculate Behavioral Risk Score (Interpretable Statistical Model)
        score_components = []
        if z_score > 3.0:
            score_components.append(0.40) # High amount variance
        elif z_score > 2.0:
            score_components.append(0.20)

        if is_new_recipient:
            score_components.append(0.25)

        if is_hour_anomaly:
            score_components.append(0.15)

        if v1h > 3:
            score_components.append(0.30)

        risk_score = min(1.0, sum(score_components))

        # Severity Determination
        if risk_score >= 0.60:
            severity = "medium" # Note: Behavior component caps at medium to avoid declaring fraud on amount alone
            signal = "high_behavioral_deviation"
            evidence_str = f"Transaction amount Rs {amount:,.2f} (z-score: {z_score:.2f}) and new recipient indicate significant baseline deviation."
        elif risk_score >= 0.30:
            severity = "medium"
            signal = "unusual_amount_pattern" if z_score > 2.0 else "unusual_behavior_pattern"
            evidence_str = f"Transaction amount Rs {amount:,.2f} is substantially above customer historical mean Rs {mean_amt:,.2f}."
        else:
            severity = "low"
            signal = "normal_behavior_pattern"
            evidence_str = f"Transaction amount Rs {amount:,.2f} and velocity fall within customer's normal historical baseline."

        return {
            "signal": signal,
            "risk_score": round(risk_score, 4),
            "severity": severity,
            "behavior_metrics": {
                "amount_zscore": round(z_score, 2),
                "is_new_recipient": is_new_recipient,
                "hour_anomaly": is_hour_anomaly,
                "velocity_1h": v1h,
                "velocity_24h": v24h,
                "historical_avg_amount": mean_amt
            },
            "evidence": evidence_str
        }

    def _heuristic_fallback(self, amount: float, recipient_id: str) -> Dict[str, Any]:
        """Fallback evaluation if database session is unavailable."""
        z_score = round((amount - 1500.0) / 500.0, 2)
        severity = "medium" if abs(z_score) > 2.5 else "low"
        return {
            "signal": "unusual_amount" if abs(z_score) > 2.5 else "normal_amount",
            "risk_score": 0.40 if abs(z_score) > 2.5 else 0.10,
            "severity": severity,
            "behavior_metrics": {
                "amount_zscore": z_score,
                "is_new_recipient": True,
                "hour_anomaly": False,
                "velocity_1h": 1
            },
            "evidence": f"Transaction amount Rs {amount:,.2f} evaluated using baseline fallback limits."
        }
