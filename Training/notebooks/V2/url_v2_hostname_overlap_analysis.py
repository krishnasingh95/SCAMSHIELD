"""Read-only analysis of hostnames appearing in both URL labels.

Reads Training/datasets/processed/url_features_14.csv and writes CSV/JSON
reports under Training/Reports/V2. It does not modify the source dataset,
models, notebooks, or application files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]  # .../Training/notebooks/V2 -> project root
DATASET = ROOT / "Training" / "datasets" / "processed" / "url_features_14.csv"
OUT_DIR = ROOT / "Training" / "Reports" / "V2"


def extract_hostname(value: object) -> str:
    """Return a lowercase hostname without a trailing dot; no network access."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    try:
        candidate = text if "://" in text else "//" + text
        return (urlsplit(candidate).hostname or "").lower().rstrip(".")
    except (ValueError, TypeError):
        return ""


def main() -> int:
    if not DATASET.exists():
        print(f"ERROR: Dataset not found: {DATASET}")
        print("Run this script from its saved location inside Training/notebooks/V2.")
        return 1

    print("Loading source dataset (read-only)...")
    df = pd.read_csv(DATASET)
    required = {"URL", "target"}
    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: Required columns missing: {sorted(missing)}")
        return 1

    target_numeric = pd.to_numeric(df["target"], errors="coerce")
    df = df.copy()
    df["_target_numeric"] = target_numeric
    df["label"] = df["_target_numeric"].map({0: "SAFE", 1: "PHISHING"})
    df["hostname"] = df["URL"].map(extract_hostname)

    valid = df[df["hostname"].ne("") & df["label"].notna()].copy()
    class_counts = valid.groupby("hostname")["label"].nunique()
    overlap_hosts = sorted(class_counts[class_counts > 1].index.tolist())
    overlap_rows = valid[valid["hostname"].isin(overlap_hosts)].copy()

    summary_rows = []
    for host in overlap_hosts:
        group = overlap_rows[overlap_rows["hostname"] == host]
        safe_count = int((group["label"] == "SAFE").sum())
        phishing_count = int((group["label"] == "PHISHING").sum())
        summary_rows.append({
            "hostname": host,
            "safe_rows": safe_count,
            "phishing_rows": phishing_count,
            "total_rows": int(len(group)),
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUT_DIR / "hostname_overlap_summary.csv"
    records_path = OUT_DIR / "hostname_overlap_records.csv"
    json_path = OUT_DIR / "hostname_overlap_analysis.json"

    summary_df = pd.DataFrame(summary_rows, columns=[
        "hostname", "safe_rows", "phishing_rows", "total_rows"
    ])
    if not summary_df.empty:
        summary_df = summary_df.sort_values(
            ["total_rows", "hostname"], ascending=[False, True]
        )
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

    export_cols = ["hostname", "URL", "label", "target"]
    if "path_length" in overlap_rows.columns:
        export_cols.append("path_length")
    if "query_length" in overlap_rows.columns:
        export_cols.append("query_length")
    overlap_rows[export_cols].sort_values(["hostname", "label", "URL"]).to_csv(
        records_path, index=False, encoding="utf-8-sig"
    )

    report = {
        "source_dataset": str(DATASET),
        "source_rows": int(len(df)),
        "hostnames_with_both_labels": int(len(overlap_hosts)),
        "rows_for_those_hostnames": int(len(overlap_rows)),
        "safe_rows_for_those_hostnames": int((overlap_rows["label"] == "SAFE").sum()),
        "phishing_rows_for_those_hostnames": int((overlap_rows["label"] == "PHISHING").sum()),
        "note": (
            "A hostname appearing in both classes is not automatically a label error. "
            "Inspect URL-level records; do not relabel or delete a whole hostname based only on this report."
        ),
        "outputs": [str(summary_path), str(records_path)],
    }
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== HOSTNAME OVERLAP SUMMARY ===")
    print(f"Source rows: {len(df)}")
    print(f"Hostnames appearing in both SAFE and PHISHING: {len(overlap_hosts)}")
    print(f"Rows for those hostnames: {len(overlap_rows)}")
    print(f"SAFE rows: {(overlap_rows['label'] == 'SAFE').sum()}")
    print(f"PHISHING rows: {(overlap_rows['label'] == 'PHISHING').sum()}")
    print("\nSaved reports:")
    print(summary_path)
    print(records_path)
    print(json_path)
    print("\nNo source dataset, model, notebook, or application file was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
