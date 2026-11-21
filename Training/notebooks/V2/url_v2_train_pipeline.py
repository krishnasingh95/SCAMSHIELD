"""
ScamShield V2 -- URL Model Training Pipeline
=============================================
Phase 1: Preprocess all three external datasets + V1 PhiUSIIL
Phase 2: Extract 14 structural features matching V1 exact schema
Phase 3: Train class-balanced Random Forest (200 trees)
Phase 4: Evaluate, compare against V1, export metrics & reports
Phase 5: Safely deploy V2 model and metadata to Application/

SAFETY:
- Original downloaded files in Training/datasets/V2/raw/ are NEVER modified.
- V1 model files are backed up to Application/models/*_v1_backup.*
- All output prints strictly ASCII-safe for Windows command line.
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
V1_RAW       = r"C:\Users\x1605\AI_Projects\ScamShield\Training\datasets\raw"

for d in [PROCESSED_V2, MODELS_V2, REPORTS_V2, METADATA_V2]:
    os.makedirs(d, exist_ok=True)

print("=" * 70)
print("ScamShield V2 -- URL Model Training Pipeline")
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print("=" * 70)

# --- Feature Extraction Definition (Exact match to V1 Application schema) ---
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
    """Extract the exact 14 features required by ScamShield."""
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
# PHASE 1: LOAD, AUDIT, AND MAP EXTERNAL DATASETS
# ==============================================================================
print("\n" + "-" * 70)
print("PHASE 1: Loading and Preprocessing Datasets")
print("-" * 70)

preprocessing_log = {}

# 1. URL_Phish_V2
# Label mapping: 0 = Benign (SAFE: 0), 1 = Phishing (PHISHING: 1)
print("\n[1/4] Processing URL_Phish_V2...")
path_up = os.path.join(EXT_BASE, "URL_Phish_V2", "Dataset.csv")
df_up = pd.read_csv(path_up, usecols=["url", "label"], low_memory=False)
raw_up_len = len(df_up)
df_up = df_up.dropna(subset=["url", "label"])
df_up["url"] = df_up["url"].astype(str).str.strip()
df_up = df_up[df_up["url"] != ""]
df_up = df_up.drop_duplicates(subset=["url"])
df_up["label"] = df_up["label"].astype(int)
df_up["source"] = "URL_Phish_V2"
clean_up_len = len(df_up)
print(f"  Raw: {raw_up_len:,} -> Clean: {clean_up_len:,} (removed {raw_up_len - clean_up_len:,})")
print(f"  Class Distribution: {df_up['label'].value_counts().to_dict()} (0=SAFE, 1=PHISHING)")
preprocessing_log["URL_Phish_V2"] = {
    "raw_records": raw_up_len,
    "clean_records": clean_up_len,
    "class_distribution": df_up["label"].value_counts().to_dict(),
    "mapping": "0->0 (SAFE), 1->1 (PHISHING) [No inversion]"
}

# 2. LegitPhish_V2
# Label mapping: 0 = Phishing (PHISHING: 1), 1 = Legitimate (SAFE: 0) -> INVERSION
print("\n[2/4] Processing LegitPhish_V2...")
path_lp = os.path.join(EXT_BASE, "LegitPhish_V2", "url_features_extracted1.csv")
df_lp = pd.read_csv(path_lp, usecols=["URL", "ClassLabel"], low_memory=False)
raw_lp_len = len(df_lp)
df_lp = df_lp.dropna(subset=["URL", "ClassLabel"])
df_lp["URL"] = df_lp["URL"].astype(str).str.strip()
df_lp = df_lp[df_lp["URL"] != ""]
df_lp = df_lp.drop_duplicates(subset=["URL"])
# CRITICAL: Invert label: 0 (Phishing) -> 1, 1 (Legitimate) -> 0
df_lp["label"] = df_lp["ClassLabel"].apply(lambda x: 1 if int(x) == 0 else 0)
df_lp = df_lp.rename(columns={"URL": "url"})
df_lp = df_lp[["url", "label"]]
dedup_lp_len = len(df_lp)

# Quarantine overlap with V1 PhiUSIIL dataset
v1_features_path = os.path.join(PROCESSED_V1, "url_features_14.csv")
df_v1_existing = pd.read_csv(v1_features_path, usecols=["URL"], low_memory=False)
v1_url_set = set(df_v1_existing["URL"].astype(str).str.strip())
overlap_mask = df_lp["url"].isin(v1_url_set)
overlap_count = int(overlap_mask.sum())
df_lp_quarantine = df_lp[overlap_mask].copy()
df_lp_clean = df_lp[~overlap_mask].copy()
clean_lp_len = len(df_lp_clean)
df_lp_clean["source"] = "LegitPhish_V2"

# Save quarantine file for auditing
quarantine_path = os.path.join(PROCESSED_V2, "legitphish_v1_overlap_quarantine.csv")
df_lp_quarantine.to_csv(quarantine_path, index=False)

print(f"  Raw: {raw_lp_len:,} -> Dedup: {dedup_lp_len:,}")
print(f"  Quarantined V1 Overlap: {overlap_count:,} saved to {os.path.basename(quarantine_path)}")
print(f"  Clean Non-overlapping: {clean_lp_len:,}")
print(f"  Class Distribution: {df_lp_clean['label'].value_counts().to_dict()} (0=SAFE, 1=PHISHING)")
preprocessing_log["LegitPhish_V2"] = {
    "raw_records": raw_lp_len,
    "dedup_records": dedup_lp_len,
    "quarantined_v1_overlap": overlap_count,
    "clean_records": clean_lp_len,
    "class_distribution": df_lp_clean["label"].value_counts().to_dict(),
    "mapping": "0->1 (PHISHING), 1->0 (SAFE) [INVERTED]"
}

# 3. CompPhish_V4
# Label mapping: 0 = Legitimate (SAFE: 0), 1 = Phishing (PHISHING: 1)
print("\n[3/4] Processing CompPhish_V4...")
path_cp = os.path.join(EXT_BASE, "CompPhish_V4", "Mapping_File.xlsx")
df_cp = pd.read_excel(path_cp, usecols=["url", "label"])
raw_cp_len = len(df_cp)
df_cp = df_cp.dropna(subset=["url", "label"])
df_cp["url"] = df_cp["url"].astype(str).str.strip()
df_cp = df_cp[df_cp["url"] != ""]
df_cp = df_cp.drop_duplicates(subset=["url"])
df_cp["label"] = df_cp["label"].astype(int)
df_cp["source"] = "CompPhish_V4"
clean_cp_len = len(df_cp)
print(f"  Raw: {raw_cp_len:,} -> Clean: {clean_cp_len:,}")
print(f"  Class Distribution: {df_cp['label'].value_counts().to_dict()} (0=SAFE, 1=PHISHING)")
preprocessing_log["CompPhish_V4"] = {
    "raw_records": raw_cp_len,
    "clean_records": clean_cp_len,
    "class_distribution": df_cp["label"].value_counts().to_dict(),
    "mapping": "0->0 (SAFE), 1->1 (PHISHING) [No inversion]"
}

# 4. Combine New Datasets & Extract Features
print("\n[4/4] Combining New External Datasets and Extracting Features...")
df_new = pd.concat([df_up[["url", "label", "source"]],
                    df_lp_clean[["url", "label", "source"]],
                    df_cp[["url", "label", "source"]]], ignore_index=True)

# Remove internal cross-duplicates within new datasets (keep first)
before_new_dedup = len(df_new)
df_new = df_new.drop_duplicates(subset=["url"], keep="first")
after_new_dedup = len(df_new)
print(f"  New combined URLs: {before_new_dedup:,} -> After internal dedup: {after_new_dedup:,}")

# Extract features
print(f"  Extracting 14 features for {len(df_new):,} external URLs...")
t0 = time.time()
feat_rows = []
valid_indices = []

for idx, (url, lbl, src) in enumerate(zip(df_new["url"], df_new["label"], df_new["source"])):
    feats = extract_url_features_fast(url)
    if feats is not None:
        feat_rows.append(feats)
        valid_indices.append(idx)

dt = time.time() - t0
print(f"  Extraction done in {dt:.1f}s ({len(feat_rows)/max(dt,0.01):.0f} URLs/sec).")

df_new_features = pd.DataFrame(feat_rows, columns=FEATURE_COLS)
df_new_valid = df_new.iloc[valid_indices].reset_index(drop=True)
df_new_features["URL"] = df_new_valid["url"]
df_new_features["target"] = df_new_valid["label"].astype(int)
df_new_features["source"] = df_new_valid["source"]

# 5. Load V1 Feature Dataset (PhiUSIIL)
print("\nLoading V1 Feature Dataset (PhiUSIIL)...")
df_v1 = pd.read_csv(v1_features_path, low_memory=False)
df_v1["source"] = "PhiUSIIL_V1"
print(f"  V1 pre-extracted records: {len(df_v1):,}")
print(f"  V1 class distribution: {df_v1['target'].value_counts().to_dict()}")

# Align columns
cols_to_use = ["URL", "target", "source"] + FEATURE_COLS
df_all = pd.concat([df_v1[cols_to_use], df_new_features[cols_to_use]], ignore_index=True)
print(f"\nTotal combined records before final deduplication: {len(df_all):,}")

# Final Deduplication across all datasets (PhiUSIIL + 3 new)
before_master = len(df_all)
df_all = df_all.drop_duplicates(subset=["URL"], keep="first").reset_index(drop=True)
after_master = len(df_all)
print(f"Master unique records: {before_master:,} -> {after_master:,} (removed {before_master - after_master:,} dups)")

print("\nFinal Master Dataset Statistics:")
print(f"  Total URLs: {len(df_all):,}")
vc = df_all["target"].value_counts()
print(f"  Class 0 (SAFE)    : {vc.get(0, 0):,} ({vc.get(0, 0)/len(df_all)*100:.2f}%)")
print(f"  Class 1 (PHISHING): {vc.get(1, 0):,} ({vc.get(1, 0)/len(df_all)*100:.2f}%)")
print("\nBreakdown by Source:")
print(df_all["source"].value_counts().to_string())

# Save master dataset
master_csv_path = os.path.join(PROCESSED_V2, "url_v2_features_master.csv")
df_all.to_csv(master_csv_path, index=False)
print(f"\nSaved master processed dataset: {master_csv_path}")

# ==============================================================================
# PHASE 2: MODEL TRAINING (RANDOM FOREST V2)
# ==============================================================================
print("\n" + "-" * 70)
print("PHASE 2: Training Random Forest V2")
print("-" * 70)

X = df_all[FEATURE_COLS].values.astype(np.float32)
y = df_all["target"].values.astype(int)

# 80/20 Stratified Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Train samples: {len(X_train):,} | Test samples: {len(X_test):,}")
print(f"Train class balance: SAFE={int((y_train==0).sum()):,}, PHISHING={int((y_train==1).sum()):,}")
print(f"Test class balance:  SAFE={int((y_test==0).sum()):,}, PHISHING={int((y_test==1).sum()):,}")

print("\nFitting Random Forest Classifier:")
print("  n_estimators = 200")
print("  class_weight = 'balanced'")
print("  min_samples_leaf = 2")
print("  n_jobs = -1")
print("  random_state = 42")

t_train_start = time.time()
rf_v2 = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)
rf_v2.fit(X_train, y_train)
t_train_elapsed = time.time() - t_train_start
print(f"Model fitted successfully in {t_train_elapsed:.2f} seconds.")

# ==============================================================================
# PHASE 3: EVALUATION & COMPARISON
# ==============================================================================
print("\n" + "-" * 70)
print("PHASE 3: Comprehensive Evaluation")
print("-" * 70)

y_pred = rf_v2.predict(X_test)
y_prob = rf_v2.predict_proba(X_test)[:, 1]

acc  = float(accuracy_score(y_test, y_pred))
prec = float(precision_score(y_test, y_pred))
rec  = float(recall_score(y_test, y_pred))
f1   = float(f1_score(y_test, y_pred))
auc  = float(roc_auc_score(y_test, y_prob))
cm   = confusion_matrix(y_test, y_pred).tolist()

V1_ACC = 0.9955814249904406
V1_PREC = 0.9982470199338876
V1_REC = 0.9913947473139674
V1_F1 = 0.9948090841028201

print(f"\n{'Metric':<18} {'V1 Score':<14} {'V2 Score':<14} {'Delta':<12}")
print("-" * 58)
print(f"{'Accuracy':<18} {V1_ACC:.6f}       {acc:.6f}       {acc - V1_ACC:+.6f}")
print(f"{'Precision':<18} {V1_PREC:.6f}       {prec:.6f}       {prec - V1_PREC:+.6f}")
print(f"{'Recall':<18} {V1_REC:.6f}       {rec:.6f}       {rec - V1_REC:+.6f}")
print(f"{'F1-Score':<18} {V1_F1:.6f}       {f1:.6f}       {f1 - V1_F1:+.6f}")
print(f"{'ROC-AUC':<18} {'N/A':<14} {auc:.6f}")

print("\nConfusion Matrix (Test Set):")
print(f"  True Negatives  (SAFE correctly predicted)    : {cm[0][0]:,}")
print(f"  False Positives (SAFE mispredicted as PHISH) : {cm[0][1]:,}")
print(f"  False Negatives (PHISH mispredicted as SAFE) : {cm[1][0]:,}")
print(f"  True Positives  (PHISH correctly predicted)  : {cm[1][1]:,}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=["SAFE", "PHISHING"], digits=4))

# Feature importances
importances = rf_v2.feature_importances_
feat_ranks = sorted(zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True)
print("\nFeature Importance Rankings:")
for name, imp in feat_ranks:
    print(f"  {name:<25}: {imp:.4f} ({imp*100:.2f}%)")

# ==============================================================================
# PHASE 4: ARTIFACT SERIALIZATION & DEPLOYMENT
# ==============================================================================
print("\n" + "-" * 70)
print("PHASE 4: Deployment & Serialization")
print("-" * 70)

# 1. Save V2 model to Training/Models/V2/
v2_training_model_path = os.path.join(MODELS_V2, "url_v2_rf_model.pkl")
joblib.dump(rf_v2, v2_training_model_path, compress=3)
print(f"Saved V2 model to: {v2_training_model_path}")

# 2. Backup V1 model in Application/models/ if not already backed up
app_model_path = os.path.join(APP_MODELS, "url_rf_model.pkl")
app_meta_path  = os.path.join(APP_MODELS, "url_feature_metadata.json")
app_model_bak  = os.path.join(APP_MODELS, "url_rf_model_v1_backup.pkl")
app_meta_bak   = os.path.join(APP_MODELS, "url_feature_metadata_v1_backup.json")

if os.path.exists(app_model_path) and not os.path.exists(app_model_bak):
    shutil.copy2(app_model_path, app_model_bak)
    print(f"Created V1 model backup at: {app_model_bak}")
if os.path.exists(app_meta_path) and not os.path.exists(app_meta_bak):
    shutil.copy2(app_meta_path, app_meta_bak)
    print(f"Created V1 metadata backup at: {app_meta_bak}")

# 3. Deploy V2 model into Application/models/
shutil.copy2(v2_training_model_path, app_model_path)
print(f"Successfully deployed V2 model to: {app_model_path}")

# Also update Training/Models/ copy
training_root_model_path = os.path.join(MODELS_ROOT, "url_rf_model.pkl")
shutil.copy2(v2_training_model_path, training_root_model_path)

# Compute SHA256 of deployed model
sha256_hash = hashlib.sha256()
with open(app_model_path, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        sha256_hash.update(chunk)
model_sha256 = sha256_hash.hexdigest()

# 4. Generate V2 Feature Metadata for Application
metadata_dict = {
    "model_version": "2.0.0",
    "model_name": "ScamShield URL Phishing Classifier V2",
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
    "class_weight": "balanced",
    "random_state": 42,
    "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    "training_samples": len(X_train),
    "testing_samples": len(X_test),
    "total_samples": len(df_all),
    "accuracy": acc,
    "precision": prec,
    "recall": rec,
    "f1_score": f1,
    "roc_auc": auc,
    "model_sha256": model_sha256,
    "datasets": [
        "PhiUSIIL Phishing URL Dataset (V1)",
        "URL-Phish Dataset V2 (Mendeley 10.17632/65z9twcx3r.2)",
        "LegitPhish Dataset V2 (Mendeley 10.17632/hx4m73v2sf.2)",
        "CompPhish Dataset V4 (Mendeley 10.17632/fmbs4kp9wz.4)"
    ],
    "source_distribution": df_all["source"].value_counts().to_dict()
}

with open(app_meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata_dict, f, indent=4)
print(f"Updated application metadata at: {app_meta_path}")

training_root_meta_path = os.path.join(MODELS_ROOT, "url_feature_metadata.json")
with open(training_root_meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata_dict, f, indent=4)

# 5. Generate Evaluation Report in Training/Reports/V2/
report_data = {
    "project": "ScamShield",
    "version": "2.0.0",
    "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    "evaluation_metrics": {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": auc
    },
    "v1_comparison": {
        "v1_accuracy": V1_ACC,
        "v2_accuracy": acc,
        "accuracy_delta": acc - V1_ACC,
        "v1_f1": V1_F1,
        "v2_f1": f1,
        "f1_delta": f1 - V1_F1
    },
    "confusion_matrix": cm,
    "feature_importances": {k: float(v) for k, v in feat_ranks},
    "dataset_provenance": preprocessing_log,
    "total_training_records": len(df_all),
    "test_samples": len(X_test),
    "model_sha256": model_sha256
}

report_json_path = os.path.join(REPORTS_V2, "url_v2_evaluation.json")
with open(report_json_path, "w", encoding="utf-8") as f:
    json.dump(report_data, f, indent=4)
print(f"Saved evaluation report to: {report_json_path}")

print("\n" + "=" * 70)
print("V2 TRAINING & DEPLOYMENT COMPLETED SUCCESSFULLY")
print(f"Final Model Accuracy: {acc:.4%}")
print(f"Final Model F1-Score: {f1:.4%}")
print(f"Final Model ROC-AUC:  {auc:.4%}")
print("=" * 70)
