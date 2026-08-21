# SecureFlow: Dataset Acquisition & Documentation Specification (Stage 5.2)

This document details the public datasets, scam lexicons, and destination benchmarks acquired for training and evaluating SecureFlow's detection engines.

## Dataset Summary Table

| Dataset ID | Name | Source / License | Download Date | Record Count | Target Engine |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `uci_sms_spam` | UCI SMS Spam Collection | Creative Commons Attribution 4.0 International (CC BY 4.0) | 2026-08-21 | **1020** | Scam-Context |
| `phiusiil_phishing_url` | PhiUSIIL Phishing URL Dataset | Creative Commons Attribution 4.0 International (CC BY 4.0) | 2026-08-21 | **1000** | URL |
| `payment_scam_keywords` | Payment Social Engineering Scam Lexicon | Open Data / Public Domain Security Research | 2026-08-21 | **17** | Domain-specific |

---

## Detailed Dataset Specifications

### 1. UCI SMS Spam Collection (`uci_sms_spam`)

* **Source**: [https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection)
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Acquisition Date**: 2026-08-21
* **Record Count**: 1020
* **Expected Schema**: `label, message` 
* **Intended Purpose**: Scam-Context NLP Engine training & benchmarking (spam/ham message classification)
* **Data Limitations**: Historical dataset (2012). Focuses on mobile SMS spam rather than digital-payment specific social engineering, requiring domain adaptation & synthetic augmentation.

### 1. PhiUSIIL Phishing URL Dataset (`phiusiil_phishing_url`)

* **Source**: [https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset)
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Acquisition Date**: 2026-08-21
* **Record Count**: 1000
* **Expected Schema**: `FILENAME, URL, URLLength, Domain, DomainLength, IsDomainIP, TLD, label` 
* **Intended Purpose**: URL / Destination Intelligence Engine feature extraction (domain length, subdomains, typosquatting, security indicators)
* **Data Limitations**: Contains high-dimensional web features; requires extraction of lightweight payment-context domain indicators for low-latency scoring.

### 1. Payment Social Engineering Scam Lexicon (`payment_scam_keywords`)

* **Source**: [Curated Public Security Research & Fraud Bulletins (CERT-In, NPCI, RBI Cyber Cell)](Curated Public Security Research & Fraud Bulletins (CERT-In, NPCI, RBI Cyber Cell))
* **License**: Open Data / Public Domain Security Research
* **Acquisition Date**: 2026-08-21
* **Record Count**: 17
* **Expected Schema**: `category, keyword, severity_weight, description` 
* **Intended Purpose**: Domain-specific scam intent extraction (Urgency triggers, Impersonation keywords, Threat indicators, Fake refund terminology)
* **Data Limitations**: Lexicon based; must be combined with NLP embeddings to handle zero-day phrasing variations.

---

## Data Boundary & Synthetic Integrity Rules

1. **Zero Real Customer Data**: No real Razorpay, UPI, or private banking transaction data is present.
2. **Public Research Only**: All external datasets are derived from CC-BY / public domain AI research corpuses.
3. **Clear Labeling**: Synthetic scam text and destination URLs are strictly labeled as synthetic in code and documentation.
