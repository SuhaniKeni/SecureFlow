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

def test_eval_dataset_leakage_and_diversity_checks():
    """Dataset quality check: verifies non-trivial distributions and zero input payload leakage."""
    with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    # 1. Input payload metadata leakage check
    for s in scenarios:
        inp = s["input"]
        assert "expected_action" not in inp, "Data Leakage: expected_action present in input payload"
        assert "category" not in inp, "Data Leakage: category present in input payload"
        assert "scenario_id" not in inp, "Data Leakage: scenario_id present in input payload"

    # 2. Text note and URL diversity checks
    notes = set(s["input"]["payment_note"] for s in scenarios)
    urls = set(s["input"]["url"] for s in scenarios)

    assert len(urls) >= 15, f"URL diversity check failed: Only {len(urls)} unique URLs"
    assert len(notes) >= 300, f"Note diversity check failed: Only {len(notes)} unique notes"

    # 3. Amount distribution overlap check (Legitimate vs Attack amounts must overlap)
    legit_amts = [s["input"]["amount"] for s in scenarios if "Legitimate" in s["category"] or s["category"] == "A_Normal_Legitimate"]
    attack_amts = [s["input"]["amount"] for s in scenarios if "Attack" in s["category"] or "Impersonation" in s["category"] or "Destination" in s["category"]]

    assert min(legit_amts) < max(attack_amts), "Amount distribution error: Legitimate and Attack amounts do not overlap"
    assert min(attack_amts) < max(legit_amts), "Amount distribution error: Attack amounts artificially separated from Legitimate"
