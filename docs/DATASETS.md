# SecureFlow: Dataset & Ingestion Documentation

## 1. Public Data Sources

SecureFlow is trained on public datasets acquired directly from academic and machine learning repositories:

1. **UCI SMS Spam Collection**:
   * **Source**: UCI ML Repository / Kaggle SMS Spam Collection
   * **Size**: 5,574 labeled messages
   * **Classes**: 4,825 legitimate (`ham`), 747 scam (`spam`)
   * **Usage**: Training Scam-Context NLP Engine vectorizer and Naive Bayes classifier.

2. **PhiUSIIL Phishing URL Dataset**:
   * **Source**: UCI ML Repository (Prasad & Chandra, 2024)
   * **Size**: 235,795 labeled web URLs
   * **Usage**: Training URL Intelligence Engine feature extractors and Gradient Boosting classifier.

---

## 2. Synthetic Database Schema

The synthetic environment is initialized reproducibly (`SEED = 42`) in SQLite (`data/secureflow.db`) with 7 relational entities:

| Entity | Primary Key | Total Records | Key Fields |
| :--- | :--- | :--- | :--- |
| **Customer** | `customer_id` | 50 | `normal_avg_amount`, `normal_std_amount`, `normal_merchants` |
| **Merchant** | `merchant_id` | 5 | `legal_name`, `brand_name`, `verified_domain`, `status` |
| **Recipient** | `recipient_id` | 6 | `display_name`, `verified_identity`, `linked_merchant_id`, `account_age_days` |
| **Scenario** | `scenario_id` | 10 | `scenario_name`, `scenario_type`, `expected_action` |
| **Transaction** | `transaction_id` | 611 | `amount`, `channel`, `status`, `timestamp` |
| **PaymentRequest** | `request_id` | 611 | `claimed_merchant`, `message`, `url`, `source_channel` |
| **ProtectionEvent**| `event_id` | 611 | `action`, `evidence`, `explanation`, `timestamp` |

---

## 3. Preprocessing & Holdout Split

* **Train / Validation / Test Split**: 70% train, 15% validation, 15% test.
* **Scenario Holdout**: Held-out attack scenarios (`SCN-002` through `SCN-006`, `SCN-009`, `SCN-010`) were excluded during model fitting to evaluate zero-day attack generalization.
