"""
ScamShield — Reusable UI Card Components
"""
import streamlit as st
from config import COLORS
from utils.risk_levels import RiskLevel, get_risk_color, get_risk_icon, get_risk_label


def page_header(icon: str, title: str, subtitle: str = ""):
    """Render a consistent page header with icon, title, and subtitle."""
    st.markdown(f"""
    <div class="ss-page-header">
        <span class="ss-page-icon">{icon}</span>
        <div>
            <p class="ss-page-title">{title}</p>
            <p class="ss-page-subtitle">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def risk_badge(level: RiskLevel, show_label: bool = True):
    """Render a coloured risk badge pill."""
    color = get_risk_color(level)
    icon  = get_risk_icon(level)
    label = get_risk_label(level)
    text  = f"{icon} {label}" if show_label else icon
    st.markdown(f"""
    <span class="ss-risk-badge" style="background:{color}22; color:{color}; border:1px solid {color}66;">
        {text}
    </span>
    """, unsafe_allow_html=True)


def model_not_loaded_notice(model_name: str = ""):
    """Show a friendly placeholder when no model is available yet."""
    name = f" ({model_name})" if model_name else ""
    st.markdown(f"""
    <div class="ss-model-notice">
        ⚙️ &nbsp; <strong>Model Not Loaded{name}</strong><br>
        <span style="font-size:0.78rem;">
            Drop the trained <code>.pkl</code> file into the <code>models/</code> directory
            and restart the app to enable predictions.
        </span>
    </div>
    """, unsafe_allow_html=True)


def info_card(title: str, value: str, icon: str = "", color: str = ""):
    """Generic info display card."""
    c = color or COLORS["accent_cyan"]
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">{icon} {title}</p>
        <p style="font-size:1.5rem;font-weight:700;color:{c};margin:0;">{value}</p>
    </div>
    """, unsafe_allow_html=True)


def feature_table(features: dict, exclude_keys: list = None):
    """Display extracted features as a clean key-value table."""
    exclude = set(exclude_keys or [])
    exclude.update({k for k in features if k.startswith("_")})
    rows = "".join(
        f"<tr><td style='color:{COLORS['text_muted']};padding:3px 10px 3px 0;'>{k}</td>"
        f"<td style='color:{COLORS['text_primary']};font-weight:500;'>{v}</td></tr>"
        for k, v in features.items() if k not in exclude
    )
    st.markdown(f"""
    <div class="ss-card ss-feature-table">
        <p class="ss-card-title">📐 Extracted Features</p>
        <table style="width:100%;border-collapse:collapse;">{rows}</table>
    </div>
    """, unsafe_allow_html=True)


def confidence_bar(confidence: float, label: str = "Threat Confidence"):
    """Render a styled confidence progress bar."""
    if confidence is None:
        return
    pct     = round(confidence * 100, 1)
    level   = _conf_to_risk(confidence)
    color   = get_risk_color(level)
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">{label}</p>
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="flex:1;background:{COLORS['bg_tertiary']};border-radius:99px;height:14px;overflow:hidden;">
                <div style="width:{pct}%;background:{color};height:100%;border-radius:99px;
                            transition:width 0.5s ease;"></div>
            </div>
            <span style="color:{color};font-weight:700;font-size:1.1rem;min-width:48px;">{pct}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _conf_to_risk(conf: float) -> RiskLevel:
    from utils.risk_levels import confidence_to_risk
    return confidence_to_risk(conf)


def keyword_highlight_card(keywords: list):
    """Show matched scam keywords as red pills."""
    if not keywords:
        return
    rc  = COLORS["risk_critical"]
    pills = "".join(
        f"<span style='background:{rc}22;color:{rc};border:1px solid {rc}44;"
        f"border-radius:99px;padding:2px 12px;font-size:0.78rem;font-weight:600;margin:2px;display:inline-block;'>{kw}</span>"
        for kw in keywords
    )
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">🚩 Matched Threat Keywords</p>
        <div style="display:flex;flex-wrap:wrap;gap:4px;">{pills}</div>
    </div>
    """, unsafe_allow_html=True)


def ai_analysis_card(ai_result: dict):
    """
    Render the FreeModel AI analysis panel.
    ai_result is the dict returned by AIAnalyzer.explain().
    """
    status = ai_result.get("status")
    ac     = COLORS["accent_purple"]

    if status == "unavailable":
        st.markdown(f"""
        <div class="ss-card" style="border-color:{ac}44;opacity:0.65;">
            <p class="ss-card-title">🤖 AI Analysis — Unavailable</p>
            <p style="color:{COLORS['text_muted']};font-size:0.82rem;">
                {ai_result.get('message', 'API key not configured.')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    if status == "error":
        st.markdown(f"""
        <div class="ss-card" style="border-color:{COLORS['risk_high']}44;">
            <p class="ss-card-title">🤖 AI Analysis — Error</p>
            <p style="color:{COLORS['risk_high']};font-size:0.82rem;">
                {ai_result.get('message', 'Unknown error.')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Success ──────────────────────────────────────────────────────────
    classification = ai_result.get("classification", "UNKNOWN")
    risk_level     = ai_result.get("risk_level", "MEDIUM")
    confidence     = ai_result.get("confidence", 50)
    explanation    = ai_result.get("explanation", "")
    warnings       = ai_result.get("warning_signs", [])
    tips           = ai_result.get("tips", [])
    model_name     = ai_result.get("model", "AI")

    risk_colors = {
        "CRITICAL": COLORS["risk_critical"],
        "HIGH":     COLORS["risk_high"],
        "MEDIUM":   COLORS["risk_medium"],
        "LOW":      COLORS["risk_low"],
        "SAFE":     COLORS["risk_safe"],
    }
    cls_colors = {
        "SCAM":       COLORS["risk_critical"],
        "SUSPICIOUS": COLORS["risk_high"],
        "SAFE":       COLORS["risk_safe"],
    }
    risk_color = risk_colors.get(risk_level, ac)
    cls_color  = cls_colors.get(classification, ac)

    warning_pills = "".join(
        f"<span style='background:{COLORS['risk_high']}22;color:{COLORS['risk_high']};"
        f"border:1px solid {COLORS['risk_high']}44;border-radius:99px;padding:2px 11px;"
        f"font-size:0.76rem;font-weight:600;margin:2px;display:inline-block;'>⚠ {w}</span>"
        for w in warnings
    )
    tip_items = "".join(
        f"<li style='margin:3px 0;color:{COLORS['text_muted']};font-size:0.82rem;'>💡 {t}</li>"
        for t in tips
    )

    st.markdown(f"""
    <div class="ss-card" style="border-color:{ac}55;background:linear-gradient(135deg,{COLORS['bg_card']} 80%,{ac}08 100%);">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;margin-bottom:0.7rem;">
            <p class="ss-card-title" style="margin:0;">🤖 AI Analysis
                <span style="background:{ac}22;color:{ac};border:1px solid {ac}55;border-radius:20px;
                             padding:1px 8px;font-size:0.70rem;font-weight:600;margin-left:6px;">{model_name}</span>
            </p>
            <span style="background:{cls_color}22;color:{cls_color};border:1px solid {cls_color}55;
                         border-radius:99px;padding:3px 14px;font-size:0.85rem;font-weight:700;">
                {classification}
            </span>
        </div>
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:0.75rem;flex-wrap:wrap;">
            <span style="color:{COLORS['text_muted']};font-size:0.78rem;">Risk:</span>
            <span style="color:{risk_color};font-weight:700;font-size:0.9rem;">{risk_level}</span>
            <span style="color:{COLORS['text_muted']};font-size:0.78rem;">AI Confidence:</span>
            <span style="color:{risk_color};font-weight:700;font-size:0.9rem;">{confidence}%</span>
        </div>
        <p style="color:{COLORS['text_primary']};font-size:0.88rem;margin-bottom:0.75rem;line-height:1.5;">
            {explanation}
        </p>
        {"<div style='margin-bottom:0.65rem;'>" + warning_pills + "</div>" if warnings else ""}
        {"<ul style='padding-left:1.1rem;margin:0;'>" + tip_items + "</ul>" if tips else ""}
    </div>
    """, unsafe_allow_html=True)


def section_divider(label: str = ""):
    if label:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin:1rem 0;">
            <hr style="flex:1;border-color:{COLORS['border']};margin:0;">
            <span style="color:{COLORS['text_muted']};font-size:0.75rem;white-space:nowrap;">{label}</span>
            <hr style="flex:1;border-color:{COLORS['border']};margin:0;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<hr style='border-color:{COLORS['border']};'>", unsafe_allow_html=True)
