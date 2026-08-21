import os
import json
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

TYPOSQUATTED_KEYWORDS = ["razorpay", "bescom", "sbi", "bank", "paytm", "customs", "police", "refund", "kyc", "claim", "bill", "elect", "utility", "pay-bill"]

def extract_url_features(url_series: pd.Series) -> pd.DataFrame:
    """Extracts lexical and structural URL security features."""
    features = pd.DataFrame()
    urls = url_series.astype(str)

    features["url_length"] = urls.apply(len)
    features["domain_length"] = urls.apply(lambda u: len(u.split("/")[2]) if len(u.split("/")) > 2 else len(u))
    features["num_subdomains"] = urls.apply(lambda u: (u.split("/")[2].count(".")) if len(u.split("/")) > 2 else 0)
    features["is_ip"] = urls.apply(lambda u: 1 if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', u) else 0)
    features["has_https"] = urls.apply(lambda u: 1 if u.startswith("https") else 0)
    features["num_hyphens"] = urls.apply(lambda u: u.count("-"))
    features["num_at_symbol"] = urls.apply(lambda u: u.count("@"))
    features["num_queries"] = urls.apply(lambda u: 1 if "?" in u else 0)
    
    # Check for brand/payment keyword presence in suspicious domains
    def contains_typosquatted_kw(u):
        u_lower = u.lower()
        domain = u_lower.split("/")[2] if len(u_lower.split("/")) > 2 else u_lower
        for kw in TYPOSQUATTED_KEYWORDS:
            if kw in domain and not (domain.endswith(f"{kw}.com") or domain.endswith(f"{kw}.in") or domain.endswith(f"{kw}.co.in")):
                return 1
        return 0

    features["has_typosquatted_keyword"] = urls.apply(contains_typosquatted_kw)
    return features

def process_url_dataset(csv_path: str, seed: int = 42):
    """Processes URL dataset with strict train/val/test separation preventing data leakage."""
    df = pd.read_csv(csv_path)
    if "URL" not in df.columns or "label" not in df.columns:
        raise ValueError("URL dataset must contain 'URL' and 'label' columns")

    X_raw = extract_url_features(df["URL"])
    y = df["label"].values

    # Train (70%), Val (15%), Test (15%) split
    X_train_raw, X_temp, y_train, y_temp = train_test_split(
        X_raw, y, test_size=0.30, random_state=seed, stratify=y
    )
    X_val_raw, X_test_raw, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=seed, stratify=y_temp
    )

    # Fit scaler ONLY on train split to prevent data leakage
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_val = scaler.transform(X_val_raw)
    X_test = scaler.transform(X_test_raw)

    config = {
        "feature_names": list(X_raw.columns),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "seed": seed,
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test)
    }

    return (X_train, y_train), (X_val, y_val), (X_test, y_test), config
