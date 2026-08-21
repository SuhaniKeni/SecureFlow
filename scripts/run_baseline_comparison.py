import os
import sys
import json
import time
import numpy as np
from typing import Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from secureflow.baseline.baseline_engine import BaselineProtectionEngine
from secureflow.api.schemas import PaymentAnalysisRequest
from secureflow.api.routes.payments import analyze_payment
from secureflow.db.database import SessionLocal

BENCHMARK_400_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "expanded_eval_scenarios.json")
UNSEEN_150_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "unseen_eval_scenarios.json")
REPORT_PATH = os.path.join(PROJECT_ROOT, "docs", "evaluation", "BASELINE_VS_SECUREFLOW_METRICS.json")

def evaluate_system_on_dataset(system_name: str, dataset_path: str, db=None) -> Dict[str, Any]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    baseline_engine = BaselineProtectionEngine() if system_name == "Baseline" else None

    total = len(scenarios)
    correct_actions = 0

    tp = 0 # Attack expected -> BLOCK actual
    fp = 0 # Legitimate expected -> BLOCK actual
    tn = 0 # Legitimate expected -> ALLOW/VERIFY/HOLD actual
    fn = 0 # Attack expected -> ALLOW/VERIFY/HOLD actual

    # Friction counts
    legit_total = 0
    legit_allowed = 0
    legit_verified = 0
    legit_held = 0
    legit_blocked = 0

    latencies = []

    for s in scenarios:
        expected_act = s["expected_action"]
        inp = s["input"]

        t0 = time.perf_counter()
        if system_name == "Baseline":
            res = baseline_engine.analyze_payment(inp)
            actual_act = res["action"]
        else:
            req = PaymentAnalysisRequest(
                customer_id=inp["customer_id"],
                amount=inp["amount"],
                recipient_id=inp["recipient_id"],
                claimed_merchant=inp["claimed_merchant"],
                payment_note=inp["payment_note"],
                url=inp["url"],
                channel=inp.get("channel", "UPI")
            )
            resp = analyze_payment(req, db=db)
            actual_act = resp.action

        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000) # In ms

        # Action match
        if actual_act == expected_act:
            correct_actions += 1

        # Binary mapping
        is_attack_expected = (expected_act == "BLOCK")
        is_blocked_actual = (actual_act == "BLOCK")

        if is_attack_expected and is_blocked_actual:
            tp += 1
        elif not is_attack_expected and not is_blocked_actual:
            tn += 1
        elif not is_attack_expected and is_blocked_actual:
            fp += 1
        elif is_attack_expected and not is_blocked_actual:
            fn += 1

        # Friction tracking
        if not is_attack_expected:
            legit_total += 1
            if actual_act == "ALLOW":
                legit_allowed += 1
            elif actual_act == "VERIFY":
                legit_verified += 1
            elif actual_act == "HOLD":
                legit_held += 1
            elif actual_act == "BLOCK":
                legit_blocked += 1

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    return {
        "system": system_name,
        "total_scenarios": total,
        "action_accuracy": round(correct_actions / total, 4),
        "binary_metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "scam_protection_rate": recall,
            "unnecessary_blocking_rate": round(fp / (tn + fp), 4) if (tn + fp) > 0 else 0.0
        },
        "friction_metrics": {
            "legitimate_total": legit_total,
            "legitimate_preservation_rate": round((legit_allowed + legit_verified + legit_held) / legit_total, 4) if legit_total > 0 else 0.0,
            "unnecessary_verification_rate": round(legit_verified / legit_total, 4) if legit_total > 0 else 0.0,
            "unnecessary_holding_rate": round(legit_held / legit_total, 4) if legit_total > 0 else 0.0,
            "unnecessary_blocking_rate": round(legit_blocked / legit_total, 4) if legit_total > 0 else 0.0
        },
        "latency_ms": {
            "mean": round(float(np.mean(latencies)), 2),
            "median": round(float(np.median(latencies)), 2),
            "p95": round(float(np.percentile(latencies, 95)), 2),
            "p99": round(float(np.percentile(latencies, 99)), 2)
        }
    }

def run_full_comparison():
    db = SessionLocal()

    print("=== Running Baseline vs SecureFlow Comparative Evaluation ===")
    
    res_400_baseline = evaluate_system_on_dataset("Baseline", BENCHMARK_400_PATH)
    res_400_secureflow = evaluate_system_on_dataset("SecureFlow", BENCHMARK_400_PATH, db=db)

    res_150_baseline = evaluate_system_on_dataset("Baseline", UNSEEN_150_PATH)
    res_150_secureflow = evaluate_system_on_dataset("SecureFlow", UNSEEN_150_PATH, db=db)

    db.close()

    full_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark_400_results": {
            "baseline": res_400_baseline,
            "secureflow": res_400_secureflow
        },
        "unseen_150_results": {
            "baseline": res_150_baseline,
            "secureflow": res_150_secureflow
        }
    }

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print("\n--- 400 Benchmark Comparison Results ---")
    print(f"  Baseline Action Acc: {res_400_baseline['action_accuracy']*100:.2f}% | F1: {res_400_baseline['binary_metrics']['f1_score']} | Mean Latency: {res_400_baseline['latency_ms']['mean']} ms")
    print(f"  SecureFlow Action Acc: {res_400_secureflow['action_accuracy']*100:.2f}% | F1: {res_400_secureflow['binary_metrics']['f1_score']} | Mean Latency: {res_400_secureflow['latency_ms']['mean']} ms")

    print("\n--- 150 Unseen Dataset Comparison Results ---")
    print(f"  Baseline Action Acc: {res_150_baseline['action_accuracy']*100:.2f}% | F1: {res_150_baseline['binary_metrics']['f1_score']} | Mean Latency: {res_150_baseline['latency_ms']['mean']} ms")
    print(f"  SecureFlow Action Acc: {res_150_secureflow['action_accuracy']*100:.2f}% | F1: {res_150_secureflow['binary_metrics']['f1_score']} | Mean Latency: {res_150_secureflow['latency_ms']['mean']} ms")
    print(f"\n[+] Baseline vs SecureFlow comparison report saved to {REPORT_PATH}")

    return full_report

if __name__ == "__main__":
    run_full_comparison()
