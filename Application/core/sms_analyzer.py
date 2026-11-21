"""
ScamShield — SMS Scam Analyzer v2
Core logic: feature extraction + TF-IDF vectorization + Random Forest inference.

Supports both v1 (10 features) and v2 (28 features) models transparently
by reading the feature column list from metadata.
"""
import os
import re
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from utils.risk_levels import confidence_to_risk, RiskLevel
from utils.logger import get_logger
from config import MODEL_PATHS

logger = get_logger("sms_analyzer")

# ── v1 fallback feature columns (10 features, legacy model) ─────────────────
SMS_FEATURE_COLUMNS_V1 = [
    "char_count", "word_count", "url_count", "has_url",
    "uppercase_ratio", "digit_ratio", "special_char_count",
    "keyword_hits", "exclamation_count", "question_count",
]

# ── Shared utilities ─────────────────────────────────────────────────────────
SCAM_KEYWORDS_V1 = [
    "urgent", "winner", "won", "free", "claim",
    "prize", "cash", "guaranteed", "offer",
    "credit", "loan", "verify", "login",
    "click", "award", "congratulations",
    "selected", "limited", "immediately",
    "suspended", "blocked", "password",
    "otp", "bank", "kyc", "payment",
]

SCAM_KEYWORDS_V2 = [
    "urgent", "winner", "won", "free", "claim", "prize", "cash",
    "guaranteed", "offer", "credit", "loan", "verify", "login",
    "click", "award", "congratulations", "selected", "limited",
    "immediately", "suspended", "suspension", "blocked", "password", "otp",
    "bank", "kyc", "payment", "account", "confirm", "update",
    "expire", "expiring", "reward", "bonus", "jackpot", "risk", "tax",
    "refund", "government", "police", "arrest", "fine", "penalty",
    "pan", "aadhaar", "sbi", "hdfc", "icici", "axis", "pnb", "yono",
    "netbanking", "electricity", "power", "disconnected", "disconnection",
    "bill", "challan", "traffic", "customs", "courier", "fedex", "parcel",
    "apk", "telegram", "earning", "wfh", "part-time", "lottery", "kbc",
    "cashback", "credited", "closure", "locked", "unblock", "reactivate",
    "due", "summons", "unauthorized", "action required", "warning",
]

def normalize_defanged(text: str) -> str:
    """Normalize defanged URLs and obfuscations commonly found in security blogs and test vectors."""
    t = str(text)
    t = re.sub(r"(?i)\bhxxps?://", lambda m: m.group(0).lower().replace("xx", "tt"), t)
    t = re.sub(r"\[:\]", ":", t)
    t = re.sub(r"(?<=[a-zA-Z0-9])(?:\[dot\]|\(dot\)|\[\.\]|\(\.\))(?=[a-zA-Z0-9])", ".", t, flags=re.I)
    return t

SHORT_DOMAINS = [
    "bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly", "tiny.cc",
    "is.gd", "cutt.ly", "rb.gy", "shorturl.at", "t.ly", "wa.me", "bit[dot]ly"
]

URL_PAT   = re.compile(
    r"(?:https?://|www\.)[a-z0-9-]+(?:\.[a-z0-9-]+)+(?:/[^\s<>\"']*)?|"
    r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|org|net|in|co|io|xyz|top|site|online|live|club|cc|me|info|gov|edu|ai|app|biz|tv|tech|store|shop|mobi|vip|pro|ly)(?:/[^\s<>\"']*)?\b",
    re.I
)
PHONE_PAT = re.compile(r"\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b")
EMAIL_PAT = re.compile(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", re.I)
MONEY_PAT = re.compile(r"(?:rs\.?|inr|usd|\$|£|€)\s*[\d,]+|[\d,]+\s*(?:rs\.?|inr|usd)", re.I)
CTA_PAT   = re.compile(
    r"\b(?:call|reply|text|click|visit|go to|open|download|install|dial|verify|verification|update|complete|confirm|pay|submit|claim|login|log in|check|reactivate|unblock|redeem)\b",
    re.I
)
THREAT_PAT= re.compile(
    r"\b(?:arrest(?:ed|ing)?|court|legal|notice[s]?|expir(?:e|ed|ing|y)|suspend(?:ed|ing)?|suspension|block(?:ed|ing|s)?|fine[s]?|penalt(?:y|ies)|warn(?:ing|ed|s)?|bann(?:ed|ing)|terminat(?:ed|ing|ion)?|deactivat(?:ed|ing|ion)?|clos(?:ed|ing|ure)?|freez(?:e|ing|en)|frozen|lock(?:ed|ing)?|seiz(?:ed|ing|ure)?|unauthorized|cancelled|cancellation|disconnect(?:ed|ing|ion)?)\b",
    re.I
)
DATE_PAT  = re.compile(r"\b\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?\b")


def _extract_v1_features(text: str) -> dict:
    """10-feature set for v1 model compatibility."""
    t = str(text)
    lo = t.lower()
    n = max(len(t), 1)
    urls = URL_PAT.findall(t)
    kwh = sum(
        len(re.findall(r"(?<!\w)" + re.escape(k) + r"(?!\w)", lo))
        for k in SCAM_KEYWORDS_V1
    )
    return {
        "char_count":         len(t),
        "word_count":         len(t.split()),
        "url_count":          len(urls),
        "has_url":            int(len(urls) > 0),
        "uppercase_ratio":    sum(c.isupper() for c in t) / n,
        "digit_ratio":        sum(c.isdigit() for c in t) / n,
        "special_char_count": len(re.findall(r"[!?$#@*]", t)),
        "keyword_hits":       kwh,
        "exclamation_count":  t.count("!"),
        "question_count":     t.count("?"),
        "_matched_keywords":  [k for k in SCAM_KEYWORDS_V1
                               if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", lo)],
        "_extracted_urls":    urls,
    }


def _extract_v2_features(text: str) -> dict:
    """28-feature set for v2 model."""
    t_clean = normalize_defanged(text)
    t = t_clean
    lo = t.lower()
    n = max(len(t), 1)
    words = t.split()
    sentences = re.split(r"[.!?]+", t)

    urls     = URL_PAT.findall(t)
    phones   = PHONE_PAT.findall(t)
    emails   = EMAIL_PAT.findall(t)
    money    = MONEY_PAT.findall(lo)
    cta      = CTA_PAT.findall(lo)
    threats  = THREAT_PAT.findall(lo)
    dates    = DATE_PAT.findall(t)

    kwh = sum(
        len(re.findall(r"(?<!\w)" + re.escape(k) + r"(?!\w)", lo))
        for k in SCAM_KEYWORDS_V2
    )
    matched_kw = [k for k in SCAM_KEYWORDS_V2
                  if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", lo)]

    feats = {
        "char_count":           len(t),
        "word_count":           len(words),
        "sentence_count":       len(sentences),
        "avg_word_length":      (sum(len(w) for w in words) / max(len(words), 1)),
        "uppercase_ratio":      sum(c.isupper() for c in t) / n,
        "digit_ratio":          sum(c.isdigit() for c in t) / n,
        "special_char_count":   len(re.findall(r"[!?$#@*&]", t)),
        "exclamation_count":    t.count("!"),
        "question_count":       t.count("?"),
        "caps_word_count":      sum(1 for w in words if w.isupper() and len(w) > 1),
        "url_count":            len(urls),
        "has_url":              int(len(urls) > 0),
        "url_in_body_ratio":    len(urls) / max(len(words), 1),
        "has_short_url":        int(any(x in lo for x in SHORT_DOMAINS)),
        "phone_count":          len(phones),
        "email_count":          len(emails),
        "has_cta":              int(len(cta) > 0),
        "cta_count":            len(cta),
        "has_money_mention":    int(len(money) > 0),
        "money_mention_count":  len(money),
        "has_threat":           int(len(threats) > 0),
        "threat_count":         len(threats),
        "keyword_hits":         kwh,
        "keyword_density":      kwh / max(len(words), 1),
        "has_date":             int(len(dates) > 0),
        "text_length_log":      float(np.log1p(len(t))),
        "punctuation_ratio":    len(re.findall(r"[^\w\s]", t)) / n,
        "numeric_token_ratio":  sum(1 for w in words if w.isdigit()) / max(len(words), 1),
        "_matched_keywords":    matched_kw,
        "_extracted_urls":      urls,
    }
    return feats


class SMSAnalyzer:
    def __init__(self):
        self.model       = None
        self.vectorizer  = None
        self.metadata    = None
        self._model_ver  = "v1"           # detected from metadata
        self._feat_cols  = SMS_FEATURE_COLUMNS_V1
        self._load_model()

    def _load_model(self):
        """Load model, vectorizer, and metadata. Auto-detect v1 vs v2."""
        try:
            if os.path.exists(MODEL_PATHS.get("sms", "")):
                self.model = joblib.load(MODEL_PATHS["sms"])
                logger.info("SMS model loaded.")

            if os.path.exists(MODEL_PATHS.get("sms_vectorizer", "")):
                self.vectorizer = joblib.load(MODEL_PATHS["sms_vectorizer"])
                logger.info("SMS TF-IDF vectorizer loaded.")

            if os.path.exists(MODEL_PATHS.get("sms_metadata", "")):
                self.metadata = joblib.load(MODEL_PATHS["sms_metadata"])
                logger.info("SMS metadata loaded.")

                # Detect model version from metadata
                meta_ver = self.metadata.get("version", "1.0.0")
                if meta_ver.startswith("2"):
                    self._model_ver = "v2"
                    self._feat_cols = self.metadata.get("feature_columns",
                                                        self.metadata.get("numerical_feature_names",
                                                                          SMS_FEATURE_COLUMNS_V1))
                    logger.info(f"SMS model v2 detected ({len(self._feat_cols)} numerical features).")
                else:
                    self._model_ver = "v1"
                    self._feat_cols = SMS_FEATURE_COLUMNS_V1
                    logger.info("SMS model v1 detected (10 numerical features).")

        except Exception as e:
            logger.warning(f"Could not load SMS model components: {e}")

    @property
    def model_loaded(self) -> bool:
        return self.model is not None and self.vectorizer is not None

    @property
    def model_version(self) -> str:
        return self._model_ver

    def extract_features(self, text: str) -> dict:
        if self._model_ver == "v2":
            return _extract_v2_features(text)
        return _extract_v1_features(text)

    def predict(self, text: str) -> dict:
        """
        Returns a result dict.
        If model or vectorizer is not loaded, returns status='model_not_loaded'.
        """
        raw = self.extract_features(text)

        if not self.model_loaded:
            return {
                "status":           "model_not_loaded",
                "label":            None,
                "confidence":       None,
                "risk_level":       RiskLevel.UNKNOWN,
                "features":         raw,
                "matched_keywords": raw.get("_matched_keywords", []),
                "extracted_urls":   raw.get("_extracted_urls", []),
            }

        try:
            # 1. Transform text with TF-IDF vectorizer (using normalized tokens)
            cleaned_text = normalize_defanged(text)
            tfidf_feat = self.vectorizer.transform([cleaned_text])

            # 2. Extract numerical features in exact training column order
            num_vals   = {k: raw.get(k, 0) for k in self._feat_cols}
            num_df     = pd.DataFrame([num_vals])
            num_sparse = csr_matrix(num_df.to_numpy(dtype=np.float32))

            # 3. Combine TF-IDF and numerical features
            combined = hstack([tfidf_feat, num_sparse], format="csr")

            # Verify feature dimension
            expected_features = getattr(self.model, "n_features_in_", combined.shape[1])
            if combined.shape[1] != expected_features:
                raise ValueError(
                    f"Feature shape mismatch: combined={combined.shape[1]}, "
                    f"model expects={expected_features}."
                )

            # 4. Predict
            probs    = self.model.predict_proba(combined)[0]
            pos_idx  = list(self.model.classes_).index(1) if hasattr(self.model, "classes_") else 1
            scam_prob = float(probs[pos_idx])
            label     = "SCAM" if scam_prob >= 0.5 else "SAFE"
            risk_level = confidence_to_risk(scam_prob)

            return {
                "status":           "ok",
                "label":            label,
                "confidence":       scam_prob,
                "risk_level":       risk_level,
                "features":         raw,
                "matched_keywords": raw.get("_matched_keywords", []),
                "extracted_urls":   raw.get("_extracted_urls", []),
            }
        except Exception as e:
            logger.error(f"SMS prediction error: {e}")
            return {"status": "error", "message": str(e), "risk_level": RiskLevel.UNKNOWN}
