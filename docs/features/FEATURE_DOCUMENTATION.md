# SecureFlow Feature & Preprocessing Documentation (Stage 5.4)

This document details the extracted features, preprocessing transformations, data leakage prevention rules, and scenario holdout split configurations.

## 1. URL & Destination Features (`url_pipeline`)

* **Features**: `url_length, domain_length, num_subdomains, is_ip, has_https, num_hyphens, num_at_symbol, num_queries, has_typosquatted_keyword` 
* **Scaling**: `StandardScaler` fitted **strictly on train split** (70% train, 15% val, 15% test).
* **Data Leakage Safeguard**: Validation and test sets are transformed using train fitted mean and scale parameters.

## 2. Scam NLP Text Features (`nlp_pipeline`)

* **Vectorization**: TF-IDF (`max_features=500`, unigrams & bigrams) fitted **strictly on train split**.
* **Domain Heuristics**: `urgency_count, impersonation_count, threat_count, has_url, msg_len` (Urgency count, Impersonation count, Threat count, URL flag, message length).

## 3. Customer Behavior Features (`behavior_pipeline`)

* **Key Features**: `amount_zscore`, `is_unusual_amount`, `hour_anomaly`, `velocity_1h`, `velocity_24h`, `is_legitimate_unusual`.
* **Anti-Overfitting Safeguard**: **Legitimate Unusual Transactions** (e.g. SCN-007 high-value purchases) are explicitly preserved as `LEGITIMATE` so models do not learn the naive false-positive heuristic 'unusual amount = fraud'.

## 4. Merchant Identity Features (`merchant_pipeline`)

* **Key Features**: `identity_similarity_score`, `is_identity_mismatch`, `recipient_account_age_days`, `is_new_recipient`, `is_merchant_verified`.

## 5. Scenario Holdout Split Specification

* **Held-out Attack Scenarios**: `SCN-002, SCN-005, SCN-006, SCN-010` 
* **Purpose**: Ensures that test set evaluation measures zero-day generalization against unseen scam tactics.
