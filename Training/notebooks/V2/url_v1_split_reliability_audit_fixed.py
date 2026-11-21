"""
Read-only reliability audit for the existing ScamShield V1 URL model.

Run from the ScamShield project root:
    python Training/notebooks/V2/url_v1_split_reliability_audit.py

This script does NOT train, overwrite, or modify the model or dataset.
It recreates the notebook's 80/20 stratified row split (random_state=42),
then evaluates the saved model on both partitions and reports possible
row-level split overlap by hostname and fragment-insensitive URL.
"""

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import json
import sys

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

ROOT = Path.cwd()
DATA_PATH = ROOT / "Training" / "datasets" / "processed" / "url_features_14.csv"
MODEL_PATH = ROOT / "Training" / "Models" / "url_rf_model.pkl"
META_PATH = ROOT / "Training" / "Models" / "url_feature_metadata.json"

def stop(message: str) -> None:
    print(f"\nERROR: {message}")
    sys.exit(1)

def hostname_of(url: str) -> str:
    value = str(url).strip()
    candidate = value if "://" in value else "http://" + value
    try:
        return (urlsplit(candidate).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""

def normalize_without_fragment(url: str) -> str:
    """Diagnostic key only: lowercase scheme/host, remove fragment."""
    value = str(url).strip()
    candidate = value if "://" in value else "http://" + value
    try:
        parts = urlsplit(candidate)
        scheme = parts.scheme.lower()
        host = (parts.hostname or "").lower().rstrip(".")
        if not host:
            return value.lower().split("#", 1)[0]
        # Preserve a non-default port; avoid reconstructing userinfo.
        try:
            port = parts.port
        except ValueError:
            port = None
        netloc = host if port is None else f"{host}:{port}"
        return urlunsplit((scheme, netloc, parts.path, parts.query, ""))
    except ValueError:
        return value.lower().split("#", 1)[0]

def metrics_block(name, model, X, y):
    pred = model.predict(X)
    result = {
        "accuracy": accuracy_score(y, pred),
        "precision_phishing": precision_score(y, pred, pos_label=1, zero_division=0),
        "recall_phishing": recall_score(y, pred, pos_label=1, zero_division=0),
        "f1_phishing": f1_score(y, pred, pos_label=1, zero_division=0),
        "confusion_matrix_labels_0_1": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
    }
    print(f"\n=== {name} ===")
    print(f"Accuracy          : {result['accuracy']:.6%}")
    print(f"Precision PHISHING: {result['precision_phishing']:.6%}")
    print(f"Recall PHISHING   : {result['recall_phishing']:.6%}")
    print(f"F1 PHISHING       : {result['f1_phishing']:.6%}")
    print("Confusion matrix (rows=actual [SAFE, PHISHING], columns=predicted [SAFE, PHISHING]):")
    print(result["confusion_matrix_labels_0_1"])
    return result

def main():
    print("ScamShield V1 URL Model — READ-ONLY SPLIT RELIABILITY AUDIT")
    print(f"Project root: {ROOT}")

    for path in (DATA_PATH, MODEL_PATH, META_PATH):
        if not path.exists():
            stop(f"Required file not found: {path}")

    df = pd.read_csv(DATA_PATH)
    with META_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)
    model = joblib.load(MODEL_PATH)

    features = metadata.get("feature_columns", [])
    if len(features) != 14:
        stop(f"Expected 14 feature columns in metadata, found {len(features)}.")
    missing = [col for col in features + ["URL", "target"] if col not in df.columns]
    if missing:
        stop(f"Dataset is missing required columns: {missing}")

    if hasattr(model, "feature_names_in_"):
        model_feature_names = list(model.feature_names_in_)
        print("Model feature names match metadata:",
              model_feature_names == features)
    else:
        print("Model has no feature_names_in_ attribute; checked feature count only.")

    if getattr(model, "n_features_in_", None) != len(features):
        stop("Saved model feature count does not match metadata.")

    X = df[features]
    y = df["target"].astype(int)
    if set(y.unique()) != {0, 1}:
        stop(f"Unexpected target labels: {sorted(y.unique())}")

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=0.20, random_state=42, stratify=y
    )

    print(f"\nDataset rows       : {len(df):,}")
    print(f"Training rows      : {len(X_train):,}")
    print(f"Testing rows       : {len(X_test):,}")
    print(f"Saved model trees  : {getattr(model, 'n_estimators', 'unknown')}")
    print(f"Saved model classes: {getattr(model, 'classes_', 'unknown')}")

    train_result = metrics_block("TRAIN PARTITION (same notebook split recipe)", model, X_train, y_train)
    test_result = metrics_block("TEST PARTITION (same notebook split recipe)", model, X_test, y_test)

    print("\n=== TRAIN-TEST GAP ===")
    gap = train_result["accuracy"] - test_result["accuracy"]
    print(f"Train accuracy - test accuracy: {gap:.6%}")
    print("Note: a small gap alone does not prove good generalization; the split is row-random.")

    train_urls = df.loc[idx_train, "URL"].astype(str)
    test_urls = df.loc[idx_test, "URL"].astype(str)

    train_hosts = {hostname_of(u) for u in train_urls if hostname_of(u)}
    test_hosts = {hostname_of(u) for u in test_urls if hostname_of(u)}
    shared_hosts = train_hosts & test_hosts

    train_norm = {normalize_without_fragment(u) for u in train_urls}
    test_norm = {normalize_without_fragment(u) for u in test_urls}
    shared_norm = train_norm & test_norm

    print("\n=== POSSIBLE ROW-SPLIT OVERLAP ===")
    print(f"Unique hostnames in train : {len(train_hosts):,}")
    print(f"Unique hostnames in test  : {len(test_hosts):,}")
    print(f"Hostnames in BOTH splits  : {len(shared_hosts):,}")
    print(f"Normalized URLs in BOTH splits (fragment removed): {len(shared_norm):,}")
    print("These are overlap indicators, not proof that every shared hostname is leakage.")

    print("\n=== CLASS DISTRIBUTION ===")
    print("Train:", y_train.value_counts().sort_index().to_dict(), "(0=SAFE, 1=PHISHING)")
    print("Test :", y_test.value_counts().sort_index().to_dict(), "(0=SAFE, 1=PHISHING)")

    print("\nRead-only audit complete. No source dataset, model, metadata, notebook, or application file was modified.")

if __name__ == "__main__":
    main()
