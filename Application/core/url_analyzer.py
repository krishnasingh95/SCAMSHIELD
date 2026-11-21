"""
ScamShield — URL Phishing Analyzer
Core logic: feature extraction + Random Forest inference.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from utils.feature_extractors import extract_url_features
from utils.risk_levels import confidence_to_risk, RiskLevel
from utils.logger import get_logger
from config import MODEL_PATHS

logger = get_logger("url_analyzer")

# Features fed into the Random Forest (exact training column order)
URL_FEATURE_COLUMNS = [
    "url_length", "domain_length", "path_length", "query_length",
    "num_subdomains", "has_ip_address", "has_https",
    "has_suspicious_tld", "num_special_chars", "num_digits_in_domain",
    "has_brand_keyword", "brand_in_subdomain", "has_redirect", "path_depth",
]


class URLAnalyzer:
    def __init__(self):
        self.model    = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        """Load trained Random Forest model and metadata from disk."""
        try:
            if os.path.exists(MODEL_PATHS.get("url", "")):
                self.model = joblib.load(MODEL_PATHS["url"])
                logger.info("URL model loaded.")

            if os.path.exists(MODEL_PATHS.get("url_metadata", "")):
                with open(MODEL_PATHS["url_metadata"], "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info("URL metadata loaded.")
        except Exception as e:
            logger.warning(f"Could not load URL model components: {e}")

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    @property
    def model_version(self) -> str:
        if self.metadata and "model_version" in self.metadata:
            return self.metadata["model_version"]
        return "1.0.0"

    @property
    def model_info(self) -> dict:
        return self.metadata or {}

    def extract_features(self, url: str) -> dict:
        return extract_url_features(url)

    def predict(self, url: str) -> dict:
        """
        Returns a result dict.
        If no model is loaded, returns status='model_not_loaded'.
        """
        raw = extract_url_features(url)

        if not self.model_loaded:
            return {
                "status":     "model_not_loaded",
                "label":      None,
                "confidence": None,
                "risk_level": RiskLevel.UNKNOWN,
                "features":   raw,
            }

        try:
            # Build 14-feature row matching exact training order and dtype
            feat_df = pd.DataFrame(
                [{k: raw.get(k, 0) for k in URL_FEATURE_COLUMNS}],
                columns=URL_FEATURE_COLUMNS,
                dtype=np.float32
            )

            expected_features = getattr(self.model, "n_features_in_", 14)
            if feat_df.shape[1] != expected_features:
                raise ValueError(
                    f"Feature shape mismatch: URL features have {feat_df.shape[1]} columns, "
                    f"but model expects {expected_features}."
                )

            prob = self.model.predict_proba(feat_df.values)[0]
            pos_idx = list(self.model.classes_).index(1) if hasattr(self.model, "classes_") else 1
            phish_prob = float(prob[pos_idx])
            label = "PHISHING" if phish_prob >= 0.5 else "SAFE"
            risk_level = confidence_to_risk(phish_prob)

            return {
                "status":     "ok",
                "label":      label,
                "confidence": phish_prob,
                "risk_level": risk_level,
                "features":   raw,
            }
        except Exception as e:
            logger.error(f"URL prediction error: {e}")
            return {"status": "error", "message": str(e), "risk_level": RiskLevel.UNKNOWN}
