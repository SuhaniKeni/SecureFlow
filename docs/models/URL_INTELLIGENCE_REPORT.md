# SecureFlow: URL / Destination Intelligence Engine Report (Stage 5.5)

This report presents the model evaluation, metrics comparison, and structured evidence schema for the URL Intelligence Component.

## 1. Model Comparison Matrix

| Model Name | Precision | Recall | F1-Score | PR-AUC | Confusion Matrix (TN, FP, FN, TP) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Baseline)** | 0.9601 | 0.9965 | **0.978** | **0.9949** | `[14305, 837, 71, 20157]` |
| **Random Forest** | 0.9492 | 0.9911 | **0.9697** | **0.9899** | `[14069, 1073, 181, 20047]` |
| **Gradient Boosting** | 0.9901 | 0.9947 | **0.9924** | **0.9956** | `[14940, 202, 107, 20121]` |

**Selected Production Model**: `Gradient Boosting`

---

## 2. Structured Evidence Output Contract

As mandated by architectural principles, the URL Intelligence component returns **STRUCTURED EVIDENCE ONLY** and never financial actions (`ALLOW`/`BLOCK`).

```json
{
  "signal": "suspicious_destination",
  "risk_score": 0.9625,
  "severity": "high",
  "evidence": {
    "domain": "elect-pay-bill.top",
    "url_length": 32,
    "has_https": false,
    "is_ip": false,
    "typosquatted_keyword_detected": true,
    "phishing_probability": 0.9625
  }
}
```
