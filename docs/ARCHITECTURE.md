# SecureFlow: Technical Architecture Specification

## 1. System Overview

SecureFlow is an adaptive payment security architecture designed to operate transparently during checkout. It processes transaction payloads through four specialized detection engines, aggregates evidence into a unified schema, and executes deterministic policy rules.

```text
                                 [ PAYMENT REQUEST ]
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
[ URL INTEL ENGINE ]             [ SCAM NLP ENGINE ]              [ BEHAVIOR ENGINE ]
  Lexical URL Model                TF-IDF Naive Bayes                Z-Score & Velocity
        │                                 │                                 │
        └─────────────────────────────────┼─────────────────────────────────┘
                                          ▼
                             [ MERCHANT CONSISTENCY ENGINE ]
                               Multi-Factor Identity Match
                                          │
                                          ▼
                             [ EVIDENCE AGGREGATION LAYER ]
                                Unified EvidenceBundle
                                          │
                                          ▼
                            [ PROTECTION DECISION ENGINE ]
                             Auditable Deterministic Code
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
            [ ACTION SELECTION ]                      [ EXPLANATION ENGINE ]
         ALLOW / VERIFY / HOLD / BLOCK              Dual Customer / Ops Notices
```

## 2. Component Specifications

### 2.1 URL Intelligence Engine
* **File**: [`secureflow/engines/url_intel_engine.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/engines/url_intel_engine.py)
* **Model**: Gradient Boosting Classifier fit on lexical features (`entropy`, `is_ip`, `has_typosquatted_keyword`, `url_length`).
* **Output**: Structured evidence dictionary containing `signal`, `risk_score`, `severity`, and lexical metrics.

### 2.2 Scam-Context NLP Engine
* **File**: [`secureflow/engines/scam_nlp_engine.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/engines/scam_nlp_engine.py)
* **Model**: TF-IDF Vectorizer + Multinomial Naive Bayes extracting threat, urgency, and financial pressure heuristics.
* **Output**: Structured evidence dictionary containing social engineering risk indicators.

### 2.3 Customer Behavior Engine
* **File**: [`secureflow/engines/behavior_engine.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/engines/behavior_engine.py)
* **Logic**: $Z$-score statistical deviation calculation against customer historical transaction distributions and 1-hour/24-hour velocity trackers.

### 2.4 Merchant Consistency Engine
* **File**: [`secureflow/engines/merchant_engine.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/engines/merchant_engine.py)
* **Logic**: Multi-factor entity matching between claimed merchant string, registered corporate entity, verified domain, and recipient account age (< 30 days).

### 2.5 Evidence Aggregator & Policy Engine
* **Files**: [`secureflow/aggregation/evidence_aggregator.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/aggregation/evidence_aggregator.py), [`secureflow/policy/decision_engine.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/policy/decision_engine.py)
* **Logic**: Fuses 4 evidence vectors into `EvidenceBundle` and evaluates explicit Python code policy rules returning actions (`ALLOW`, `VERIFY`, `HOLD`, `BLOCK`).
