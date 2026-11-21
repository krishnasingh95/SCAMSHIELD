"""
ScamShield — Analysis History Manager
Read/write persistent scan history to data/history.json
"""
import json
import os
import uuid
from datetime import datetime
from config import HISTORY_FILE, MAX_HISTORY_RECORDS

os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def _load() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(records: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records[-MAX_HISTORY_RECORDS:], f, indent=2, default=str)


def add_record(scan_type: str, input_preview: str, result: dict) -> dict:
    """Append a scan result to history. Returns the stored record."""
    records = _load()
    risk_level = result.get("risk_level")
    record = {
        "id":            str(uuid.uuid4())[:8],
        "timestamp":     datetime.now().isoformat(timespec="seconds"),
        "scan_type":     scan_type,
        "input_preview": input_preview[:120],
        "risk_level":    risk_level.value if hasattr(risk_level, "value") else str(risk_level),
        "confidence":    result.get("confidence"),
        "label":         result.get("label"),
        "status":        result.get("status"),
    }
    records.append(record)
    _save(records)
    return record


def get_all() -> list:
    return list(reversed(_load()))


def clear_history():
    _save([])


def get_stats() -> dict:
    records = _load()
    total   = len(records)
    if total == 0:
        return {"total": 0, "scam": 0, "safe": 0, "by_type": {}}

    scam_count = sum(1 for r in records if r.get("label") in ("SCAM", "PHISHING"))
    by_type    = {}
    for r in records:
        t = r.get("scan_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total":    total,
        "scam":     scam_count,
        "safe":     total - scam_count,
        "by_type":  by_type,
    }
