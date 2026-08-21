import os
import json
import pytest
from scripts.run_evaluation_framework import run_evaluation, LegacyBaselineEngine

def test_legacy_baseline_engine():
    bl = LegacyBaselineEngine()
    assert bl.evaluate(100.0, "normal payment") == "ALLOW"
    assert bl.evaluate(85000.0, "laptop purchase") == "BLOCK" # Naive baseline error
    assert bl.evaluate(100.0, "URGENT disconnection") == "BLOCK"

def test_run_evaluation_framework():
    results = run_evaluation()
    
    assert "baseline_model" in results
    assert "secureflow_adaptive_engine" in results
    assert "delta_improvements" in results

    sf = results["secureflow_adaptive_engine"]
    bl = results["baseline_model"]

    # Verify metric keys exist
    for k in ["precision", "recall", "f1_score", "scam_protection_rate", "legitimate_payment_preservation_rate", "action_selection_accuracy", "mean_latency_ms"]:
        assert k in sf
        assert k in bl

    # Verify SecureFlow superiority over naive baseline
    assert sf["f1_score"] >= bl["f1_score"]
    assert sf["action_selection_accuracy"] >= bl["action_selection_accuracy"]
    assert sf["unnecessary_blocking_rate"] <= bl["unnecessary_blocking_rate"]

def test_evaluation_artifacts_exist():
    assert os.path.exists("docs/evaluation/EVALUATION_METRICS.json")
    assert os.path.exists("docs/evaluation/EVALUATION_METRICS.csv")
    assert os.path.exists("docs/evaluation/EVALUATION_REPORT.md")
