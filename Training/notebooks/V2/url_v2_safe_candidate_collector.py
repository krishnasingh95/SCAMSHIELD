r"""
ScamShield URL Model V2 — SAFE-source sitemap candidate collector.

Reads only robots.txt and sitemap XML from allowlisted official documentation hosts.
It does not visit the individual page URLs listed in the sitemaps.
It never assigns a SAFE label automatically.
It writes timestamped outputs only under Training/datasets/V2/raw.
It does not modify V1 data, models, notebooks, or the application.

Run from the ScamShield project root:
    python Training\notebooks\V2\url_v2_safe_candidate_collector.py
"""

from __future__ import annotations

import csv
import gzip
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser


ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "Training" / "datasets" / "V2" / "raw"
TEMPLATE_PATH = RAW_DIR / "url_v2_provenance_template.csv"

USER_AGENT = "ScamShield-URLResearch/1.0 (sitemap metadata collection; no page crawling)"
REQUEST_TIMEOUT_SECONDS = 25
REQUEST_DELAY_SECONDS = 1.0
MAX_ROBOTS_BYTES = 1_000_000
MAX_SITEMAP_BYTES = 25_000_000
MAX_DECOMPRESSED_BYTES = 50_000_000
MAX_SITEMAPS_PER_SOURCE = 12
MAX_URLS_PER_SOURCE = 3000

EXPECTED_COLUMNS = [
    "record_id", "url", "label", "target", "source_name", "source_record_id",
    "source_reference", "license_or_terms", "retrieved_date",
    "verification_status", "label_confidence", "target_brand",
    "evidence_note", "is_synthetic",
]

# These hosts currently declare sitemap locations in their official robots.txt.
# W3C is intentionally omitted: its robots.txt did not declare a Sitemap directive
# when the source review was performed, so no guessed sitemap path is used.
SOURCES = [
    {
        "source_name": "Python Documentation",
        "host": "docs.python.org",
        "robots_url": "https://docs.python.org/robots.txt",
        "license_or_terms": (
            "Python documentation: PSF License Version 2, subject to page-specific "
            "notices. This run collects URL metadata only, not page text. Review "
            "source terms before training or redistribution."
        ),
    },
    {
        "source_name": "MDN Web Docs",
        "host": "developer.mozilla.org",
        "robots_url": "https://developer.mozilla.org/robots.txt",
        "license_or_terms": (
            "MDN documentation is generally CC-BY-SA 2.5 or later unless stated "
            "otherwise; attribution to Mozilla Contributors is required for content "
            "reuse. This run collects URL metadata only, not page text. Review terms "
            "before training or redistribution."
        ),
    },
]


def http_get(url: str, max_bytes: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/plain, application/xml, text/xml, */*",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"Response exceeded configured byte limit: {url}")
    return data


def parse_robots(text: str):
    lines = text.splitlines()
    sitemap_urls = []
    for line in lines:
        match = re.match(r"^\s*sitemap\s*:\s*(\S+)", line, flags=re.IGNORECASE)
        if match:
            sitemap_urls.append(match.group(1).strip())

    parser = RobotFileParser()
    parser.parse(lines)
    return parser, sitemap_urls


def host_is_allowed(url: str, allowed_host: str) -> bool:
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        return (
            parsed.scheme.lower() in {"http", "https"}
            and (host == allowed_host or host.endswith("." + allowed_host))
            and parsed.username is None
            and parsed.password is None
        )
    except ValueError:
        return False


def normalize_for_dedup(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower().rstrip(".")
    if not scheme or not host:
        return ""
    try:
        port = parsed.port
    except ValueError:
        return ""
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"
    return urlunsplit((scheme, netloc, parsed.path or "/", parsed.query, ""))


def get_xml_bytes(url: str) -> bytes:
    data = http_get(url, MAX_SITEMAP_BYTES)
    if data.startswith(b"\x1f\x8b") or url.lower().endswith(".gz"):
        data = gzip.decompress(data)
    if len(data) > MAX_DECOMPRESSED_BYTES:
        raise ValueError(f"Decompressed sitemap exceeded byte limit: {url}")
    return data


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def collect_sitemap(
    sitemap_url: str,
    allowed_host: str,
    robots_parser,
    visited: set[str],
    candidates: list[tuple[str, str]],
    log: list[dict],
) -> None:
    if len(visited) >= MAX_SITEMAPS_PER_SOURCE or sitemap_url in visited:
        return
    if not host_is_allowed(sitemap_url, allowed_host):
        log.append({"sitemap_url": sitemap_url, "status": "skipped_host_not_allowlisted"})
        return
    if not robots_parser.can_fetch(USER_AGENT, sitemap_url):
        log.append({"sitemap_url": sitemap_url, "status": "skipped_disallowed_by_robots"})
        return

    visited.add(sitemap_url)
    time.sleep(REQUEST_DELAY_SECONDS)
    try:
        xml_data = get_xml_bytes(sitemap_url)
        root = ET.fromstring(xml_data)
        kind = local_name(root.tag)
        locs = [
            (node.text or "").strip()
            for node in root.iter()
            if local_name(node.tag) == "loc" and (node.text or "").strip()
        ]

        if kind == "sitemapindex":
            log.append({"sitemap_url": sitemap_url, "status": "index_ok", "entries": len(locs)})
            for nested in locs:
                if len(visited) >= MAX_SITEMAPS_PER_SOURCE:
                    break
                collect_sitemap(nested, allowed_host, robots_parser, visited, candidates, log)
        elif kind == "urlset":
            accepted = 0
            for candidate in locs:
                if not host_is_allowed(candidate, allowed_host):
                    continue
                if not robots_parser.can_fetch(USER_AGENT, candidate):
                    continue
                candidates.append((candidate, sitemap_url))
                accepted += 1
                if len(candidates) >= MAX_URLS_PER_SOURCE:
                    break
            log.append({
                "sitemap_url": sitemap_url,
                "status": "urlset_ok",
                "entries_seen": len(locs),
                "accepted_after_host_and_robots_checks": accepted,
            })
        else:
            log.append({
                "sitemap_url": sitemap_url,
                "status": "unrecognized_xml_root",
                "root_tag": root.tag,
            })
    except (urllib.error.URLError, TimeoutError, ValueError, ET.ParseError, OSError) as exc:
        log.append({"sitemap_url": sitemap_url, "status": "error", "error": str(exc)[:500]})


def main() -> int:
    print("=== SCAMSHIELD V2 SAFE-SOURCE SITEMAP CANDIDATE COLLECTION ===")
    print("Fetch scope: robots.txt and sitemap XML only; no individual page visits.")
    print("Every collected URL remains unverified; no SAFE labels are assigned.\n")

    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Provenance template not found: {TEMPLATE_PATH}")
        return 1

    with TEMPLATE_PATH.open("r", newline="", encoding="utf-8-sig") as handle:
        columns = next(csv.reader(handle), [])
    if columns != EXPECTED_COLUMNS:
        print("ERROR: Provenance template columns do not match expected schema.")
        print("Found columns:", columns)
        print("Expected columns:", EXPECTED_COLUMNS)
        return 1

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    retrieved_date = now.date().isoformat()
    out_csv = RAW_DIR / f"url_v2_safe_candidates_unverified_{stamp}.csv"
    out_json = RAW_DIR / f"url_v2_safe_candidate_collection_{stamp}.json"

    all_rows = []
    source_reports = []

    for source in SOURCES:
        print(f"[SOURCE] {source['source_name']} ({source['host']})")
        report = {
            "source_name": source["source_name"],
            "host": source["host"],
            "robots_url": source["robots_url"],
            "status": "pending",
        }
        try:
            robots_text = http_get(source["robots_url"], MAX_ROBOTS_BYTES).decode(
                "utf-8", errors="replace"
            )
            robots_parser, sitemaps = parse_robots(robots_text)
            report["robots_status"] = "fetched"
            report["declared_sitemaps"] = sitemaps

            if not sitemaps:
                report["status"] = "no_sitemap_declared"
                report["note"] = "No sitemap directive; no sitemap path was guessed."
                source_reports.append(report)
                print("  No sitemap directive declared; skipped.")
                continue

            found = []
            visited = set()
            sitemap_log = []
            for sitemap in sitemaps:
                collect_sitemap(
                    sitemap, source["host"], robots_parser, visited, found, sitemap_log
                )
                if len(found) >= MAX_URLS_PER_SOURCE:
                    break

            report["status"] = "completed" if found else "completed_no_candidates"
            report["sitemap_files_visited"] = len(visited)
            report["sitemap_log"] = sitemap_log
            report["candidate_count_before_global_dedup"] = len(found)

            for index, (url, sitemap_reference) in enumerate(found, start=1):
                key = normalize_for_dedup(url)
                if not key:
                    continue
                all_rows.append({
                    "record_id": f"{source['host'].replace('.', '_')}-{index:06d}",
                    "url": url,
                    "label": "",
                    "target": "",
                    "source_name": source["source_name"],
                    "source_record_id": f"sitemap-entry-{index:06d}",
                    "source_reference": sitemap_reference,
                    "license_or_terms": source["license_or_terms"],
                    "retrieved_date": retrieved_date,
                    "verification_status": "candidate_unverified",
                    "label_confidence": "",
                    "target_brand": "",
                    "evidence_note": (
                        "Discovered in the source's robots.txt-declared sitemap. "
                        "Sitemap inclusion is not proof of safety. The page itself "
                        "was not fetched; verify its URL/domain and label before training."
                    ),
                    "is_synthetic": "false",
                    "_dedup_key": key,
                })

            print(f"  Sitemaps visited: {len(visited)} | Candidates: {len(found)}")
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            report["status"] = "error"
            report["error"] = str(exc)[:500]
            print(f"  ERROR: {exc}")
        source_reports.append(report)

    seen = set()
    unique_rows = []
    duplicates = 0
    for row in all_rows:
        key = row.pop("_dedup_key")
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique_rows.append(row)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with out_csv.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(unique_rows)

    summary = {
        "run_timestamp_utc": now.isoformat(),
        "purpose": "Collect documentation sitemap URL candidates for later verification.",
        "network_scope": "robots.txt and sitemap XML only; listed pages are not fetched.",
        "label_policy": "No SAFE or PHISHING labels assigned; all rows are candidate_unverified.",
        "sources": source_reports,
        "candidate_rows_before_dedup": len(all_rows),
        "duplicate_candidates_removed": duplicates,
        "unique_unverified_candidates_written": len(unique_rows),
        "output_csv": str(out_csv),
        "limits": {
            "max_sitemaps_per_source": MAX_SITEMAPS_PER_SOURCE,
            "max_urls_per_source": MAX_URLS_PER_SOURCE,
            "timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "delay_seconds_between_sitemap_requests": REQUEST_DELAY_SECONDS,
        },
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== SUMMARY ===")
    print(f"Candidates before dedup : {len(all_rows):,}")
    print(f"Duplicates removed      : {duplicates:,}")
    print(f"Unique candidates       : {len(unique_rows):,}")
    print(f"CSV report              : {out_csv}")
    print(f"JSON report             : {out_json}")
    print("\nAll rows remain unverified. Do not use them for training yet.")
    print("No V1 dataset, model, notebook, or application file was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
