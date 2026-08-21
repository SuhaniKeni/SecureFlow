# SecureFlow Data Layer Documentation (Stage 5.2)

This directory contains public datasets and metadata registered for SecureFlow.

## Directory Structure

```text
data/
├── raw/         # Unmodified downloaded raw dataset files
├── processed/   # Cleaned, standardized CSVs ready for feature extraction
├── external/    # Original archived zip/txt datasets from external sources
├── metadata/    # Dataset registry JSON metadata
├── dataset_registry.json
└── README.md    # Data layer documentation
```

## Verified Public Datasets Registry

### UCI SMS Spam Collection (`uci_sms_spam`)

- **Source URL**: [https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Download Date**: 2026-08-21
- **Actual File Size**: 486,480 bytes
- **Verified Record Count**: 5,574 rows
- **Target**: `label (ham/spam) / is_spam (0/1)`
- **Features**: `message`
- **Intended Use**: Scam-Context NLP Engine training & benchmarking (spam vs ham text baseline classification)
- **Limitations**: Collected in 2012; mobile SMS context. Does not include UPI/payment app specific terms, requiring domain-specific lexicon integration.

### PhiUSIIL Phishing URL Dataset (`phiusiil_phishing_url`)

- **Source URL**: [https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Download Date**: 2026-08-21
- **Actual File Size**: 56,854,345 bytes
- **Verified Record Count**: 235,795 rows
- **Target**: `label (0=legitimate, 1=phishing)`
- **Features**: `FILENAME, URL, URLLength, Domain, DomainLength, IsDomainIP, TLD, URLSimilarityIndex`
- **Intended Use**: URL / Destination Intelligence Engine feature extraction (lexical, domain, and security indicators)
- **Limitations**: High-dimensional dataset (54 features); light extraction required for low-latency payment gateway scoring.

---
## Security & Data Privacy Enforcement
- **No Real Customer Data**: Zero real financial, UPI, or personal customer data is present.
- **No Payment Data**: Payment behavior data is NOT created in Stage 5.2 (strictly reserved for Stage 5.3 synthetic database).
- **No Trained Models**: No ML models are trained in Stage 5.2.
