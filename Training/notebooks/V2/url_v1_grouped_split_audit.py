"""
ScamShield V1 URL Model — Registrable-Domain Grouped Split Audit
READ-ONLY with respect to V1 source data and saved model.

This script trains a temporary in-memory Random Forest on a domain-grouped
80/20-style split to compare with the existing row-random split result.
It does NOT save or overwrite any model, dataset, notebook, or application file.
Only a JSON audit report is written under Training/Reports/V2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import StratifiedGroupKFold


try:
    import tldextract
except ImportError:
    print("ERROR: tldextract is not installed in the scamshield environment.")
    print("Install it with:")
    print("  python -m pip install tldextract")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = ROOT / "Training" / "datasets" / "processed" / "url_features_14.csv"
METADATA_PATH = ROOT / "Training" / "Models" / "url_feature_metadata.json"
REPORT_DIR = ROOT / "Training" / "Reports" / "V2"
REPORT_PATH = REPORT_DIR / "url_v1_grouped_split_audit.json"

# Baseline reproduced by the previous row-random audit using the V1 notebook
# split recipe (80/20, stratify=y, random_state=42).
ROW_RANDOM_BASELINE = {
    "accuracy": 0.99558142,
    "precision_phishing": 0.99824702,
    "recall_phishing": 0.99139475,
    "f1_phishing": 0.99480908,
}

EXPECTED_LABELS = {0, 1}


def registrable_domain(url: str, extractor) -> str:
    """Return registrable domain using the Public Suffix List; fallback to host."""
    value = str(url).strip()
    if not value:
        return ""

    parsed = urlsplit(value)
    if not parsed.hostname:
        parsed = urlsplit("//" + value)

    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return ""

    # Preserve IP addresses and localhost-like hosts as their own groups.
    ext = extractor(host)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower()
    return host


def main() -> int:
    print("=== SCAMSHIELD V1 GROUPED-SPLIT RELIABILITY AUDIT ===")
    print("Loading processed dataset and feature metadata (read-only)...")

    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found: {DATASET_PATH}")
        return 1
    if not METADATA_PATH.exists():
        print(f"ERROR: Feature metadata not found: {METADATA_PATH}")
        return 1

    df = pd.read_csv(DATASET_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    feature_columns = metadata.get("feature_columns", [])

    if not feature_columns:
        print("ERROR: 'feature_columns' is missing or empty in metadata.")
        return 1

    required = {"URL", "target", *feature_columns}
    missing = sorted(required.difference(df.columns))
    if missing:
        print(f"ERROR: Required columns missing from dataset: {missing}")
        return 1

    if df["target"].isna().any():
        print("ERROR: Dataset contains missing target labels.")
        return 1

    y = df["target"].astype(int)
    if set(y.unique()) != EXPECTED_LABELS:
        print(f"ERROR: Expected numeric labels {EXPECTED_LABELS}, found {set(y.unique())}")
        return 1

    X = df[feature_columns].copy()
    if X.isna().any().any():
        print("ERROR: Feature matrix contains missing values.")
        return 1

    # Disable network fetching and include private suffixes (e.g. hosted platforms)
    # so tenant domains are grouped more safely.
    extractor_obj = tldextract.TLDExtract(
        suffix_list_urls=(),
        include_psl_private_domains=True,
    )

    groups = df["URL"].astype(str).map(
        lambda item: registrable_domain(item, extractor_obj)
    )

    if (groups == "").any():
        bad_count = int((groups == "").sum())
        print(f"ERROR: Could not derive a domain group for {bad_count} URLs.")
        return 1

    print(f"Dataset rows: {len(df):,}")
    print(f"Feature count: {len(feature_columns)}")
    print(f"Unique registrable-domain groups: {groups.nunique():,}")
    print(f"Class counts: {y.value_counts().sort_index().to_dict()}")

    # Generate group-disjoint folds. Choose a fold only by test-size and class
    # proportion closeness, never by its model score.
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    overall_positive_rate = float(y.mean())
    candidates = []

    for fold_number, (train_idx, test_idx) in enumerate(
        splitter.split(X, y, groups=groups), start=1
    ):
        test_fraction = len(test_idx) / len(df)
        test_positive_rate = float(y.iloc[test_idx].mean())
        selection_score = (
            abs(test_fraction - 0.20)
            + abs(test_positive_rate - overall_positive_rate)
        )
        candidates.append(
            (selection_score, fold_number, train_idx, test_idx, test_fraction, test_positive_rate)
        )

    _, selected_fold, train_idx, test_idx, test_fraction, test_positive_rate = min(
        candidates, key=lambda item: item[0]
    )

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    groups_train, groups_test = groups.iloc[train_idx], groups.iloc[test_idx]

    overlap = set(groups_train).intersection(set(groups_test))
    print(f"\nSelected StratifiedGroupKFold fold: {selected_fold}/5")
    print(f"Training rows: {len(train_idx):,}")
    print(f"Testing rows: {len(test_idx):,} ({test_fraction:.2%})")
    print(f"Training domain groups: {groups_train.nunique():,}")
    print(f"Testing domain groups: {groups_test.nunique():,}")
    print(f"Registrable domains shared across train/test: {len(overlap)}")
    print(f"Training class counts: {y_train.value_counts().sort_index().to_dict()}")
    print(f"Testing class counts: {y_test.value_counts().sort_index().to_dict()}")

    if overlap:
        print("ERROR: Domain overlap detected; refusing to report this split as grouped.")
        return 1

    print("\nTraining temporary audit model in memory (V1 saved model is NOT touched)...")
    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision_phishing": float(precision_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "recall_phishing": float(recall_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "f1_phishing": float(f1_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "confusion_matrix_actual_rows_predicted_columns": confusion_matrix(
            y_test, y_pred, labels=[0, 1]
        ).tolist(),
    }

    importances = sorted(
        [
            {"feature": name, "importance_percent": float(value * 100)}
            for name, value in zip(feature_columns, model.feature_importances_)
        ],
        key=lambda item: item["importance_percent"],
        reverse=True,
    )

    print("\n=== DOMAIN-GROUPED TEST RESULTS ===")
    print(f"Accuracy          : {metrics['accuracy'] * 100:.6f}%")
    print(f"Precision PHISHING: {metrics['precision_phishing'] * 100:.6f}%")
    print(f"Recall PHISHING   : {metrics['recall_phishing'] * 100:.6f}%")
    print(f"F1 PHISHING       : {metrics['f1_phishing'] * 100:.6f}%")
    print("Confusion matrix (actual rows [SAFE, PHISHING], predicted columns [SAFE, PHISHING]):")
    print(metrics["confusion_matrix_actual_rows_predicted_columns"])

    print("\n=== COMPARISON WITH PREVIOUS ROW-RANDOM TEST BASELINE ===")
    for key, baseline_value in ROW_RANDOM_BASELINE.items():
        grouped_value = metrics[key]
        difference_pp = (grouped_value - baseline_value) * 100
        print(
            f"{key}: row-random={baseline_value * 100:.4f}% | "
            f"domain-grouped={grouped_value * 100:.4f}% | "
            f"change={difference_pp:+.4f} percentage points"
        )

    print("\n=== TOP 14 FEATURE IMPORTANCES (TEMPORARY GROUPED MODEL) ===")
    for rank, item in enumerate(importances, start=1):
        print(
            f"{rank:2}. {item['feature']:<24} "
            f"{item['importance_percent']:.4f}%"
        )

    report = {
        "audit_type": "registrable_domain_grouped_split",
        "source_dataset": str(DATASET_PATH),
        "feature_metadata": str(METADATA_PATH),
        "rows": int(len(df)),
        "features": feature_columns,
        "unique_registrable_domains": int(groups.nunique()),
        "splitter": "StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)",
        "selected_fold": int(selected_fold),
        "test_fraction": float(test_fraction),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "train_domain_groups": int(groups_train.nunique()),
        "test_domain_groups": int(groups_test.nunique()),
        "shared_registrable_domains": int(len(overlap)),
        "train_class_counts": {
            str(k): int(v) for k, v in y_train.value_counts().sort_index().items()
        },
        "test_class_counts": {
            str(k): int(v) for k, v in y_test.value_counts().sort_index().items()
        },
        "row_random_test_baseline": ROW_RANDOM_BASELINE,
        "domain_grouped_test_metrics": metrics,
        "temporary_grouped_model_feature_importance": importances,
        "interpretation_note": (
            "A domain-grouped split tests generalization to registrable domains "
            "held out from training. This temporary audit model is not saved and "
            "does not replace the V1 model. Differences versus row-random results "
            "are evidence about split sensitivity, not by themselves proof of "
            "overfitting or data leakage."
        ),
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved to: {REPORT_PATH}")
    print("V1 saved model, source dataset, notebooks, and application were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
