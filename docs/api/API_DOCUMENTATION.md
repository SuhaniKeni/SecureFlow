# SecureFlow: REST API Documentation (Stage 5.12)

The SecureFlow backend provides a high-performance REST API built with FastAPI, OpenAPI 3.0 schemas, and automatic Pydantic validation.

---

## 1. Security & Data Boundary Rules

* **Zero Real Payment Credentials**: The API strictly prohibits and rejects any request containing real payment credentials (`upi_pin`, `card_number`, `cvv`, `password`). Any payload with sensitive credentials immediately returns **400 Unprocessable Entity / Bad Request**.
* **Local Synthetic Environment**: Runs 100% locally against SQLite synthetic databases and open security models.

---

## 2. API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/payments/analyze` | Core security evaluation endpoint (Runs 4 engines, aggregator, decision policy, and explanation generator) |
| `POST` | `/payments/simulate` | Interactive customer checkout UI sandbox simulation endpoint |
| `GET` | `/payments/{id}` | Retrieves payment metadata by transaction ID |
| `GET` | `/protection-events` | Lists historical protection events with action pagination for Risk Ops |
| `GET` | `/protection-events/{id}` | Retrieves full forensic audit trace for a specific event |
| `GET` | `/merchants/{id}` | Retrieves merchant profile and domain verification status |
| `GET` | `/customers/{id}/history` | Retrieves customer profile and baseline transaction history |
| `POST` | `/scenarios/run` | Executes benchmark attack/legitimate test scenario by ID |

---

## 3. Sample Requests & Responses

### `POST /payments/analyze`

#### Request Payload:
```json
{
  "customer_id": "CUST-001",
  "amount": 8742.00,
  "recipient_id": "RCP-004",
  "claimed_merchant": "BESCOM Electricity Board",
  "payment_note": "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
  "url": "http://elect-pay-bill.top/pay",
  "channel": "UPI"
}
```

#### Response Payload (HTTP 200 OK):
```json
{
  "transaction_id": "TXN-LIVE-A89F4C",
  "action": "BLOCK",
  "reasons": [
    "Claimed merchant 'BESCOM Electricity Board' does not match actual account holder 'Rajesh Kumar Private Account'.",
    "Payment destination URL domain exhibits security risk signals.",
    "Urgent utility disconnection threat detected in payment message."
  ],
  "customer_explanation": {
    "what_happened": "Payment to 'BESCOM Electricity Board' could not be completed.",
    "why": "The payment destination could not be verified for 'BESCOM Electricity Board'.",
    "what_action_was_taken": "BLOCK",
    "what_should_happen_next": "Do not attempt to resend funds. Contact the service provider directly via their official application or website.",
    "how_to_prevent_recurrence": "Always initiate utility and bill payments directly inside official provider mobile apps or verified portals."
  },
  "ops_explanation": {
    "what_happened": "High-risk payment of Rs 8,742.00 BLOCKED for claimed merchant 'BESCOM Electricity Board'.",
    "why": "Severe evidence combination detected: Identity mismatch, Phishing URL, Disconnection threat.",
    "what_action_was_taken": "BLOCK",
    "what_should_happen_next": "Place destination account and domain under security block.",
    "how_to_prevent_recurrence": "Update domain blocklist."
  },
  "evidence_bundle": {
    "bundle_id": "BDL-52E9B1",
    "overall_severity": "high",
    "evidence_count": 3,
    "has_critical_indicators": true
  },
  "recommended_next_step": "Do not proceed with this payment. Verify payee details through official public channels.",
  "prevention_recommendation": "Place recipient account and payment domain under enhanced security monitoring.",
  "audit_trail": {
    "timestamp": "2026-08-21T12:28:40.123456+00:00",
    "policy_rule_triggered": "RULE_BLOCK_MALICIOUS_DESTINATION_AND_IDENTITY_MISMATCH",
    "overall_severity": "high"
  }
}
```
