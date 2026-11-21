"""
ScamShield — Page 1: Dashboard
System overview with KPI cards, recent alerts, and activity charts.
"""
import streamlit as st
import pandas as pd
from config import PAGE_CONFIG, COLORS
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import page_header, section_divider
from ui.charts import scan_history_bar, risk_distribution_pie, timeline_chart
from core.history_manager import get_all, get_stats

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────
page_header("📊", "Dashboard", "Real-time threat monitoring and system overview")

# ── Model Status Banner ──────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{COLORS['bg_card']};border:1px solid {COLORS['border']};border-radius:10px;padding:0.75rem 1.25rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
    <div style="display:flex;align-items:center;gap:15px;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:6px;">
            <div style="width:8px;height:8px;border-radius:50%;background:{COLORS['risk_safe']};box-shadow:0 0 6px {COLORS['risk_safe']};"></div>
            <span style="color:{COLORS['text_primary']};font-size:0.8rem;font-weight:600;">SMS Model:</span>
            <span style="color:{COLORS['text_muted']};font-size:0.8rem;">Random Forest (v1.0)</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
            <div style="width:8px;height:8px;border-radius:50%;background:{COLORS['accent_cyan']};box-shadow:0 0 6px {COLORS['accent_cyan']};"></div>
            <span style="color:{COLORS['text_primary']};font-size:0.8rem;font-weight:600;">URL Model:</span>
            <span style="color:{COLORS['accent_cyan']};font-size:0.8rem;font-weight:700;">V2.1 Active</span>
            <span style="color:{COLORS['text_muted']};font-size:0.78rem;">(1.34M URLs across 7 Datasets)</span>
        </div>
    </div>
    <span style="background:{COLORS['accent_blue']}22;color:{COLORS['accent_blue']};border:1px solid {COLORS['accent_blue']}55;border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:600;">
        ScamShield Engine v2.0
    </span>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────
stats   = get_stats()
records = get_all()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Scans",    stats.get("total", 0), help="All scans performed")
with col2:
    st.metric("Threats Found",  stats.get("scam",  0), help="Scam / Phishing detections",
              delta=None)
with col3:
    safe = stats.get("safe", 0)
    st.metric("Safe Results",   safe,  help="Clean inputs")
with col4:
    pct = f"{round(stats['scam']/stats['total']*100,1)}%" if stats.get("total") else "—"
    st.metric("Threat Rate",    pct,   help="Percentage of threats detected")

section_divider("SCAN ACTIVITY")

# ── Charts Row ────────────────────────────────────────────────────────────
ch1, ch2, ch3 = st.columns(3)
with ch1:
    st.plotly_chart(scan_history_bar(records),      use_container_width=True)
with ch2:
    st.plotly_chart(risk_distribution_pie(records), use_container_width=True)
with ch3:
    st.plotly_chart(timeline_chart(records),        use_container_width=True)

section_divider("RECENT ALERTS")

# ── Recent Alerts Table ───────────────────────────────────────────────────
recent = records[:10]
if recent:
    df = pd.DataFrame(recent)[["timestamp","scan_type","input_preview","risk_level","label","confidence"]]
    df.columns = ["Time","Type","Input","Risk Level","Label","Confidence"]
    df["Confidence"] = df["Confidence"].apply(lambda x: f"{x*100:.1f}%" if x is not None else "—")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.markdown(f"""
    <div style="text-align:center;padding:3rem;color:{COLORS['text_muted']};">
        <div style="font-size:2.5rem;">🛡️</div>
        <p style="font-size:1rem;margin-top:0.5rem;">No scans yet — use the sidebar to start analysing.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Quick Action Cards ────────────────────────────────────────────────────
section_divider("QUICK ACTIONS")
qa1, qa2, qa3 = st.columns(3)
with qa1:
    st.markdown(f"""
    <div class="ss-card" style="text-align:center;cursor:pointer;">
        <div style="font-size:2rem;">💬</div>
        <p style="color:{COLORS['accent_cyan']};font-weight:600;margin:0.5rem 0 0.25rem;">SMS Scanner</p>
        <p style="color:{COLORS['text_muted']};font-size:0.8rem;margin:0;">Detect scam text messages</p>
    </div>
    """, unsafe_allow_html=True)
with qa2:
    st.markdown(f"""
    <div class="ss-card" style="text-align:center;cursor:pointer;">
        <div style="font-size:2rem;">🌐</div>
        <p style="color:{COLORS['accent_cyan']};font-weight:600;margin:0.5rem 0 0.25rem;">URL Checker</p>
        <p style="color:{COLORS['text_muted']};font-size:0.8rem;margin:0;">Identify phishing links</p>
    </div>
    """, unsafe_allow_html=True)
with qa3:
    st.markdown(f"""
    <div class="ss-card" style="text-align:center;cursor:pointer;">
        <div style="font-size:2rem;">📷</div>
        <p style="color:{COLORS['accent_cyan']};font-weight:600;margin:0.5rem 0 0.25rem;">QR Scanner</p>
        <p style="color:{COLORS['text_muted']};font-size:0.8rem;margin:0;">Scan QR codes for threats</p>
    </div>
    """, unsafe_allow_html=True)
