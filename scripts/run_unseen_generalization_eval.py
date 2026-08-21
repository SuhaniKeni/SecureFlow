import os
import sys
import json
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from secureflow.api.schemas import PaymentAnalysisRequest
from secureflow.api.routes.payments import analyze_payment
from secureflow.db.database import SessionLocal

UNSEEN_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "unseen_eval_scenarios.json")
REPORT_PATH = os.path.join(PROJECT_ROOT, "docs", "evaluation", "UNSEEN_GENERALIZATION_METRICS.json")

def run_unseen_evaluation():
    if not os.path.exists(UNSEEN_DATASET_PATH):
        raise FileNotFoundError(f"Missing unseen dataset: {UNSEEN_DATASET_PATH}")

    with open(UNSEEN_DATASET_PATH, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    db = SessionLocal()

    total = len(scenarios)
    correct_actions = 0
    
    # Binary classification counts (Attack vs Legitimate)
    tp = 0 # Attack expected -> BLOCK actual
    fp = 0 # Legitimate expected -> BLOCK actual
    tn = 0 # Legitimate expected -> ALLOW/VERIFY actual
    fn = 0 # Attack expected -> ALLOW/VERIFY actual

    subgroups = {
        "seen_categories": {"total": 0, "correct": 0},
        "unseen_categories": {"total": 0, "correct": 0},
        "legitimate_unusual": {"total": 0, "correct": 0},
        "unseen_utility": {"total": 0, "correct": 0},
        "unseen_challan": {"total": 0, "correct": 0},
        "unseen_insurance": {"total": 0, "correct": 0}
    }

    errors = []

    for s in scenarios:
        sc_id = s["scenario_id"]
        cat = s["category"]
        expected_act = s["expected_action"]
        is_seen = s.get("is_seen_category", False)
        inp = s["input"]

        req = PaymentAnalysisRequest(
            customer_id=inp["customer_id"],
            amount=inp["amount"],
            recipient_id=inp["recipient_id"],
            claimed_merchant=inp["claimed_merchant"],
            payment_note=inp["payment_note"],
            url=inp["url"],
            channel=inp.get("channel", "UPI")
        )

        res = analyze_payment(req, db=db)
        actual_act = res.action

        # Check action match
        is_correct = (actual_act == expected_act)
        if is_correct:
            correct_actions += 1

        # Binary confusion matrix mapping
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

        # Subgroup metrics tracking
        sub_key = "seen_categories" if is_seen else "unseen_categories"
        subgroups[sub_key]["total"] += 1
        if is_correct:
            subgroups[sub_key]["correct"] += 1

        if cat == "Legitimate_Unusual":
            subgroups["legitimate_unusual"]["total"] += 1
            if is_correct:
                subgroups["legitimate_unusual"]["correct"] += 1
        elif cat == "Unseen_Category_Utility":
            subgroups["unseen_utility"]["total"] += 1
            if is_correct:
                subgroups["unseen_utility"]["correct"] += 1
        elif cat == "Unseen_Category_Challan":
            subgroups["unseen_challan"]["total"] += 1
            if is_correct:
                subgroups["unseen_challan"]["correct"] += 1
        elif cat == "Unseen_Category_Insurance":
            subgroups["unseen_insurance"]["total"] += 1
            if is_correct:
                subgroups["unseen_insurance"]["correct"] += 1

        if not is_correct:
            errors.append({
                "scenario_id": sc_id,
                "category": cat,
                "expected": expected_act,
                "actual": actual_act,
                "evidence": res.reasons
            })

    db.close()

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    action_acc = round(correct_actions / total, 4)

    metrics = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_unseen_scenarios": total,
        "action_selection_accuracy": action_acc,
        "binary_metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": {
                "tp": tp, "tn": tn, "fp": fp, "fn": fn
            }
        },
        "subgroup_accuracies": {
            k: round(v["correct"] / v["total"], 4) if v["total"] > 0 else 0.0
            for k, v in subgroups.items()
        },
        "errors_count": len(errors),
        "error_details": errors,
        "generalization_assessment": "STRONG GENERALIZATION" if action_acc >= 0.90 else "MODERATE GENERALIZATION"
    }

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[+] Unseen Generalization Evaluation Completed successfully:")
    print(f"    - Total Scenarios: {total}")
    print(f"    - Action Accuracy: {action_acc * 100:.2f}%")
    print(f"    - F1 Score: {f1:.4f}")
    print(f"    - Precision: {precision:.4f}, Recall: {recall:.4f}")
    print(f"    - Confusion Matrix: TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f"    - Subgroup Accuracies: {json.dumps(metrics['subgroup_accuracies'], indent=2)}")
    print(f"    - Report saved to: {REPORT_PATH}")

    return metrics

if __name__ == "__main__":
    run_unseen_evaluation()
