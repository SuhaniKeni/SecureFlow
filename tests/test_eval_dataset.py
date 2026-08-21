import os
import json
import pytest
from secureflow.scenarios.eval_dataset_generator import generate_expanded_evaluation_dataset, EVAL_DATASET_PATH

def test_generate_expanded_evaluation_dataset():
    data = generate_expanded_evaluation_dataset(seed=42, target_count=400)
    assert len(data) == 400, f"Expected 400 scenarios, found {len(data)}"
    assert os.path.exists(EVAL_DATASET_PATH)

def test_eval_dataset_categories_and_uniqueness():
    with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as f:
        scenarios = json.load(f)
    
    assert len(scenarios) == 400
    ids = set(s["scenario_id"] for s in scenarios)
    assert len(ids) == 400, "Duplicate scenario IDs detected"

    categories = set(s["category"] for s in scenarios)
    expected_categories = {
        "A_Normal_Legitimate", "B_Legitimate_Unusual", "C_Social_Engineering_Attack",
        "D_Merchant_Impersonation", "E_Suspicious_Destination", "F_Recipient_Anomalies",
        "G_Conflicting_Signals", "H_Ambiguous_Cases"
    }
    assert expected_categories.issubset(categories), f"Missing categories: {expected_categories - categories}"
