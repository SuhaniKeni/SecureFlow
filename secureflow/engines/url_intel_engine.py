import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

from secureflow.preprocessing.url_pipeline import extract_url_features

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "url_model.joblib"
)

class URLIntelligenceEngine:
    """Engine for assessing URL and payment destination domain risk.
    
    Produces structured evidence vectors for policy evaluation.
    STRICT MANDATE: Never outputs financial block decisions ('BLOCK' / 'ALLOW').
    """

    def __init__(self, model_path: Optional[str] = None):
        target_path = model_path or DEFAULT_MODEL_PATH
        if os.path.exists(target_path):
            payload = joblib.load(target_path)
            self.model = payload["model"]
            self.feature_names = payload["feature_names"]
            self.scaler_mean = np.array(payload["scaler_mean"])
            self.scaler_scale = np.array(payload["scaler_scale"])
            self.is_loaded = True
        else:
            self.model = None
            self.is_loaded = False

    def analyze(self, url: Optional[str]) -> Dict[str, Any]:
        """Analyzes a destination URL and returns structured security evidence."""
        if not url or not isinstance(url, str) or not url.strip():
            return {
                "signal": "no_destination_url",
                "risk_score": 0.0,
                "severity": "low",
                "evidence": {
                    "url": "",
                    "domain": "",
                    "has_https": True,
                    "is_ip": False,
                    "phishing_probability": 0.0
                }
            }

        url_clean = url.strip()
        # Feature extraction
        df_feat = extract_url_features(pd.Series([url_clean]))

        # Calculate heuristics directly
        domain = url_clean.split("/")[2] if len(url_clean.split("/")) > 2 else url_clean
        has_https = url_clean.startswith("https")
        is_ip = bool(df_feat["is_ip"].iloc[0])
        typosquatted = bool(df_feat["has_typosquatted_keyword"].iloc[0])

        # Domain structural heuristic risk
        heur_risk = 0.85 if (typosquatted or is_ip or not has_https) else 0.05

        if self.is_loaded and self.model is not None:
            # Standardize using fitted mean and scale
            X_raw = df_feat[self.feature_names].values
            X_scaled = (X_raw - self.scaler_mean) / self.scaler_scale
            ml_prob = float(self.model.predict_proba(X_scaled)[0, 1])
            if has_https and not is_ip and not typosquatted and domain.endswith((".co.in", ".in", ".com", ".gov.in", ".org", ".net")) and len(url_clean) < 60:
                prob = min(ml_prob, 0.15)
            else:
                prob = max(ml_prob, heur_risk)
        else:
            # Heuristic fallback if model artifact not present
            prob = heur_risk

        # Determine severity level
        if prob >= 0.70:
            severity = "high"
            signal = "suspicious_destination"
        elif prob >= 0.40:
            severity = "medium"
            signal = "moderate_destination_risk"
        else:
            severity = "low"
            signal = "clean_destination"

        return {
            "signal": signal,
            "risk_score": round(prob, 4),
            "severity": severity,
            "evidence": {
                "url": url_clean,
                "domain": domain,
                "url_length": len(url_clean),
                "has_https": has_https,
                "is_ip": is_ip,
                "typosquatted_keyword_detected": typosquatted,
                "phishing_probability": round(prob, 4)
            }
        }
