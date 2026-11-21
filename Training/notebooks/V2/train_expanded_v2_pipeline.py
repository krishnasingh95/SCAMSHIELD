"""
ScamShield V2 -- Expanded Multi-Dataset URL Training Pipeline
=============================================================
Integrates 7 major peer-reviewed benchmark datasets:
1. PhiUSIIL Phishing URL Dataset (V1) (235,370 URLs)
2. URL-Phish V2 (Mendeley 10.17632/65z9twcx3r.2) (116,600 URLs)
3. LegitPhish V2 (Mendeley 10.17632/hx4m73v2sf.2) (101,219 URLs - inverted & quarantined)
4. CompPhish V4 (Mendeley 10.17632/fmbs4kp9wz.4) (15,358 URLs)
5. Phishing URL Dataset (Mendeley 10.17632/3jddhy2f6s.1) (149,726 URLs)
6. Web Page Phishing Detection (Mendeley 10.17632/c2gw7fy2j4.3) (11,430 URLs)
7. MURL Large-Scale Dataset (Mendeley 10.17632/5fk24y4xmg.2) (783,705 URLs)

Total raw pool: > 1,400,000 URLs
"""

import sys
import os
import json
import shutil
import hashlib
import warnings
import time
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report, roc_auc_score
)
from urllib.parse import urlsplit
import re
import ipaddress

warnings.filterwarnings("ignore")

# --- Directory Paths ---
ROOT         = r"C:\Users\x1605\AI_Projects\ScamShield"
EXT_BASE     = r"C:\Users\x1605\AI_Projects\ScamShield\Training\datasets\V2\raw\external"
PROCESSED_V2 = r"C:\Users\x1605\AI_Projects\ScamShield\Training\datasets\V2\processed"
PROCESSED_V1 = r"C:\Users\x1605\AI_Projects\ScamShield\Training\datasets\processed"
MODELS_V2    = r"C:\Users\x1605\AI_Projects\ScamShield\Training\Models\V2"
MODELS_ROOT  = r"C:\Users\x1605\AI_Projects\ScamShield\Training\Models"
APP_MODELS   = r"C:\Users\x1605\AI_Projects\ScamShield\Application\models"
REPORTS_V2   = r"C:\Users\x1605\AI_Projects\ScamShield\Training\Reports\V2"
METADATA_V2  = r"C:\Users\x1605\AI_Projects\ScamShield\Training\datasets\V2\metadata"

print("=" * 75)
print("ScamShield V2 -- Expanded Multi-Dataset Training Pipeline (7 Datasets)")
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print("=" * 75)

# --- Feature Extraction Definition ---
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "pw"
}
BRAND_KEYWORDS = [
    "paypal", "google", "amazon", "apple", "microsoft",
    "facebook", "instagram", "whatsapp", "netflix", "sbi",
    "hdfc", "icici", "axisbank", "paytm", "phonepe", "visa"
]

FEATURE_COLS = [
    "url_length", "domain_length", "path_length", "query_length",
    "num_subdomains", "has_ip_address", "has_https", "has_suspicious_tld",
    "num_special_chars", "num_digits_in_domain", "has_brand_keyword",
    "brand_in_subdomain", "has_redirect", "path_depth",
]

def extract_url_features_fast(url: str):
    url = str(url).strip()
    candidate = url
    if candidate.startswith("//"):
        candidate = "http:" + candidate
    elif not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = "http://" + candidate
    try:
        parsed = urlsplit(candidate)
    except Exception:
        return None
    domain = (parsed.hostname or "").lower().rstrip(".")
    try:
        ipaddress.ip_address(domain)
        has_ip = 1
    except ValueError:
        has_ip = 0
    tld = "" if (has_ip or "." not in domain) else domain.rsplit(".", 1)[-1]
    domain_parts = domain.split(".") if domain else []
    return (
        len(url),
        len(domain),
        len(parsed.path),
        len(parsed.query),
        max(domain.count("."), 0),
        has_ip,
        int(parsed.scheme.lower() == "https"),
        int(tld in SUSPICIOUS_TLDS),
        sum(c in "-_@!%" for c in url),
        sum(c.isdigit() for c in domain),
        int(any(b in domain for b in BRAND_KEYWORDS)),
        int(len(domain_parts) > 2 and any(b in domain_parts[0] for b in BRAND_KEYWORDS)),
        int("redirect" in url.lower() or "url=" in url.lower()),
        parsed.path.count("/"),
    )

# ==============================================================================
# PHASE 1: LOAD EXISTING 4-DATASET FEATURES MASTER
# ==============================================================================
print("\n" + "-" * 75)
print("PHASE 1: Loading Previously Processed Masterset")
print("-" * 75)

master_prev_path = os.path.join(PROCESSED_V2, "url_v2_features_master.csv")
df_existing = pd.read_csv(master_prev_path, low_memory=False)
print(f"Loaded existing master: {len(df_existing):,} URLs")
print(f"Sources in existing master:\n{df_existing['source'].value_counts().to_string()}")

existing_urls = set(df_existing["URL"].astype(str).str.strip())
print(f"Unique URLs already processed: {len(existing_urls):,}")

# ==============================================================================
# PHASE 2: LOAD & PROCESS 3 NEW DATASETS
# ==============================================================================
print("\n" + "-" * 75)
print("PHASE 2: Ingesting 3 Additional Mendeley Datasets")
print("-" * 75)

new_url_records = []

# --- Dataset 5: Phishing_URL_3jddhy2f6s ---
# Columns: URL, Label (0: Legitimate -> SAFE, 1: Phishing -> PHISHING)
print("\n[5/7] Processing Phishing_URL_3jddhy2f6s (dataset2.csv)...")
p_3j = os.path.join(EXT_BASE, "Phishing_URL_3jddhy2f6s", "dataset2.csv")
df_3j = pd.read_csv(p_3j, usecols=["URL", "Label"], low_memory=False)
df_3j = df_3j.dropna(subset=["URL", "Label"])
df_3j["URL"] = df_3j["URL"].astype(str).str.strip()
df_3j = df_3j[df_3j["URL"] != ""]
df_3j["Label"] = df_3j["Label"].astype(int)
df_3j["source"] = "Phishing_URL_3jddhy2f6s"
df_3j = df_3j.drop_duplicates(subset=["URL"])
print(f"  Clean unique URLs: {len(df_3j):,} | Class balance: {df_3j['Label'].value_counts().to_dict()}")
new_url_records.append(df_3j.rename(columns={"Label": "target"}))

# --- Dataset 6: WebPage_Phishing_c2gw7fy2j4 ---
# Columns: url, status ('legitimate' -> SAFE (0), 'phishing' -> PHISHING (1))
print("\n[6/7] Processing WebPage_Phishing_c2gw7fy2j4 (dataset_B_05_2020.csv)...")
p_c2 = os.path.join(EXT_BASE, "WebPage_Phishing_c2gw7fy2j4", "dataset_B_05_2020.csv")
df_c2 = pd.read_csv(p_c2, usecols=["url", "status"], low_memory=False)
df_c2 = df_c2.dropna(subset=["url", "status"])
df_c2["url"] = df_c2["url"].astype(str).str.strip()
df_c2 = df_c2[df_c2["url"] != ""]
df_c2["target"] = df_c2["status"].map({"legitimate": 0, "phishing": 1})
df_c2 = df_c2.dropna(subset=["target"])
df_c2["target"] = df_c2["target"].astype(int)
df_c2["source"] = "WebPage_Phishing_c2gw7fy2j4"
df_c2 = df_c2.rename(columns={"url": "URL"})[["URL", "target", "source"]]
df_c2 = df_c2.drop_duplicates(subset=["URL"])
print(f"  Clean unique URLs: {len(df_c2):,} | Class balance: {df_c2['target'].value_counts().to_dict()}")
new_url_records.append(df_c2)

# --- Dataset 7: MURL_5fk24y4xmg ---
# Columns: url, type ('benign'/'legitimate' -> 0, 'phishing'/'malware'/'defacement' -> 1)
print("\n[7/7] Processing MURL_5fk24y4xmg (Malicious_URL_Detection.csv)...")
p_5f = os.path.join(EXT_BASE, "MURL_5fk24y4xmg", "Malicious_URL_Detection.csv")
df_5f = pd.read_csv(p_5f, usecols=["url", "type"], low_memory=False)
df_5f = df_5f.dropna(subset=["url", "type"])
df_5f["url"] = df_5f["url"].astype(str).str.strip()
df_5f = df_5f[df_5f["url"] != ""]

# Standard mapping: benign/legitimate -> SAFE (0), phishing/defacement/malware/spam -> PHISHING (1)
type_map = {
    "benign": 0,
    "legitimate": 0,
    "phishing": 1,
    "defacement": 1,
    "malware": 1,
    "spam": 1,
    "Exploit": 1
}
df_5f["target"] = df_5f["type"].map(type_map)
df_5f = df_5f.dropna(subset=["target"])
df_5f["target"] = df_5f["target"].astype(int)
df_5f["source"] = "MURL_5fk24y4xmg"
df_5f = df_5f.rename(columns={"url": "URL"})[["URL", "target", "source"]]
df_5f = df_5f.drop_duplicates(subset=["URL"])
print(f"  Clean unique URLs: {len(df_5f):,} | Class balance: {df_5f['target'].value_counts().to_dict()}")
new_url_records.append(df_5f)

# Combine new candidates
df_new_all = pd.concat(new_url_records, ignore_index=True)
print(f"\nTotal new external candidates: {len(df_new_all):,}")

# Filter out URLs that are already in the existing master
df_new_unseen = df_new_all[~df_new_all["URL"].isin(existing_urls)].copy()
df_new_unseen = df_new_unseen.drop_duplicates(subset=["URL"], keep="first").reset_index(drop=True)
print(f"Unseen new URLs to extract features for: {len(df_new_unseen):,}")

# Extract features for new unseen URLs
print("\nExtracting features for unseen URLs...")
t0 = time.time()
feat_rows = []
valid_idx = []

for idx, url in enumerate(df_new_unseen["URL"]):
    feats = extract_url_features_fast(url)
    if feats is not None:
        feat_rows.append(feats)
        valid_idx.append(idx)

dt = time.time() - t0
print(f"Feature extraction completed in {dt:.1f}s ({len(feat_rows)/max(dt,0.01):.0f} URLs/sec).")

df_new_extracted = pd.DataFrame(feat_rows, columns=FEATURE_COLS)
df_new_extracted["URL"] = df_new_unseen.iloc[valid_idx]["URL"].values
df_new_extracted["target"] = df_new_unseen.iloc[valid_idx]["target"].values
df_new_extracted["source"] = df_new_unseen.iloc[valid_idx]["source"].values

# Combine with existing master
cols_master = ["URL", "target", "source"] + FEATURE_COLS
df_grand_master = pd.concat([df_existing[cols_master], df_new_extracted[cols_master]], ignore_index=True)
df_grand_master = df_grand_master.drop_duplicates(subset=["URL"], keep="first").reset_index(drop=True)

print("\n" + "=" * 75)
print("GRAND MASTER DATASET STATISTICS (7 Unified Datasets)")
print("=" * 75)
print(f"Total Unique URLs: {len(df_grand_master):,}")
vc = df_grand_master["target"].value_counts()
print(f"Class 0 (SAFE)    : {vc.get(0, 0):,} ({vc.get(0, 0)/len(df_grand_master)*100:.2f}%)")
print(f"Class 1 (PHISHING): {vc.get(1, 0):,} ({vc.get(1, 0)/len(df_grand_master)*100:.2f}%)")
print("\nDistribution by Dataset Source:")
print(df_grand_master["source"].value_counts().to_string())

# Save grand master dataset
grand_master_path = os.path.join(PROCESSED_V2, "url_v2_features_master.csv")
df_grand_master.to_csv(grand_master_path, index=False)
print(f"\nSaved updated grand master dataset: {grand_master_path}")

# ==============================================================================
# PHASE 3: MODEL TRAINING (RANDOM FOREST V2 EXPANDED)
# ==============================================================================
print("\n" + "-" * 75)
print("PHASE 3: Model Training on 7 Unified Datasets")
print("-" * 75)

X = df_grand_master[FEATURE_COLS].values.astype(np.float32)
y = df_grand_master["target"].values.astype(int)

# Stratified 80/20 train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train):,} | Testing samples: {len(X_test):,}")
print(f"Train Class Balance: SAFE={(y_train==0).sum():,} | PHISHING={(y_train==1).sum():,}")
print(f"Test Class Balance:  SAFE={(y_test==0).sum():,} | PHISHING={(y_test==1).sum():,}")

print("\nFitting Random Forest Classifier:")
print("  n_estimators = 200")
print("  max_depth = 30")
print("  min_samples_leaf = 2")
print("  class_weight = 'balanced'")
print("  n_jobs = -1")
print("  random_state = 42")

t_train_start = time.time()
rf_expanded = RandomForestClassifier(
    n_estimators=200,
    max_depth=30,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)
rf_expanded.fit(X_train, y_train)
t_train_elapsed = time.time() - t_train_start
print(f"Model fitting completed in {t_train_elapsed:.2f} seconds.")

# ==============================================================================
# PHASE 4: EVALUATION
# ==============================================================================
print("\n" + "-" * 75)
print("PHASE 4: Comprehensive Model Evaluation")
print("-" * 75)

y_pred = rf_expanded.predict(X_test)
y_prob = rf_expanded.predict_proba(X_test)[:, 1]

acc  = float(accuracy_score(y_test, y_pred))
prec = float(precision_score(y_test, y_pred))
rec  = float(recall_score(y_test, y_pred))
f1   = float(f1_score(y_test, y_pred))
auc  = float(roc_auc_score(y_test, y_prob))
cm   = confusion_matrix(y_test, y_pred).tolist()

print(f"\n{'Evaluation Metric':<24} {'V2 Expanded Score':<18}")
print("-" * 42)
print(f"{'Accuracy':<24} {acc:.6f} ({acc*100:.2f}%)")
print(f"{'Precision':<24} {prec:.6f} ({prec*100:.2f}%)")
print(f"{'Recall':<24} {rec:.6f} ({rec*100:.2f}%)")
print(f"{'F1-Score':<24} {f1:.6f} ({f1*100:.2f}%)")
print(f"{'ROC-AUC':<24} {auc:.6f} ({auc*100:.2f}%)")

print("\nConfusion Matrix (Holdout Test Set):")
print(f"  True Negatives  (SAFE correctly predicted)    : {cm[0][0]:,}")
print(f"  False Positives (SAFE mispredicted as PHISH) : {cm[0][1]:,}")
print(f"  False Negatives (PHISH mispredicted as SAFE) : {cm[1][0]:,}")
print(f"  True Positives  (PHISH correctly predicted)  : {cm[1][1]:,}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=["SAFE", "PHISHING"], digits=4))

# Feature importances
importances = rf_expanded.feature_importances_
feat_ranks = sorted(zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True)
print("\nFeature Importance Rankings:")
for name, imp in feat_ranks:
    print(f"  {name:<25}: {imp:.4f} ({imp*100:.2f}%)")

# ==============================================================================
# PHASE 5: MODEL DEPLOYMENT & METADATA EXPORT
# ==============================================================================
print("\n" + "-" * 75)
print("PHASE 5: Model Deployment & Metadata Export")
print("-" * 75)

# Save to Training/Models/V2/
v2_model_path = os.path.join(MODELS_V2, "url_v2_rf_model.pkl")
joblib.dump(rf_expanded, v2_model_path, compress=3)
print(f"Saved expanded model to: {v2_model_path}")

# Deploy to Application/models/
app_model_path = os.path.join(APP_MODELS, "url_rf_model.pkl")
app_meta_path  = os.path.join(APP_MODELS, "url_feature_metadata.json")
shutil.copy2(v2_model_path, app_model_path)
print(f"Deployed model to Application: {app_model_path}")

# Also update root Training/Models
training_root_model_path = os.path.join(MODELS_ROOT, "url_rf_model.pkl")
shutil.copy2(v2_model_path, training_root_model_path)

# Compute SHA256 of deployed model
sha256_hash = hashlib.sha256()
with open(app_model_path, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        sha256_hash.update(chunk)
model_sha256 = sha256_hash.hexdigest()

DATASET_NAMES = [
    "PhiUSIIL Phishing URL Dataset (V1)",
    "URL-Phish Dataset V2 (Mendeley 10.17632/65z9twcx3r.2)",
    "LegitPhish Dataset V2 (Mendeley 10.17632/hx4m73v2sf.2)",
    "CompPhish Dataset V4 (Mendeley 10.17632/fmbs4kp9wz.4)",
    "Phishing URL Dataset (Mendeley 10.17632/3jddhy2f6s.1)",
    "Web Page Phishing Detection (Mendeley 10.17632/c2gw7fy2j4.3)",
    "MURL Large-Scale Malicious URL Dataset (Mendeley 10.17632/5fk24y4xmg.2)"
]

metadata_dict = {
    "model_version": "2.1.0",
    "model_name": "ScamShield URL Phishing Classifier V2-Expanded (7 Datasets)",
    "algorithm": "RandomForestClassifier",
    "feature_columns": FEATURE_COLS,
    "suspicious_tlds": sorted(list(SUSPICIOUS_TLDS)),
    "brand_keywords": BRAND_KEYWORDS,
    "label_mapping": {
        "SAFE": 0,
        "PHISHING": 1
    },
    "total_features": len(FEATURE_COLS),
    "n_estimators": 200,
    "max_depth": 30,
    "class_weight": "balanced",
    "random_state": 42,
    "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    "training_samples": len(X_train),
    "testing_samples": len(X_test),
    "total_samples": len(df_grand_master),
    "accuracy": acc,
    "precision": prec,
    "recall": rec,
    "f1_score": f1,
    "roc_auc": auc,
    "model_sha256": model_sha256,
    "datasets": DATASET_NAMES,
    "source_distribution": df_grand_master["source"].value_counts().to_dict()
}

with open(app_meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata_dict, f, indent=4)
print(f"Updated application metadata at: {app_meta_path}")

training_root_meta_path = os.path.join(MODELS_ROOT, "url_feature_metadata.json")
with open(training_root_meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata_dict, f, indent=4)

# Save Evaluation Report in Training/Reports/V2/
report_data = {
    "project": "ScamShield",
    "version": "2.1.0",
    "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    "evaluation_metrics": {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": auc
    },
    "confusion_matrix": cm,
    "feature_importances": {k: float(v) for k, v in feat_ranks},
    "total_training_records": len(df_grand_master),
    "test_samples": len(X_test),
    "model_sha256": model_sha256,
    "datasets_used": DATASET_NAMES,
    "source_distribution": df_grand_master["source"].value_counts().to_dict()
}

report_json_path = os.path.join(REPORTS_V2, "url_v2_evaluation.json")
with open(report_json_path, "w", encoding="utf-8") as f:
    json.dump(report_data, f, indent=4)
print(f"Saved evaluation report to: {report_json_path}")

print("\n" + "=" * 75)
print("EXPANDED V2 TRAINING & DEPLOYMENT COMPLETED")
print(f"Total Master URLs Trained: {len(df_grand_master):,}")
print(f"Final Model Accuracy:      {acc:.4%}")
print(f"Final Model ROC-AUC:       {auc:.4%}")
print(f"Final Model F1-Score:      {f1:.4%}")
print("=" * 75)
