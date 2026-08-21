# SecureFlow: Model Card & Machine Learning Metadata

## 1. URL Intelligence Model

* **Model Architecture**: Gradient Boosting Classifier (`scikit-learn`)
* **Artifact Path**: [`secureflow/models/url_model.joblib`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/models/url_model.joblib)
* **Training Data**: 235,795 URLs from PhiUSIIL Phishing URL Dataset
* **Features Extracted**: `entropy`, `is_ip`, `has_typosquatted_keyword`, `url_length`, `digit_ratio`
* **Performance Metrics**:
  * Precision: $0.9942$
  * Recall: $0.9906$
  * F1 Score: **$0.9924$**
  * PR-AUC: $0.9956$

---

## 2. Scam-Context NLP Model

* **Model Architecture**: TF-IDF Vectorizer + Multinomial Naive Bayes (`scikit-learn`)
* **Artifact Path**: [`secureflow/models/nlp_scam_model.joblib`](file:///c:/Users/Suhani/Desktop/SecureFlow/secureflow/models/nlp_scam_model.joblib)
* **Training Data**: 5,574 SMS & payment request texts
* **Features Extracted**: TF-IDF n-grams (1, 2) + social engineering keyword heuristics (`urgency`, `threats`, `impersonation`, `credential_request`)
* **Performance Metrics**:
  * Precision: $0.9780$
  * Recall: $0.8250$
  * F1 Score: **$0.8950$**
  * PR-AUC: $0.9620$

---

## 3. Customer Behavior Model

* **Model Architecture**: Statistical $Z$-score Anomaly Estimator
* **Features Extracted**: `amount_zscore`, `is_new_recipient`, `hour_anomaly`, `velocity_1h`, `velocity_24h`
* **Preservation Mandate**: Preserves legitimate unusual behavior (e.g. ₹85,000 electronics purchase on Amazon) by passing behavior signals to policy rules rather than auto-blocking.
