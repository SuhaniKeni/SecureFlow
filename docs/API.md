# SecureFlow: REST API Specification

FastAPI REST API specification for SecureFlow Adaptive Payment Protection.

---

## Endpoints Summary

| Method | Endpoint | Request Schema | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | System health check |
| `POST` | `/payments/analyze` | `PaymentAnalysisRequest` | Core payment security evaluation endpoint |
| `POST` | `/payments/simulate` | `PaymentSimulationRequest` | Sandbox checkout UI simulation endpoint |
| `GET` | `/payments/{id}` | None | Retrieves transaction details by ID |
| `GET` | `/protection-events` | Query params: `action`, `limit` | Lists historical audit events for Risk Ops |
| `GET` | `/protection-events/{id}`| None | Retrieves single forensic event record |
| `GET` | `/merchants/{id}` | None | Retrieves merchant profile & domain verification |
| `GET` | `/customers/{id}/history`| None | Retrieves customer profile & transaction history |
| `POST` | `/scenarios/run` | `ScenarioRunRequest` | Executes benchmark attack scenario by ID |

---

## Security Validation Rule

Any request containing sensitive credentials (`upi_pin`, `card_number`, `cvv`, `password`) returns **HTTP 400/422 Bad Request**:

```json
{
  "detail": "Security Violation: Sensitive payment credential field 'upi_pin' is prohibited."
}
```
