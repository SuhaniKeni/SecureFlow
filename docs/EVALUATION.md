# SecureFlow: Comprehensive Evaluation Framework & Benchmark Results

## 1. Experimental Setup

The evaluation framework compares **SecureFlow** against a **Legacy Baseline System** (amount threshold > ₹5,000 & simple keyword matching) across held-out benchmark scenarios.

* **Reproducible Script**: [`scripts/run_evaluation_framework.py`](file:///c:/Users/Suhani/Desktop/SecureFlow/scripts/run_evaluation_framework.py)
* **JSON Metrics**: [`docs/evaluation/EVALUATION_METRICS.json`](file:///c:/Users/Suhani/Desktop/SecureFlow/docs/evaluation/EVALUATION_METRICS.json)
* **CSV Metrics**: [`docs/evaluation/EVALUATION_METRICS.csv`](file:///c:/Users/Suhani/Desktop/SecureFlow/docs/evaluation/EVALUATION_METRICS.csv)

---

## 2. Experimental Results Summary

| Metric | Legacy Baseline Engine | SecureFlow Adaptive Engine | Delta Improvement |
| :--- | :--- | :--- | :--- |
| **Precision** | `0.8571` | **`1.0000`** | **`+0.1429`** |
| **Recall** | `0.8571` | **`1.0000`** | **`+0.1429`** |
| **F1 Score** | `0.8571` | **`1.0000`** | **`+0.1429`** |
| **Scam Protection Rate** | `0.8571` | **`1.0000`** | **`+0.1429`** (100% attack detection) |
| **Legitimate Preservation Rate** | `0.6667` | **`1.0000`** | **`+0.3333`** |
| **Unnecessary Blocking Rate** | `0.3333` | **`0.0000`** | **`-0.3333`** (Eliminated false blocks) |
| **Action Selection Accuracy** | `0.6000` | **`1.0000`** | **`+0.4000`** (100% action match) |
| **Mean Execution Latency** | `0.02 ms` | **`1.15 ms`** | Sub-2ms processing overhead |

---

## 3. Key Findings

1. **Protection Optimization**: SecureFlow correctly blocks 100% of social engineering scams, phishing links, and merchant identity mismatches.
2. **Friction Reduction**: By routing unusual legitimate transactions (e.g. ₹85,000 Amazon laptop purchase) to **`VERIFY`** instead of auto-blocking, SecureFlow reduces unnecessary customer blocking to **0.0%**.
