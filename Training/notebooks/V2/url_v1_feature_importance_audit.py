"""Read-only feature-importance inspection for ScamShield URL V1 model.

Loads the existing model and feature metadata, prints impurity-based
Random Forest feature importances, and writes a CSV report under Reports/V2.
It does not train, modify, or overwrite the model or source dataset.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import joblib
except ImportError as exc:
    raise SystemExit(
        "joblib is not installed in this environment. Run: python -m pip install joblib"
    ) from exc

ROOT = Path(__file__).resolve().parents[3]  # .../ScamShield/Training/notebooks/V2 -> project root
MODEL_PATH = ROOT / "Training" / "Models" / "url_rf_model.pkl"
METADATA_PATH = ROOT / "Training" / "Models" / "url_feature_metadata.json"
OUTPUT_DIR = ROOT / "Training" / "Reports" / "V2"
OUTPUT_CSV = OUTPUT_DIR / "url_v1_feature_importance.csv"


def main() -> int:
    if not MODEL_PATH.is_file():
        print(f"ERROR: Model not found: {MODEL_PATH}")
        return 1
    if not METADATA_PATH.is_file():
        print(f"ERROR: Metadata not found: {METADATA_PATH}")
        return 1

    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    feature_names = metadata.get("feature_columns")
    if not isinstance(feature_names, list) or not feature_names:
        print("ERROR: 'feature_columns' is missing or empty in metadata.")
        return 1

    print("Loading existing V1 URL model (read-only)...")
    model = joblib.load(MODEL_PATH)
    print("Model type:", type(model).__name__)

    # Support either a direct estimator or a Pipeline whose final step is an estimator.
    estimator = model
    if not hasattr(estimator, "feature_importances_") and hasattr(model, "steps"):
        estimator = model.steps[-1][1]

    if not hasattr(estimator, "feature_importances_"):
        print("ERROR: Loaded estimator does not expose feature_importances_.")
        return 1

    importances = estimator.feature_importances_
    if len(importances) != len(feature_names):
        print(
            f"ERROR: Model has {len(importances)} importances but metadata lists "
            f"{len(feature_names)} feature names. Do not assume the order matches."
        )
        return 1

    try:
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(estimator)
    except Exception as exc:
        print(f"WARNING: Could not confirm fitted state: {exc}")

    rows = sorted(
        zip(feature_names, importances), key=lambda item: float(item[1]), reverse=True
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    import csv
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "feature", "impurity_based_importance", "importance_percent"])
        for rank, (name, value) in enumerate(rows, start=1):
            writer.writerow([rank, name, f"{float(value):.10f}", f"{float(value) * 100:.4f}"])

    print("\n=== V1 URL RANDOM FOREST FEATURE IMPORTANCE ===")
    print("Model feature count:", len(importances))
    print("Metadata estimators:", metadata.get("n_estimators", "not specified"))
    print("Metadata random_state:", metadata.get("random_state", "not specified"))
    print("\nRank | Feature | Importance (%)")
    print("-" * 52)
    for rank, (name, value) in enumerate(rows, start=1):
        print(f"{rank:>4} | {name:<25} | {float(value) * 100:>9.4f}")

    print(f"\nCSV report saved: {OUTPUT_CSV}")
    print("The model, metadata, dataset, and application were not modified.")
    print("NOTE: These are impurity-based importances, not causal explanations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
