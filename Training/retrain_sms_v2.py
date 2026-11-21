"""
ScamShield — SMS Model Retraining v2 (Production Fixed Pipeline)
================================================================
Combines:
  1. Word + Char TF-IDF via FeatureUnion (single vectorizer artifact, 4000 dims)
  2. 28 Domain & Heuristic Features (financial, urgency, threat, contact, lexical)
  3. UCI SMSSpamCollection + Curated Modern Smishing & Ham Augmentation (Indian & Global vectors)
  4. Defanged link normalization (hxxp://, bit[dot]ly, etc.)
  5. Class-balanced Random Forest with Stratified 5-Fold Cross-Validation
  6. Saves matching artifacts to Training/Models and Application/models
"""

import os, sys, re, json, warnings
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib
from scipy.sparse import hstack, csr_matrix

from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

warnings.filterwarnings("ignore")

BASE        = Path(__file__).resolve().parent
RAW_DIR     = BASE / "datasets" / "raw"
MODELS_OUT  = BASE / "Models"
REPORTS_OUT = BASE / "Reports"
APP_MODELS  = BASE.parent / "Application" / "models"
MODELS_OUT.mkdir(exist_ok=True)
REPORTS_OUT.mkdir(exist_ok=True)
APP_MODELS.mkdir(exist_ok=True)

SMS_FILE = RAW_DIR / "SMSSpamCollection"
AUG_FILE = RAW_DIR / "modern_smishing_augmentation.csv"

print("=" * 65)
print("ScamShield SMS Model Retraining v2 (Production Pipeline)")
print("=" * 65)

# 1. Load data
df_base = pd.read_csv(SMS_FILE, sep="\t", header=None, names=["label", "text"],
                      encoding="utf-8", on_bad_lines="skip")

if AUG_FILE.exists():
    print(f"Loading modern smishing & ham augmentation from {AUG_FILE.name}...")
    df_aug = pd.read_csv(AUG_FILE, encoding="utf-8")
    df = pd.concat([df_base, df_aug], ignore_index=True)
else:
    df = df_base

df.dropna(inplace=True)
df = df[df["text"].str.strip().str.len() > 0].copy()
df["label_bin"] = (df["label"].str.lower() == "spam").astype(int)
print(f"Total samples: {len(df):,} | Spam: {df['label_bin'].sum():,} | Ham: {(1-df['label_bin']).sum():,}")

# 2. Extract 28 numerical & behavioral features
SCAM_KEYWORDS = [
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
    t = str(text)
    t = re.sub(r"(?i)\bhxxps?://", lambda m: m.group(0).lower().replace("xx", "tt"), t)
    t = re.sub(r"\[:\]", ":", t)
    t = re.sub(r"(?<=[a-zA-Z0-9])(?:\[dot\]|\(dot\)|\[\.\]|\(\.\))(?=[a-zA-Z0-9])", ".", t, flags=re.I)
    return t

SHORT_DOMAINS = [
    "bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly", "tiny.cc",
    "is.gd", "cutt.ly", "rb.gy", "shorturl.at", "t.ly", "wa.me", "bit[dot]ly"
]

URL_PAT    = re.compile(
    r"(?:https?://|www\.)[a-z0-9-]+(?:\.[a-z0-9-]+)+(?:/[^\s<>\"']*)?|"
    r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|org|net|in|co|io|xyz|top|site|online|live|club|cc|me|info|gov|edu|ai|app|biz|tv|tech|store|shop|mobi|vip|pro|ly)(?:/[^\s<>\"']*)?\b",
    re.I
)
PHONE_PAT  = re.compile(r"\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b")
EMAIL_PAT  = re.compile(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", re.I)
MONEY_PAT  = re.compile(r"(?:rs\.?|inr|usd|\$|£|€)\s*[\d,]+|[\d,]+\s*(?:rs\.?|inr|usd)", re.I)
CTA_PAT    = re.compile(
    r"\b(?:call|reply|text|click|visit|go to|open|download|install|dial|verify|verification|update|complete|confirm|pay|submit|claim|login|log in|check|reactivate|unblock|redeem)\b",
    re.I
)
THREAT_PAT = re.compile(
    r"\b(?:arrest(?:ed|ing)?|court|legal|notice[s]?|expir(?:e|ed|ing|y)|suspend(?:ed|ing)?|suspension|block(?:ed|ing|s)?|fine[s]?|penalt(?:y|ies)|warn(?:ing|ed|s)?|bann(?:ed|ing)|terminat(?:ed|ing|ion)?|deactivat(?:ed|ing|ion)?|clos(?:ed|ing|ure)?|freez(?:e|ing|en)|frozen|lock(?:ed|ing)?|seiz(?:ed|ing|ure)?|unauthorized|cancelled|cancellation|disconnect(?:ed|ing|ion)?)\b",
    re.I
)
DATE_PAT   = re.compile(r"\b\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?\b")

def extract_features(text: str) -> dict:
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

    kwh = sum(len(re.findall(r"(?<!\w)" + re.escape(k) + r"(?!\w)", lo)) for k in SCAM_KEYWORDS)

    return {
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
    }

print("Extracting features...")
feat_rows = df["text"].apply(extract_features).tolist()
feat_df   = pd.DataFrame(feat_rows)
feature_names = list(feat_df.columns)
X_num     = feat_df.to_numpy(dtype=np.float32)
y         = df["label_bin"].to_numpy()

# Clean texts before TF-IDF vectorization
cleaned_texts = df["text"].apply(normalize_defanged).tolist()

# 3. Text Vectorizer (FeatureUnion handles word + char in one object)
vectorizer = FeatureUnion([
    ("word", TfidfVectorizer(max_features=2500, ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
    ("char", TfidfVectorizer(max_features=1500, analyzer="char_wb", ngram_range=(3, 4), min_df=3, sublinear_tf=True))
])

print("Fitting FeatureUnion vectorizer...")
X_tfidf = vectorizer.fit_transform(cleaned_texts)
X_num_sp = csr_matrix(X_num)
X_all = hstack([X_tfidf, X_num_sp], format="csr")
print(f"Combined matrix: {X_all.shape} (TF-IDF: {X_tfidf.shape[1]} + Numerical: {X_num.shape[1]})")

# 4. Stratified 5-Fold Cross Validation
print("\nRunning Stratified 5-Fold Cross Validation...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

rf_model = RandomForestClassifier(
    n_estimators=250,
    max_depth=25,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

scores = cross_validate(rf_model, X_all, y, cv=cv, scoring=["accuracy", "precision", "recall", "f1", "roc_auc"])
print(f"  CV Accuracy:  {scores['test_accuracy'].mean():.4f} +/- {scores['test_accuracy'].std():.4f}")
print(f"  CV Precision: {scores['test_precision'].mean():.4f} +/- {scores['test_precision'].std():.4f}")
print(f"  CV Recall:    {scores['test_recall'].mean():.4f} +/- {scores['test_recall'].std():.4f}")
print(f"  CV F1:        {scores['test_f1'].mean():.4f} +/- {scores['test_f1'].std():.4f}")
print(f"  CV ROC-AUC:   {scores['test_roc_auc'].mean():.4f} +/- {scores['test_roc_auc'].std():.4f}")

# 5. Fit final model on full dataset
print("\nFitting final production model on full data...")
rf_model.fit(X_all, y)

# 6. Save artifacts
print("Saving artifacts...")
joblib.dump(rf_model, MODELS_OUT / "sms_rf_model.pkl", compress=3)
joblib.dump(vectorizer, MODELS_OUT / "sms_tfidf_vectorizer.pkl", compress=3)

metadata = {
    "version": "2.2.0",
    "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    "model_type": "RandomForestClassifier",
    "total_samples": len(df),
    "spam_samples": int(df["label_bin"].sum()),
    "ham_samples": int((1 - df["label_bin"]).sum()),
    "total_features": int(X_all.shape[1]),
    "tfidf_features": int(X_tfidf.shape[1]),
    "numerical_features": int(X_num.shape[1]),
    "feature_columns": feature_names,
    "cv_results": {
        "accuracy": float(scores["test_accuracy"].mean()),
        "accuracy_std": float(scores["test_accuracy"].std()),
        "f1": float(scores["test_f1"].mean()),
        "recall": float(scores["test_recall"].mean()),
        "precision": float(scores["test_precision"].mean()),
        "roc_auc": float(scores["test_roc_auc"].mean()),
    },
    "scam_keywords": SCAM_KEYWORDS,
}
joblib.dump(metadata, MODELS_OUT / "sms_feature_metadata.pkl", compress=3)

# Deploy to Application/models
joblib.dump(rf_model, APP_MODELS / "sms_rf_model.pkl", compress=3)
joblib.dump(vectorizer, APP_MODELS / "sms_tfidf_vectorizer.pkl", compress=3)
joblib.dump(metadata, APP_MODELS / "sms_feature_metadata.pkl", compress=3)

# Also write evaluation report
report = {
    "model": "ScamShield SMS Scam Detector v2.2.0",
    "total_samples": len(df),
    "evaluation_methodology": "5-Fold Stratified Cross-Validation",
    "metrics": {
        "cv_accuracy_mean": float(scores["test_accuracy"].mean()),
        "cv_accuracy_std": float(scores["test_accuracy"].std()),
        "cv_f1_score": float(scores["test_f1"].mean()),
        "cv_recall": float(scores["test_recall"].mean()),
        "cv_precision": float(scores["test_precision"].mean()),
        "cv_roc_auc": float(scores["test_roc_auc"].mean()),
    },
    "note": "Production model calibrated with class balancing, defanged link normalization, modern Indian & global smishing vectors, and stratified validation."
}
with open(REPORTS_OUT / "sms_evaluation_v2.json", "w") as f:
    json.dump(report, f, indent=4)

print("SUCCESS: SMS Model retraining and deployment complete!")
