"""
ScamShield — Risk Levels Enum & Colour Mapping
"""
from enum import Enum
from config import COLORS, RISK_THRESHOLDS


class RiskLevel(Enum):
    SAFE     = "SAFE"
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN  = "UNKNOWN"


RISK_COLORS = {
    RiskLevel.SAFE:     COLORS["risk_safe"],
    RiskLevel.LOW:      COLORS["risk_low"],
    RiskLevel.MEDIUM:   COLORS["risk_medium"],
    RiskLevel.HIGH:     COLORS["risk_high"],
    RiskLevel.CRITICAL: COLORS["risk_critical"],
    RiskLevel.UNKNOWN:  COLORS["text_muted"],
}

RISK_ICONS = {
    RiskLevel.SAFE:     "✅",
    RiskLevel.LOW:      "🟢",
    RiskLevel.MEDIUM:   "🟡",
    RiskLevel.HIGH:     "🟠",
    RiskLevel.CRITICAL: "🔴",
    RiskLevel.UNKNOWN:  "⚪",
}

RISK_LABELS = {
    RiskLevel.SAFE:     "Safe",
    RiskLevel.LOW:      "Low Risk",
    RiskLevel.MEDIUM:   "Suspicious",
    RiskLevel.HIGH:     "High Risk",
    RiskLevel.CRITICAL: "Critical Threat",
    RiskLevel.UNKNOWN:  "Unknown",
}


def confidence_to_risk(confidence: float) -> RiskLevel:
    """Map a 0–1 confidence score to a RiskLevel monotonically."""
    if confidence is None:
        return RiskLevel.UNKNOWN
    if confidence >= RISK_THRESHOLDS["critical"]:
        return RiskLevel.CRITICAL
    elif confidence >= RISK_THRESHOLDS["high"]:
        return RiskLevel.HIGH
    elif confidence >= RISK_THRESHOLDS["medium"]:
        return RiskLevel.MEDIUM
    elif confidence >= RISK_THRESHOLDS["low"]:
        return RiskLevel.LOW
    else:
        return RiskLevel.SAFE


def get_risk_color(level: RiskLevel) -> str:
    return RISK_COLORS.get(level, COLORS["text_muted"])


def get_risk_icon(level: RiskLevel) -> str:
    return RISK_ICONS.get(level, "⚪")


def get_risk_label(level: RiskLevel) -> str:
    return RISK_LABELS.get(level, "Unknown")
