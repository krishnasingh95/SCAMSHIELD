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

SHORT_DOMAINS = {
    "bit.ly", "tinyurl.com", "is.gd", "rb.gy", "cutt.ly",
    "t.ly", "shorturl.at", "ow.ly", "tiny.cc", "wa.me"
}

OFFICIAL_DOMAINS = {
    "google.com", "google.co.in", "amazon.com", "amazon.in",
    "apple.com", "microsoft.com", "facebook.com", "instagram.com",
    "whatsapp.com", "netflix.com", "sbi.co.in", "onlinesbi.sbi",
    "hdfcbank.com", "icicibank.com", "axisbank.com", "paytm.com",
    "phonepe.com", "paypal.com", "wikipedia.org"
}

SENSITIVE_KEYWORDS = [
    "login", "signin", "sign-in", "log-in", "verify", "verification",
    "banking", "secure", "account", "update", "admin", "wallet",
    "claim", "bonus", "confirm", "session", "credential", "auth",
    "password", "support", "bill", "challan", "kyc", "pan", "yono",
    "disconnection", "unblock", "reactivate", "suspend", "blocked"
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

            # 1. Base ML inference
            prob = self.model.predict_proba(feat_df.values)[0]
            pos_idx = list(self.model.classes_).index(1) if hasattr(self.model, "classes_") else 1
            raw_prob = float(prob[pos_idx])

            # 2. Heuristic structural risk flags & multi-layer threat calibration
            flags = []
            calibrated_prob = raw_prob
            domain = raw.get("_parsed_domain", "").lower()
            has_https = raw.get("has_https", 0) == 1
            path_str = str(url).lower()

            # Shortener masking
            is_shortener = (
                raw.get("_is_shortener", 0)
                or any(domain == sd or domain.endswith("." + sd) for sd in SHORT_DOMAINS)
            )
            if is_shortener:
                flags.append("URL Shortener masking destination")
                has_sensitive_slug = any(kw in path_str for kw in SENSITIVE_KEYWORDS)
                if has_sensitive_slug:
                    flags.append("Shortener hides credential/banking path")
                    calibrated_prob = max(calibrated_prob, 0.88)
                else:
                    calibrated_prob = max(calibrated_prob, 0.65)

            # Brand impersonation on non-official host
            brand_matched = raw.get("has_brand_keyword", 0)
            is_official = any(domain == od or domain.endswith("." + od) for od in OFFICIAL_DOMAINS)
            if brand_matched and not is_official:
                flags.append("Target brand mention on untrusted domain")
                calibrated_prob = max(calibrated_prob, 0.78)

            # Insecure HTTP on sensitive endpoint
            sensitive_matched = any(kw in path_str for kw in SENSITIVE_KEYWORDS)
            if sensitive_matched and not has_https:
                flags.append("Insecure HTTP protocol on sensitive action")
                calibrated_prob = max(calibrated_prob, 0.68)

            # Deep nested path on non-HTTPS
            if raw.get("path_depth", 0) >= 5 and not has_https:
                flags.append("Deeply nested path on unencrypted host")
                calibrated_prob = max(calibrated_prob, 0.65)

            # Raw IP address
            if raw.get("has_ip_address", 0):
                flags.append("Raw IP address used as domain")
                calibrated_prob = max(calibrated_prob, 0.85)

            # Suspicious TLD on sensitive endpoint
            if raw.get("has_suspicious_tld", 0) and sensitive_matched:
                flags.append(f"High-abuse TLD on sensitive endpoint ({raw.get('_tld','')})")
                calibrated_prob = max(calibrated_prob, 0.82)

            # Open redirect
            if raw.get("has_redirect", 0):
                flags.append("Open redirect parameter detected")
                calibrated_prob = max(calibrated_prob, 0.70)

            # High special char density
            if raw.get("num_special_chars", 0) >= 4:
                flags.append("Excessive special characters in URL")

            # Final classification
            calibrated_prob = round(min(max(calibrated_prob, 0.0), 1.0), 4)
            label = "PHISHING" if calibrated_prob >= 0.50 else "SAFE"
            risk_level = confidence_to_risk(calibrated_prob)
            raw["_flags"] = flags

            return {
                "status":     "ok",
                "label":      label,
                "confidence": calibrated_prob,
                "raw_ml_confidence": raw_prob,
                "risk_level": risk_level,
                "features":   raw,
                "flags":      flags,
            }
        except Exception as e:
            logger.error(f"URL prediction error: {e}")
            return {"status": "error", "message": str(e), "risk_level": RiskLevel.UNKNOWN}
