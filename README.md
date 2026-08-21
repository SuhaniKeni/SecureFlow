# SecureFlow: Adaptive AI Security Layer for Digital Payments

> **Submission for Razorpay AI Builder Internship 2026 — AI Risk Manager Track**  
> *Notice: SecureFlow is a functional research prototype operating on local synthetic database environments. It does NOT use real customer credentials, live banking rails, or real Razorpay production integration.*

---

## 1. Problem
Digital payments in India (UPI, cards, net banking) processing billions of monthly transactions face an escalating wave of social engineering scams—such as fake electricity disconnection threats, impersonation of courier customs duty, fake bank security alerts, and customer care refund bait.

## 2. Why It Matters
Traditional payment risk systems rely heavily on post-fraud chargebacks or simplistic transaction amount limits. When victims are manipulated into authorizing payments themselves, legacy systems struggle because the transaction appears authorized by the user.

## 3. Existing Ecosystem
Current risk solutions typically evaluate risk in isolation—checking either basic device fingerprints or static transaction limits. They lack holistic context fusion across message text intent, destination URL legitimacy, and payee identity consistency.

## 4. Our Specific Gap
Existing security solutions suffer from a binary dilemma: either they let scams pass unnoticed, or they aggressively block legitimate high-value payments (creating severe customer friction). Moreover, LLM-based risk tools often introduce non-deterministic decision risks or latency bottlenecks.

## 5. SecureFlow Solution
SecureFlow introduces an **Adaptive, Invisible Security Layer** that enforces **DETECT → UNDERSTAND → PROTECT → EXPLAIN**:
* **4 Detection Engines**: URL Intelligence, Scam NLP Intent, Customer Behavior Baselines, and Merchant Consistency.
* **Deterministic Policy Engine**: Code-driven, auditable policy rules that select strictly between `ALLOW`, `VERIFY`, `HOLD`, and `BLOCK`.
* **Security Principle**: *Security should feel invisible.*

---

## Data & Methodological Categorization

| Category | Description & Boundary |
| :--- | :--- |
| **VERIFIED FACTS** | 78/78 passing automated test cases; 100% benchmark scenario action match; sub-2ms execution latency; zero credential exposure. |
| **PROTOTYPE ASSUMPTIONS** | Local SQLite database simulation; synthetic customer transaction distributions; offline ML model scoring. |
| **SYNTHETIC DATA** | Synthetic environment with 50 customers, 5 merchants, 6 recipients, 10 scenarios, and 611 seeded transactions. |
| **EXPERIMENTAL RESULTS** | Held-out evaluation metrics ($F_1 = 1.0000$, Scam Protection Rate = $100\%$, Unnecessary Block Rate = $0.0\%$). |

---

## 6. System Architecture

```text
Payment Request (Amount, Payee, Message, URL)
   │
   ├──► 1. URL Intelligence Engine (Gradient Boosting Classifier)
   ├──► 2. Scam-Context NLP Engine (TF-IDF + Naive Bayes)
   ├──► 3. Customer Behavior Engine (Statistical Z-Scores & Velocity)
   └──► 4. Merchant Consistency Engine (Identity & Domain Match)
           │
           ▼
   Evidence Aggregator (Normalized EvidenceBundle)
           │
           ▼
   Protection Decision Engine (Deterministic Code Policy Rules)
           │
           ├──► Action: ALLOW | VERIFY | HOLD | BLOCK
           │
   Dual Explanation Engine (Factual Grounding)
           │
           ├──► Customer UX Notice (Non-alarming, zero jargon)
           └──► Risk Ops Forensic Summary (5-Question Hierarchy)
```

---

## 7. AI & Machine Learning Techniques
* **URL Intelligence**: Lexical feature extractor (entropy, domain length, IP presence, typosquatting) paired with a trained **Gradient Boosting Classifier** ($F_1 = 0.9924$).
* **Scam-Context NLP**: TF-IDF vectorizer + **Multinomial Naive Bayes** model ($F_1 = 0.8950$) extracting social engineering heuristics (urgency, threats, credential requests).
* **Customer Behavior**: Non-ML statistical $Z$-score anomaly detection comparing transaction amounts against historical customer means while preserving legitimate unusual behavior.
* **Merchant Consistency**: Multi-factor identity alignment comparing claimed payee names against verified corporate domain registrations and account age.

## 8. Data Sources
* **Public Datasets**: UCI SMS Spam Collection (5,574 rows) & PhiUSIIL Phishing URL Dataset (235,795 rows).
* **Synthetic Payment DB**: Generated using `SEED = 42` in SQLite (`data/secureflow.db`).

## 9. Synthetic Data Limitations
* Does not reflect live banking network latency or real-world UPI traffic volumes.
* Customer behavior distributions are generated via Gaussian distributions around synthetic baselines.

## 10. Protection Decision Engine
* **Strict Rule**: LLMs are NEVER permitted to make or override financial protection decisions.
* **Actions**: `ALLOW`, `VERIFY` (2FA prompt), `HOLD` (temporary review), `BLOCK` (destination unverified).

## 11. Evaluation Framework
Compares SecureFlow against a **Legacy Baseline** (naive amount > ₹5,000 threshold & simple string matching).

## 12. Benchmark Results
* **Precision**: $1.0000$ vs Baseline $0.8571$
* **Scam Protection Rate**: $100\%$ vs Baseline $85.7\%$
* **Unnecessary Blocking Rate**: $0.0\%$ vs Baseline $33.3\%$
* **Mean Latency**: $1.15\text{ ms}$ inline processing overhead.

## 13. Security Boundaries & Privacy Guardrails
* **Zero Real Payment Credentials**: Inputs containing `upi_pin`, `card_number`, `cvv`, or `password` are rejected instantly with HTTP 400/422.
* **No Raw ML Scores to Customers**: Customers see clean, non-alarming notices; raw probabilities are strictly hidden.

## 14. How to Run Locally

### Quick Start (Python Environment):
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run test suite
python -m pytest tests/

# 3. Run end-to-end verification
python scripts/run_e2e_verification.py

# 4. Start FastAPI server
uvicorn secureflow.api.main:app --reload --port 8000
```

### Docker Quick Start:
```bash
cp .env.example .env
docker compose up --build -d
```

## 15. Demo Scenarios
1. **Normal Electricity Bill**: ₹1,450 to BESCOM Official → **`ALLOW`**
2. **Fake Disconnection Scam**: ₹8,742 to `elect-pay-bill.top` → **`BLOCK`**
3. **High-Value Purchase**: ₹85,000 Laptop on Amazon Pay → **`VERIFY`**

## 16. Future Improvements
* Integration of graph database (Neo4j) for mule account network detection.
* On-device privacy-preserving NLP intent scoring for mobile checkout SDKs.
