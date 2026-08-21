import os
import json
import pytest
from scripts.run_unseen_generalization_eval import run_unseen_evaluation, UNSEEN_DATASET_PATH

def test_unseen_eval_dataset_integrity():
    assert os.path.exists(UNSEEN_DATASET_PATH)
    with open(UNSEEN_DATASET_PATH, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    assert len(scenarios) == 150, f"Expected 150 unseen scenarios, found {len(scenarios)}"
    for s in scenarios:
        assert "expected_action" not in s["input"], "Metadata leakage: expected_action in input"
        assert "category" not in s["input"], "Metadata leakage: category in input"

def test_unseen_generalization_evaluation_metrics():
    metrics = run_unseen_evaluation()
    assert metrics["total_unseen_scenarios"] == 150
    assert metrics["binary_metrics"]["f1_score"] >= 0.90
    assert metrics["binary_metrics"]["precision"] >= 0.90
    assert metrics["binary_metrics"]["recall"] >= 0.90
    assert metrics["action_selection_accuracy"] >= 0.80
