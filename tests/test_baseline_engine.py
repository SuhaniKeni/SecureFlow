import os
import json
import pytest
from secureflow.baseline.baseline_engine import BaselineProtectionEngine
from scripts.run_baseline_comparison import run_full_comparison, REPORT_PATH

def test_baseline_engine_logic():
    engine = BaselineProtectionEngine()
    
    # Normal transaction -> ALLOW
    res_allow = engine.analyze_payment({
        "amount": 500.0,
        "recipient_id": "RCP-001",
        "claimed_merchant": "BESCOM",
        "payment_note": "Electricity bill",
        "url": "https://bescom.co.in/pay"
    })
    assert res_allow["action"] == "ALLOW"

    # Suspicious domain -> BLOCK
    res_block = engine.analyze_payment({
        "amount": 500.0,
        "recipient_id": "RCP-004",
        "claimed_merchant": "BESCOM Board",
        "payment_note": "Urgent bill",
        "url": "http://elect-pay-bill.top/pay"
    })
    assert res_block["action"] == "BLOCK"

    # High amount + new recipient -> VERIFY
    res_verify = engine.analyze_payment({
        "amount": 25000.0,
        "recipient_id": "RCP-005",
        "claimed_merchant": "Hardware Store",
        "payment_note": "Supplies",
        "url": "https://hardware.com"
    })
    assert res_verify["action"] == "VERIFY"

def test_baseline_comparison_script():
    report = run_full_comparison()
    assert os.path.exists(REPORT_PATH)
    assert "benchmark_400_results" in report
    assert "unseen_150_results" in report
    assert report["benchmark_400_results"]["secureflow"]["binary_metrics"]["f1_score"] == 1.0
