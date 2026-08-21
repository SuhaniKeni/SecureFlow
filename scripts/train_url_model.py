import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, confusion_matrix

from secureflow.preprocessing.url_pipeline import process_url_dataset, extract_url_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "secureflow", "models")
DOCS_MODELS_DIR = os.path.join(BASE_DIR, "docs", "models")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_MODELS_DIR, exist_ok=True)

def evaluate_classifier(model, X_tr, y_tr, X_val, y_val, X_te, y_te, name: str):
    """Fits model and computes precision, recall, f1, pr-auc, and confusion matrix."""
    model.fit(X_tr, y_tr)

    # Test set evaluation
    y_pred = model.predict(X_te)
    y_prob = model.predict_proba(X_te)[:, 1] if hasattr(model, "predict_proba") else y_pred

    prec = float(precision_score(y_te, y_pred, zero_division=0))
    rec = float(recall_score(y_te, y_pred, zero_division=0))
    f1 = float(f1_score(y_te, y_pred, zero_division=0))
    pr_auc = float(average_precision_score(y_te, y_prob))
    cm = confusion_matrix(y_te, y_pred).tolist()

    return {
        "model_name": name,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": cm
    }, model

def main():
    print("=== Training URL / Destination Intelligence Component (Stage 5.5) ===")

    url_csv = os.path.join(DATA_PROCESSED_DIR, "phiusiil_phishing_url_clean.csv")
    if not os.path.exists(url_csv):
        raise FileNotFoundError(f"Missing URL dataset: {url_csv}")

    (X_tr, y_tr), (X_val, y_val), (X_te, y_te), config = process_url_dataset(url_csv, seed=42)

    class_counts = np.bincount(y_tr)
    print(f"[+] Train split class distribution: Legitimate (0)={class_counts[0]}, Phishing (1)={class_counts[1]}")

    # Models comparison
    models_to_test = [
        ("Logistic Regression (Baseline)", LogisticRegression(max_iter=1000, random_state=42)),
        ("Random Forest", RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)),
        ("Gradient Boosting", GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42))
    ]

    results = []
    trained_models = {}

    for name, model_obj in models_to_test:
        print(f"[+] Evaluating {name}...")
        metrics, trained_m = evaluate_classifier(model_obj, X_tr, y_tr, X_val, y_val, X_te, y_te, name)
        results.append(metrics)
        trained_models[name] = trained_m
        print(f"    -> Precision: {metrics['precision']}, Recall: {metrics['recall']}, F1: {metrics['f1_score']}, PR-AUC: {metrics['pr_auc']}")

    # Select best model based on F1-Score and PR-AUC
    best_result = max(results, key=lambda x: (x["f1_score"], x["pr_auc"]))
    best_model_name = best_result["model_name"]
    best_model = trained_models[best_model_name]

    print(f"\n[+] Selected Best Model: {best_model_name} (F1: {best_result['f1_score']}, PR-AUC: {best_result['pr_auc']})")

    # Save artifacts
    model_artifact_path = os.path.join(MODELS_DIR, "url_model.joblib")
    artifact_payload = {
        "model": best_model,
        "feature_names": config["feature_names"],
        "scaler_mean": config["scaler_mean"],
        "scaler_scale": config["scaler_scale"],
        "model_name": best_model_name,
        "best_metrics": best_result
    }
    joblib.dump(artifact_payload, model_artifact_path)

    eval_report_json = os.path.join(MODELS_DIR, "url_model_evaluation.json")
    with open(eval_report_json, "w") as f:
        json.dump({"best_model": best_model_name, "all_models_evaluated": results}, f, indent=2)

    feat_meta_path = os.path.join(MODELS_DIR, "url_feature_metadata.json")
    with open(feat_meta_path, "w") as f:
        json.dump({
            "features": config["feature_names"],
            "scaler_mean": config["scaler_mean"],
            "scaler_scale": config["scaler_scale"]
        }, f, indent=2)

    # Save Markdown Evaluation Report
    doc_path = os.path.join(DOCS_MODELS_DIR, "URL_INTELLIGENCE_REPORT.md")
    content = "# SecureFlow: URL / Destination Intelligence Engine Report (Stage 5.5)\n\n"
    content += "This report presents the model evaluation, metrics comparison, and structured evidence schema for the URL Intelligence Component.\n\n"
    content += "## 1. Model Comparison Matrix\n\n"
    content += "| Model Name | Precision | Recall | F1-Score | PR-AUC | Confusion Matrix (TN, FP, FN, TP) |\n"
    content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for r in results:
        cm_flat = f"{r['confusion_matrix'][0][0]}, {r['confusion_matrix'][0][1]}, {r['confusion_matrix'][1][0]}, {r['confusion_matrix'][1][1]}"
        content += f"| **{r['model_name']}** | {r['precision']} | {r['recall']} | **{r['f1_score']}** | **{r['pr_auc']}** | `[{cm_flat}]` |\n"

    content += f"\n**Selected Production Model**: `{best_model_name}`\n\n"
    content += "---\n\n"
    content += "## 2. Structured Evidence Output Contract\n\n"
    content += "As mandated by architectural principles, the URL Intelligence component returns **STRUCTURED EVIDENCE ONLY** and never financial actions (`ALLOW`/`BLOCK`).\n\n"
    content += "```json\n"
    content += "{\n"
    content += "  \"signal\": \"suspicious_destination\",\n"
    content += "  \"risk_score\": 0.9625,\n"
    content += "  \"severity\": \"high\",\n"
    content += "  \"evidence\": {\n"
    content += "    \"domain\": \"elect-pay-bill.top\",\n"
    content += "    \"url_length\": 32,\n"
    content += "    \"has_https\": false,\n"
    content += "    \"is_ip\": false,\n"
    content += "    \"typosquatted_keyword_detected\": true,\n"
    content += "    \"phishing_probability\": 0.9625\n"
    content += "  }\n"
    content += "}\n"
    content += "```\n"

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Saved model artifact: {model_artifact_path}")
    print(f"[+] Saved evaluation JSON: {eval_report_json}")
    print(f"[+] Saved markdown report: {doc_path}")

if __name__ == "__main__":
    main()
