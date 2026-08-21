# SecureFlow: Scam-Context NLP Engine Report (Stage 5.6)

This report presents the model evaluation, indicator extraction specs, and structured evidence schema for the Scam-Context NLP Component.

## 1. Model Comparison Matrix

| Model Name | Precision | Recall | F1-Score | PR-AUC | Confusion Matrix (TN, FP, FN, TP) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TF-IDF + Logistic Regression (Baseline)** | 0.9495 | 0.8393 | **0.891** | **0.9735** | `[720, 5, 18, 94]` |
| **TF-IDF + Multinomial Naive Bayes** | 0.9159 | 0.875 | **0.895** | **0.962** | `[716, 9, 14, 98]` |
| **TF-IDF + Random Forest** | 1.0 | 0.6696 | **0.8021** | **0.9637** | `[725, 0, 37, 75]` |
| **TF-IDF + Gradient Boosting** | 0.9485 | 0.8214 | **0.8804** | **0.944** | `[720, 5, 20, 92]` |

**Selected Production Model**: `TF-IDF + Multinomial Naive Bayes`

---

## 2. Contextual Scam Indicators Extracted

* **Urgency**: `overdue`, `immediately`, `within 10 mins`, `disconnection`, `tonight`, `cutoff`
* **Impersonation**: `electricity board`, `BESCOM`, `bank manager`, `customs`, `customer care`, `tax`
* **Threats**: `legal action`, `police complaint`, `account blocked`, `arrest warrant`
* **Credential Request**: `upi pin`, `otp`, `password`, `share details`
* **Financial Pressure**: `fine`, `penalty`, `processing fee`, `unpaid duty`

---

## 3. Structured Evidence Output Contract

```json
{
  "signal": "scam_context_detected",
  "risk_score": 0.9450,
  "severity": "high",
  "indicators_detected": {
    "urgency": true,
    "threats": true,
    "impersonation": true,
    "credential_request": false,
    "financial_pressure": true,
    "claimed_organization": "BESCOM Electricity"
  },
  "evidence": "Urgent utility disconnection threat and organization impersonation detected in payment text."
}
```
