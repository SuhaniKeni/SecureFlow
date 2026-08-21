import os
import json
import pandas as pd
from secureflow.db.database import SessionLocal
from secureflow.preprocessing.url_pipeline import process_url_dataset
from secureflow.preprocessing.nlp_pipeline import process_nlp_dataset
from secureflow.preprocessing.behavior_pipeline import compute_behavior_features
from secureflow.preprocessing.merchant_pipeline import compute_merchant_features
from secureflow.preprocessing.scenario_split import split_by_scenario_holdout, HOLDOUT_TEST_SCENARIOS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DOCS_FEAT_DIR = os.path.join(BASE_DIR, "docs", "features")

os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
os.makedirs(DOCS_FEAT_DIR, exist_ok=True)

def main():
    print("=== SecureFlow Preprocessing Pipelines (Stage 5.4) ===")
    
    # 1. URL Pipeline Preprocessing
    url_csv = os.path.join(DATA_PROCESSED_DIR, "phiusiil_phishing_url_clean.csv")
    if not os.path.exists(url_csv):
        url_csv = os.path.join(DATA_RAW_DIR, "phishing_url_dataset.csv")

    (X_url_tr, y_url_tr), (X_url_val, y_url_val), (X_url_te, y_url_te), url_cfg = process_url_dataset(url_csv)
    url_cfg_path = os.path.join(DATA_PROCESSED_DIR, "url_pipeline_config.json")
    with open(url_cfg_path, "w") as f:
        json.dump(url_cfg, f, indent=2)
    print(f"[+] URL Pipeline: Train={len(X_url_tr)}, Val={len(X_url_val)}, Test={len(X_url_te)} | Saved config: {url_cfg_path}")

    # 2. NLP Scam Text Pipeline Preprocessing
    nlp_csv = os.path.join(DATA_PROCESSED_DIR, "uci_sms_spam_clean.csv")
    if not os.path.exists(nlp_csv):
        nlp_csv = os.path.join(DATA_RAW_DIR, "sms_spam_collection.csv")

    (X_nlp_tr, y_nlp_tr), (X_nlp_val, y_nlp_val), (X_nlp_te, y_nlp_te), nlp_cfg = process_nlp_dataset(nlp_csv)
    nlp_cfg_path = os.path.join(DATA_PROCESSED_DIR, "nlp_pipeline_config.json")
    with open(nlp_cfg_path, "w") as f:
        json.dump(nlp_cfg, f, indent=2)
    print(f"[+] NLP Pipeline: Train={X_nlp_tr.shape[0]}, Val={X_nlp_val.shape[0]}, Test={X_nlp_te.shape[0]} | Saved config: {nlp_cfg_path}")

    # 3. Behavior & Merchant Pipeline Preprocessing
    session = SessionLocal()
    try:
        df_behavior = compute_behavior_features(session)
        df_merchant = compute_merchant_features(session)

        # Merge behavior + merchant features on transaction_id
        df_combined = pd.merge(df_behavior, df_merchant, on="transaction_id", how="inner")
        
        # Save processed baseline dataset
        combined_path = os.path.join(DATA_PROCESSED_DIR, "payment_behavior_merchant_processed.csv")
        df_combined.to_csv(combined_path, index=False)

        # Apply Scenario Holdout Split
        train_val_df, test_holdout_df = split_by_scenario_holdout(df_combined)
        
        train_val_path = os.path.join(DATA_PROCESSED_DIR, "payment_train_val.csv")
        holdout_path = os.path.join(DATA_PROCESSED_DIR, "payment_scenario_holdout_test.csv")
        train_val_df.to_csv(train_val_path, index=False)
        test_holdout_df.to_csv(holdout_path, index=False)

        print(f"[+] Behavior & Merchant Pipeline: Total={len(df_combined)} txns")
        print(f"    - Train/Val Split: {len(train_val_df)} txns")
        print(f"    - Scenario Holdout Test Set: {len(test_holdout_df)} txns (Held-out Scenarios: {HOLDOUT_TEST_SCENARIOS})")
        print(f"    - Preserved Legitimate Unusual Txns: {df_combined['is_legitimate_unusual'].sum()} txns")

    finally:
        session.close()

    # 4. Generate Feature Documentation
    doc_path = os.path.join(DOCS_FEAT_DIR, "FEATURE_DOCUMENTATION.md")
    content = "# SecureFlow Feature & Preprocessing Documentation (Stage 5.4)\n\n"
    content += "This document details the extracted features, preprocessing transformations, data leakage prevention rules, and scenario holdout split configurations.\n\n"
    content += "## 1. URL & Destination Features (`url_pipeline`)\n\n"
    content += f"* **Features**: `{', '.join(url_cfg['feature_names'])}` \n"
    content += "* **Scaling**: `StandardScaler` fitted **strictly on train split** (70% train, 15% val, 15% test).\n"
    content += "* **Data Leakage Safeguard**: Validation and test sets are transformed using train fitted mean and scale parameters.\n\n"
    content += "## 2. Scam NLP Text Features (`nlp_pipeline`)\n\n"
    content += f"* **Vectorization**: TF-IDF (`max_features=500`, unigrams & bigrams) fitted **strictly on train split**.\n"
    content += f"* **Domain Heuristics**: `{', '.join(nlp_cfg['heuristic_features'])}` (Urgency count, Impersonation count, Threat count, URL flag, message length).\n\n"
    content += "## 3. Customer Behavior Features (`behavior_pipeline`)\n\n"
    content += "* **Key Features**: `amount_zscore`, `is_unusual_amount`, `hour_anomaly`, `velocity_1h`, `velocity_24h`, `is_legitimate_unusual`.\n"
    content += "* **Anti-Overfitting Safeguard**: **Legitimate Unusual Transactions** (e.g. SCN-007 high-value purchases) are explicitly preserved as `LEGITIMATE` so models do not learn the naive false-positive heuristic 'unusual amount = fraud'.\n\n"
    content += "## 4. Merchant Identity Features (`merchant_pipeline`)\n\n"
    content += "* **Key Features**: `identity_similarity_score`, `is_identity_mismatch`, `recipient_account_age_days`, `is_new_recipient`, `is_merchant_verified`.\n\n"
    content += "## 5. Scenario Holdout Split Specification\n\n"
    content += f"* **Held-out Attack Scenarios**: `{', '.join(HOLDOUT_TEST_SCENARIOS)}` \n"
    content += "* **Purpose**: Ensures that test set evaluation measures zero-day generalization against unseen scam tactics.\n"

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"[+] Saved feature documentation: {doc_path}")

if __name__ == "__main__":
    main()
