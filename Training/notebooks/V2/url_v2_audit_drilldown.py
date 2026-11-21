"""Read-only drill-down for ScamShield's V1 URL audit findings.

Run from the ScamShield project root. This script only reads the processed
V1 CSV and the audit JSON report; it does not modify either file or any model.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd

ROOT = Path.cwd()
CSV_PATH = ROOT / "Training" / "datasets" / "processed" / "url_features_14.csv"
REPORT_PATH = ROOT / "Training" / "Reports" / "V2" / "url_v1_quality_audit.json"
LABELS = {0: "SAFE", 1: "PHISHING"}


def normalize_url(value: object) -> str | None:
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
        port = parsed.port
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None
        host_port = host if port is None else f"{host}:{port}"
        if scheme:
            return f"{scheme}://{host_port}{parsed.path}?{parsed.query}".rstrip("?")
        return f"//{host_port}{parsed.path}?{parsed.query}".rstrip("?")
    except (ValueError, TypeError):
        return None


def hostname_of(value: object) -> str | None:
    if pd.isna(value):
        return None
    raw = str(value).strip()
    try:
        parsed = urlsplit(raw if "://" in raw else "//" + raw)
        return (parsed.hostname or "").lower().rstrip(".") or None
    except ValueError:
        return None


def main() -> int:
    for path in (CSV_PATH, REPORT_PATH):
        if not path.exists():
            print(f"ERROR: File not found: {path}")
            return 2

    df = pd.read_csv(CSV_PATH, low_memory=False)
    with REPORT_PATH.open("r", encoding="utf-8") as f:
        report = json.load(f)

    work = df[["URL", "target"]].copy()
    work["normalized_url"] = work["URL"].map(normalize_url)
    work["hostname"] = work["URL"].map(hostname_of)

    print("=== AUDIT DRILL-DOWN (READ ONLY) ===")
    integrity = report.get("data_integrity", {})
    for key in (
        "missing_url_values", "blank_url_values", "missing_target_values",
        "invalid_target_values", "rows_with_unparseable_or_missing_hostname",
        "hostnames_appearing_in_both_classes",
    ):
        print(f"{key}: {integrity.get(key)}")

    duplicate_rows = work[work["normalized_url"].notna() & work.duplicated("normalized_url", keep=False)]
    groups = []
    for normalized, group in duplicate_rows.groupby("normalized_url", sort=False):
        labels = sorted({LABELS.get(int(v), str(v)) for v in group["target"].dropna()})
        groups.append((normalized, group, labels))

    conflicting = [item for item in groups if len(item[2]) > 1]
    print("\n=== NORMALIZED DUPLICATE DETAILS ===")
    print("Duplicate groups:", len(groups))
    print("Rows involved:", len(duplicate_rows))
    print("Groups with conflicting labels:", len(conflicting))
    for idx, (normalized, group, labels) in enumerate(groups[:40], start=1):
        print(f"\nGroup {idx} | labels={labels} | rows={len(group)}")
        print("Normalized:", normalized)
        for _, row in group.iterrows():
            label = LABELS.get(int(row["target"]), str(row["target"])) if pd.notna(row["target"]) else "MISSING"
            print(f"  [{label}] {row['URL']}")
    if len(groups) > 40:
        print(f"\nOnly first 40 of {len(groups)} groups displayed.")

    print("\n=== HOSTNAMES PRESENT IN BOTH CLASSES (FIRST 25) ===")
    host_labels = work.dropna(subset=["hostname"]).groupby("hostname")["target"].agg(
        lambda values: sorted({int(v) for v in values.dropna()})
    )
    cross = [(host, [LABELS.get(v, str(v)) for v in labels]) for host, labels in host_labels.items() if len(labels) > 1]
    print("Count:", len(cross))
    for host, labels in cross[:25]:
        print(f"{host}: {labels}")

    print("\n=== SAFE URL PATH EXAMPLES ===")
    examples = report.get("examples", {}).get("safe_urls_with_paths", [])
    print(examples if examples else "None found in the processed dataset.")
    print("\n=== PHISHING URLS WITHOUT PATH EXAMPLES ===")
    examples = report.get("examples", {}).get("phishing_urls_without_paths", [])
    print(examples if examples else "None found in the processed dataset.")

    print("\nNo files were modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
