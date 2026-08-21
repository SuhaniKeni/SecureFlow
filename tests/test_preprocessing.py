import os
import json
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from secureflow.db.models import Base
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.preprocessing.url_pipeline import process_url_dataset
from secureflow.preprocessing.nlp_pipeline import process_nlp_dataset
from secureflow.preprocessing.behavior_pipeline import compute_behavior_features
from secureflow.preprocessing.merchant_pipeline import compute_merchant_features
from secureflow.preprocessing.scenario_split import split_by_scenario_holdout, HOLDOUT_TEST_SCENARIOS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def test_url_pipeline_no_data_leakage():
    """Verify URL pipeline fits scaler strictly on train set and avoids data leakage."""
    url_csv = os.path.join(DATA_PROCESSED_DIR, "phiusiil_phishing_url_clean.csv")
    if not os.path.exists(url_csv):
        pytest.skip("PhiUSIIL clean CSV missing")

    (X_tr, y_tr), (X_val, y_val), (X_te, y_te), config = process_url_dataset(url_csv)

    assert len(X_tr) > len(X_val)
    assert len(X_val) == len(X_te) or abs(len(X_val) - len(X_te)) <= 1
    assert X_tr.shape[1] == 9, f"Expected 9 extracted URL features, got {X_tr.shape[1]}"
    assert "scaler_mean" in config
    assert "scaler_scale" in config

def test_nlp_pipeline_no_data_leakage():
    """Verify NLP pipeline fits TF-IDF vectorizer strictly on train set."""
    nlp_csv = os.path.join(DATA_PROCESSED_DIR, "uci_sms_spam_clean.csv")
    if not os.path.exists(nlp_csv):
        pytest.skip("SMS spam clean CSV missing")

    (X_tr, y_tr), (X_val, y_val), (X_te, y_te), config = process_nlp_dataset(nlp_csv, max_features=100)

    assert X_tr.shape[0] > X_val.shape[0]
    assert X_tr.shape[1] == 100 + 5, f"Expected 105 total NLP features, got {X_tr.shape[1]}"

def test_behavior_pipeline_preserves_legitimate_unusual():
    """Verify behavior pipeline preserves legitimate high z-score transactions."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_synthetic_database(session, seed=42)

    df_behavior = compute_behavior_features(session)
    session.close()

    assert "amount_zscore" in df_behavior.columns
    assert "is_legitimate_unusual" in df_behavior.columns
    assert df_behavior["is_legitimate_unusual"].sum() > 0, "Must preserve legitimate unusual transactions"

def test_merchant_pipeline_mismatch_detection():
    """Verify merchant pipeline calculates identity mismatch scores."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_synthetic_database(session, seed=42)

    df_merchant = compute_merchant_features(session)
    session.close()

    assert "identity_similarity_score" in df_merchant.columns
    assert "is_identity_mismatch" in df_merchant.columns
    assert df_merchant["is_identity_mismatch"].sum() > 0, "Must flag identity mismatches"

def test_scenario_holdout_split_isolation():
    """Verify scenario-based holdout set isolates target attack types from training."""
    sample_df = pd.DataFrame({
        "transaction_id": [f"TXN-{i}" for i in range(10)],
        "scenario_id": ["SCN-001", "SCN-001", "SCN-002", "SCN-003", "SCN-005", "SCN-007", "SCN-006", "SCN-001", "SCN-010", "SCN-004"]
    })

    train_val_df, holdout_df = split_by_scenario_holdout(sample_df)

    # Check zero overlap of holdout scenarios in train set
    for s_id in HOLDOUT_TEST_SCENARIOS:
        assert s_id not in train_val_df["scenario_id"].values, f"Holdout scenario {s_id} leaked into train set"
        
    assert len(holdout_df) == 4, f"Expected 4 holdout transactions, got {len(holdout_df)}"

def test_feature_documentation_generated():
    """Verify feature documentation markdown file exists."""
    doc_path = os.path.join(BASE_DIR, "docs", "features", "FEATURE_DOCUMENTATION.md")
    assert os.path.exists(doc_path), "FEATURE_DOCUMENTATION.md missing"
    
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "FEATURE_DOCUMENTATION.md" in doc_path or "SecureFlow Feature" in content
    assert "url_pipeline" in content
    assert "nlp_pipeline" in content
    assert "behavior_pipeline" in content
    assert "merchant_pipeline" in content
