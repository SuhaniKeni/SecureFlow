import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix

URGENCY_KEYWORDS = ["urgent", "immediately", "within", "overdue", "disconnection", "tonight", "cutoff", "now", "today"]
IMPERSONATION_KEYWORDS = ["electricity", "bescom", "bank", "sbi", "customs", "police", "kyc", "support", "refund", "tax"]
THREAT_KEYWORDS = ["arrest", "legal action", "suspended", "blocked", "penalty", "warrant", "fine", "disconnected"]

def extract_text_heuristics(messages: pd.Series) -> np.ndarray:
    """Extracts domain-specific scam text heuristic features."""
    feats = []
    for msg in messages.astype(str):
        m_lower = msg.lower()
        urgency_count = sum(1 for kw in URGENCY_KEYWORDS if kw in m_lower)
        impersonation_count = sum(1 for kw in IMPERSONATION_KEYWORDS if kw in m_lower)
        threat_count = sum(1 for kw in THREAT_KEYWORDS if kw in m_lower)
        has_url = 1 if ("http://" in m_lower or "https://" in m_lower or ".com" in m_lower or ".top" in m_lower) else 0
        msg_len = len(msg)
        feats.append([urgency_count, impersonation_count, threat_count, has_url, msg_len])
    return np.array(feats, dtype=np.float32)

def process_nlp_dataset(csv_path: str, max_features: int = 500, seed: int = 42):
    """Preprocesses text scam dataset with strict train/val/test split and no data leakage."""
    df = pd.read_csv(csv_path)
    if "message" not in df.columns or "is_spam" not in df.columns:
        raise ValueError("Text dataset must contain 'message' and 'is_spam' columns")

    X_text = df["message"]
    y = df["is_spam"].values

    # Train (70%), Val (15%), Test (15%) split
    X_train_text, X_temp_text, y_train, y_temp = train_test_split(
        X_text, y, test_size=0.30, random_state=seed, stratify=y
    )
    X_val_text, X_test_text, y_val, y_test = train_test_split(
        X_temp_text, y_temp, test_size=0.50, random_state=seed, stratify=y_temp
    )

    # Fit TF-IDF Vectorizer STRICTLY on train set to prevent data leakage
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english", ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_val_tfidf = vectorizer.transform(X_val_text)
    X_test_tfidf = vectorizer.transform(X_test_text)

    # Extract heuristics
    h_train = extract_text_heuristics(X_train_text)
    h_val = extract_text_heuristics(X_val_text)
    h_test = extract_text_heuristics(X_test_text)

    # Combine TF-IDF + Heuristics
    X_train = hstack([X_train_tfidf, csr_matrix(h_train)]).tocsr()
    X_val = hstack([X_val_tfidf, csr_matrix(h_val)]).tocsr()
    X_test = hstack([X_test_tfidf, csr_matrix(h_test)]).tocsr()

    config = {
        "max_features": max_features,
        "vocabulary_size": len(vectorizer.vocabulary_),
        "heuristic_features": ["urgency_count", "impersonation_count", "threat_count", "has_url", "msg_len"],
        "seed": seed,
        "train_samples": X_train.shape[0],
        "val_samples": X_val.shape[0],
        "test_samples": X_test.shape[0]
    }

    return (X_train, y_train), (X_val, y_val), (X_test, y_test), config
