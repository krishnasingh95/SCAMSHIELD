"""
ScamShield V1 URL Model — Domain-Grouped Feature Ablation Audit
READ-ONLY audit: does not modify V1 data, model, notebook, or application.
Trains temporary in-memory Random Forests using one fixed registrable-domain
holdout fold, then measures the effect of removing selected feature groups.
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
    print("ERROR: tldextract is not installed.")
    print("Run: python -m pip install tldextract")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = ROOT / "Training" / "datasets" / "processed" / "url_features_14.csv"
METADATA_PATH = ROOT / "Training" / "Models" / "url_feature_metadata.json"
REPORT_DIR = ROOT / "Training" / "Reports" / "V2"
REPORT_PATH = REPORT_DIR / "url_v1_feature_ablation_grouped.json"


def get_registrable_domain(url: str, extractor) -> str:
    value = str(url).strip()
    parsed = urlsplit(value)
    if not parsed.hostname:
        parsed = urlsplit("//" + value)
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return ""
    result = extractor(host)
    if result.domain and result.suffix:
        return f"{result.domain}.{result.suffix}".lower()
    return host


def metrics_for(model, X_test, y_test):
    pred = model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision_phishing": float(
            precision_score(y_test, pred, pos_label=1, zero_division=0)
        ),
        "recall_phishing": float(
            recall_score(y_test, pred, pos_label=1, zero_division=0)
        ),
        "f1_phishing": float(
            f1_score(y_test, pred, pos_label=1, zero_division=0)
        ),
        "confusion_matrix_actual_rows_predicted_columns": confusion_matrix(
            y_test, pred, labels=[0, 1]
        ).tolist(),
    }


def main() -> int:
    print("=== V1 URL FEATURE ABLATION AUDIT (DOMAIN-GROUPED) ===")
    print("Reading source dataset and metadata (read-only)...")

    if not DATASET_PATH.exists() or not METADATA_PATH.exists():
        print("ERROR: Dataset or metadata file not found.")
        print(f"Dataset: {DATASET_PATH}")
        print(f"Metadata: {METADATA_PATH}")
        return 1

    df = pd.read_csv(DATASET_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    features = metadata.get("feature_columns", [])

    required = {"URL", "target", *features}
    missing = sorted(required.difference(df.columns))
    if missing:
        print(f"ERROR: Required columns missing: {missing}")
        return 1

    if not features:
        print("ERROR: No feature_columns found in metadata.")
        return 1

    y = df["target"].astype(int)
    X = df[features].copy()

    extractor = tldextract.TLDExtract(
        suffix_list_urls=(),
        include_psl_private_domains=True,
    )
    groups = df["URL"].astype(str).map(
        lambda url: get_registrable_domain(url, extractor)
    )

    if (groups == "").any():
        print("ERROR: One or more URLs could not be assigned a domain group.")
        return 1

    splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )
    overall_rate = float(y.mean())
    folds = []

    for fold_no, (train_idx, test_idx) in enumerate(
        splitter.split(X, y, groups=groups), start=1
    ):
        frac = len(test_idx) / len(df)
        positive_rate = float(y.iloc[test_idx].mean())
        score = abs(frac - 0.20) + abs(positive_rate - overall_rate)
        folds.append((score, fold_no, train_idx, test_idx))

    _, fold_no, train_idx, test_idx = min(folds, key=lambda item: item[0])
    train_groups = set(groups.iloc[train_idx])
    test_groups = set(groups.iloc[test_idx])
    overlap = train_groups.intersection(test_groups)

    if overlap:
        print(f"ERROR: {len(overlap)} registrable domains overlap.")
        return 1

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    variants = {
        "all_14_features": list(features),
        "without_has_https": [f for f in features if f != "has_https"],
        "without_path_length_and_depth": [
            f for f in features if f not in {"path_length", "path_depth"}
        ],
        "without_top_3_shortcut_features": [
            f for f in features
            if f not in {"has_https", "path_length", "path_depth"}
        ],
        "top_3_features_only": [
            f for f in ["has_https", "path_length", "path_depth"] if f in features
        ],
    }

    print(f"Rows: {len(df):,} | Registrable-domain groups: {groups.nunique():,}")
    print(f"Selected grouped fold: {fold_no}/5")
    print(f"Train rows: {len(train_idx):,} | Test rows: {len(test_idx):,}")
    print(f"Shared registrable domains: {len(overlap)}")
    print("\nTraining temporary models in memory; saved V1 model will not be touched.")

    results = {}
    for name, selected_features in variants.items():
        if not selected_features:
            continue

        model = RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X.iloc[train_idx][selected_features], y_train)
        scores = metrics_for(model, X.iloc[test_idx][selected_features], y_test)
        results[name] = {
            "features_used": selected_features,
            "feature_count": len(selected_features),
            **scores,
        }

        print(f"\n--- {name} ({len(selected_features)} features) ---")
        print(f"Accuracy           : {scores['accuracy'] * 100:.6f}%")
        print(f"Precision PHISHING : {scores['precision_phishing'] * 100:.6f}%")
        print(f"Recall PHISHING    : {scores['recall_phishing'] * 100:.6f}%")
        print(f"F1 PHISHING        : {scores['f1_phishing'] * 100:.6f}%")
        print("Confusion matrix   :", scores["confusion_matrix_actual_rows_predicted_columns"])

    report = {
        "audit_type": "domain_grouped_feature_ablation",
        "source_dataset": str(DATASET_PATH),
        "rows": int(len(df)),
        "selected_fold": int(fold_no),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "unique_registrable_domains": int(groups.nunique()),
        "shared_registrable_domains": int(len(overlap)),
        "splitter": "StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)",
        "model_configuration": {
            "class": "RandomForestClassifier",
            "n_estimators": 200,
            "class_weight": "balanced",
            "random_state": 42,
        },
        "variants": results,
        "interpretation": (
            "Feature ablation measures how this particular grouped holdout's "
            "metrics change when selected feature(s) are removed. It does not "
            "by itself establish causality or production performance. The "
            "models are temporary and are not saved."
        ),
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nJSON report saved: {REPORT_PATH}")
    print("No source dataset, saved model, notebook, or application file was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
