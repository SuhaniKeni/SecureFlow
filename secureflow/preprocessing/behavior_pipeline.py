import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from secureflow.db.models import Customer, Transaction

def compute_behavior_features(session: Session) -> pd.DataFrame:
    """Computes customer behavioral features and anomaly scores from database transactions."""
    customers = {c.customer_id: c for c in session.query(Customer).all()}
    transactions = session.query(Transaction).order_by(Transaction.timestamp).all()

    records = []
    customer_history = {} # customer_id -> list of timestamps for velocity computation

    for t in transactions:
        c = customers.get(t.customer_id)
        if not c:
            continue

        mean_amt = c.normal_avg_amount if c.normal_avg_amount > 0 else 1000.0
        std_amt = c.normal_std_amount if c.normal_std_amount > 0 else 300.0

        # Calculate Z-score
        z_score = (t.amount - mean_amt) / std_amt
        is_unusual = 1 if abs(z_score) > 2.5 else 0

        # Calculate Hour Anomaly
        t_hour = t.timestamp.hour
        normal_hours = c.normal_payment_hours or [8, 22]
        hour_anomaly = 1 if (t_hour < normal_hours[0] or t_hour > normal_hours[1]) else 0

        # Velocity tracking (transactions in past 1 hour and past 24 hours)
        history = customer_history.get(t.customer_id, [])
        v1h = sum(1 for ts in history if (t.timestamp - ts).total_seconds() <= 3600)
        v24h = sum(1 for ts in history if (t.timestamp - ts).total_seconds() <= 86400)
        history.append(t.timestamp)
        customer_history[t.customer_id] = history

        # Is Legitimate Unusual transaction (e.g., SCN-007 high-value electronics)
        is_legitimate_unusual = 1 if (t.scenario_id == "SCN-007" or (is_unusual and t.status == "SUCCESS")) else 0

        records.append({
            "transaction_id": t.transaction_id,
            "customer_id": t.customer_id,
            "amount": t.amount,
            "mean_amount": mean_amt,
            "std_amount": std_amt,
            "amount_zscore": round(z_score, 4),
            "is_unusual_amount": is_unusual,
            "hour_anomaly": hour_anomaly,
            "velocity_1h": v1h,
            "velocity_24h": v24h,
            "is_legitimate_unusual": is_legitimate_unusual,
            "status": t.status,
            "scenario_id": t.scenario_id
        })

    return pd.DataFrame(records)
