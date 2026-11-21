"""Read-only quality audit for ScamShield URL Model V2 preparation.

Reads the existing V1 processed dataset and V2 metadata files. It does not
modify any source dataset, model, notebook, or application file. It writes one
JSON report into Training/Reports/V2/.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd

ROOT = Path.cwd()
DATASET = ROOT / "Training" / "datasets" / "processed" / "url_features_14.csv"
SCHEMA = ROOT / "Training" / "datasets" / "v2" / "proposed_v2_schema.json"
MANIFEST = ROOT / "Training" / "datasets" / "v2" / "test_cases_manifest.json"
REPORT_DIR = ROOT / "Training" / "Reports" / "V2"
REPORT_PATH = REPORT_DIR / "url_v1_quality_audit.json"

LABELS = {0: "SAFE", 1: "PHISHING"}
SUSPICIOUS_TLDS = {"tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "pw"}


def normalize_url(value: object) -> str | None:
    """Conservative normalization: lower scheme/host, remove fragment/default port.

    Path and query are deliberately preserved to avoid merging URLs that may
    have different server-side meaning.
    """
    if pd.isna(value):
        return None
    raw = str(value).strip()
    if not raw:
        return None
    candidate = raw if "://" in raw else "//" + raw
    try:
        parsed = urlsplit(candidate)
        host = (parsed.hostname or "").lower().rstrip(".")
        if not host:
            return None
        scheme = parsed.scheme.lower()
        port = parsed.port  # Access may raise ValueError for malformed ports.
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None
        host_port = host if port is None else f"{host}:{port}"
        if scheme:
            return f"{scheme}://{host_port}{parsed.path}?{parsed.query}".rstrip("?")
        return f"//{host_port}{parsed.path}?{parsed.query}".rstrip("?")
    except (ValueError, TypeError):
        return None


def safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def main() -> int:
    for path in (DATASET, SCHEMA, MANIFEST):
        if not path.exists():
            print(f"ERROR: Required file not found: {path}")
            return 2

    print("Loading files (read-only)...")
    df = pd.read_csv(DATASET, low_memory=False)
    with SCHEMA.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    with MANIFEST.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    required_columns = {"URL", "target", "path_length", "query_length"}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        print("ERROR: Dataset is missing required columns:", missing_columns)
        return 3

    feature_names = [item.get("name") for item in schema.get("features", [])]
    dataset_feature_names = [c for c in df.columns if c not in {"URL", "target"}]
    invalid_labels = sorted(set(df["target"].dropna().unique()) - set(LABELS))

    work = df[["URL", "target", "path_length", "query_length"]].copy()
    work["target"] = pd.to_numeric(work["target"], errors="coerce")
    work["path_length"] = pd.to_numeric(work["path_length"], errors="coerce").fillna(0)
    work["query_length"] = pd.to_numeric(work["query_length"], errors="coerce").fillna(0)
    work["normalized_url"] = work["URL"].map(normalize_url)

    # Hostname-level grouping only. This intentionally does NOT claim to be
    # registrable-domain grouping because a Public Suffix List is required.
    def get_hostname(value: object) -> str | None:
        if pd.isna(value):
            return None
        raw = str(value).strip()
        try:
            parsed = urlsplit(raw if "://" in raw else "//" + raw)
            return (parsed.hostname or "").lower().rstrip(".") or None
        except ValueError:
            return None

    work["hostname"] = work["URL"].map(get_hostname)
    work["tld"] = work["hostname"].map(lambda h: h.rsplit(".", 1)[-1] if h and "." in h else None)
    work["has_path"] = work["path_length"] > 0
    work["has_query"] = work["query_length"] > 0

    target_counts = {LABELS.get(safe_int(k), str(k)): int(v) for k, v in df["target"].value_counts(dropna=False).items()}
    per_class = {}
    for target, label in LABELS.items():
        subset = work[work["target"] == target]
        per_class[label] = {
            "records": int(len(subset)),
            "urls_with_path": int(subset["has_path"].sum()),
            "urls_without_path": int((~subset["has_path"]).sum()),
            "urls_with_query": int(subset["has_query"].sum()),
            "urls_without_query": int((~subset["has_query"]).sum()),
            "mean_path_length": round(float(subset["path_length"].mean()), 4) if len(subset) else None,
            "mean_query_length": round(float(subset["query_length"].mean()), 4) if len(subset) else None,
        }

    host_label_sets = work.dropna(subset=["hostname"]).groupby("hostname")["target"].agg(lambda x: sorted(set(int(v) for v in x.dropna())))
    cross_label_hosts = [host for host, labels in host_label_sets.items() if len(labels) > 1]
    safe_path_samples = work[(work["target"] == 0) & work["has_path"]]["URL"].head(10).tolist()
    phish_no_path_samples = work[(work["target"] == 1) & (~work["has_path"])]["URL"].head(10).tolist()

    manifest_cases = manifest.get("test_cases", [])
    test_case_summary = []
    for item in manifest_cases:
        expected_label = item.get("expected_label")
        expected_target = item.get("expected_target")
        mapping_ok = (expected_label == "SAFE" and expected_target == 0) or (expected_label == "PHISHING" and expected_target == 1)
        test_case_summary.append({
            "url": item.get("url"),
            "expected_label": expected_label,
            "expected_target": expected_target,
            "category": item.get("category"),
            "label_mapping_consistent": mapping_ok,
        })

    report = {
        "audit_name": "ScamShield V1 URL Dataset Read-only Quality Audit for V2 Planning",
        "dataset_path": str(DATASET),
        "schema_path": str(SCHEMA),
        "manifest_path": str(MANIFEST),
        "dataset_shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "dataset_columns": df.columns.tolist(),
        "schema": {
            "version": schema.get("schema_version"),
            "model_type": schema.get("model_type"),
            "declared_num_features": schema.get("num_features"),
            "actual_schema_feature_count": len(feature_names),
            "schema_feature_order": feature_names,
            "dataset_feature_count_excluding_URL_target": len(dataset_feature_names),
            "dataset_feature_order": dataset_feature_names,
            "feature_names_match_in_order": feature_names == dataset_feature_names,
            "label_mapping": schema.get("label_mapping"),
        },
        "data_integrity": {
            "exact_duplicate_url_rows": int(df["URL"].duplicated().sum()),
            "normalized_duplicate_url_rows": int(work["normalized_url"].dropna().duplicated().sum()),
            "missing_url_values": int(df["URL"].isna().sum()),
            "blank_url_values": int(df["URL"].fillna("").astype(str).str.strip().eq("").sum()),
            "missing_target_values": int(df["target"].isna().sum()),
            "invalid_target_values": invalid_labels,
            "rows_with_unparseable_or_missing_hostname": int(work["hostname"].isna().sum()),
            "hostnames_appearing_in_both_classes": int(len(cross_label_hosts)),
            "cross_label_hostname_examples": cross_label_hosts[:25],
        },
        "target_counts": target_counts,
        "classwise_url_structure": per_class,
        "tld_counts_by_class": {
            LABELS[target]: {str(k): int(v) for k, v in work[work["target"] == target]["tld"].value_counts().head(20).items()}
            for target in LABELS
        },
        "suspicious_tld_counts_by_class": {
            LABELS[target]: int(((work["target"] == target) & work["tld"].isin(SUSPICIOUS_TLDS)).sum())
            for target in LABELS
        },
        "examples": {
            "safe_urls_with_paths": safe_path_samples,
            "phishing_urls_without_paths": phish_no_path_samples,
        },
        "benchmark_manifest": {
            "name": manifest.get("benchmark_name"),
            "isolation_policy": manifest.get("isolation_policy"),
            "case_count": len(manifest_cases),
            "all_label_mappings_consistent": all(x["label_mapping_consistent"] for x in test_case_summary),
            "cases": test_case_summary,
            "note": "The 7 canonical cases are regression/smoke tests, not a statistically sufficient final evaluation set. Synthetic fixtures must remain separate from training data.",
        },
        "interpretation_notes": [
            "Hostname overlap is reported at exact-hostname level, not registrable-domain level; robust registrable-domain grouping requires a maintained Public Suffix List.",
            "Normalized duplicate detection is conservative: it lowercases scheme/hostname, removes fragments and default ports, but preserves path and query.",
            "This script does not train a model or modify source data.",
        ],
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n=== AUDIT SUMMARY ===")
    print("Rows x Columns:", df.shape)
    print("Target counts:", target_counts)
    print("Exact duplicate URL rows:", report["data_integrity"]["exact_duplicate_url_rows"])
    print("Normalized duplicate URL rows:", report["data_integrity"]["normalized_duplicate_url_rows"])
    print("Feature names match schema in exact order:", report["schema"]["feature_names_match_in_order"])
    print("Canonical test cases:", len(manifest_cases))
    print("All test label mappings consistent:", report["benchmark_manifest"]["all_label_mappings_consistent"])
    print("\nClass-wise structure:")
    for label, values in per_class.items():
        print(label, values)
    print("\nReport saved to:", REPORT_PATH)
    print("Source dataset, models, notebooks, and application were not modified.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # Print actionable error without silently hiding it.
        print(f"AUDIT FAILED: {type(exc).__name__}: {exc}")
        raise
