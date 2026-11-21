"""
ScamShield — Page 5: Combined Risk Analysis
Multi-signal assessment combining SMS + URL analyzers via the Risk Engine.
"""
import streamlit as st
import pandas as pd
from config import PAGE_CONFIG, COLORS
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import (page_header, risk_badge, model_not_loaded_notice,
                      confidence_bar, feature_table, section_divider)
from ui.charts import threat_gauge
from core.sms_analyzer import SMSAnalyzer
from core.url_analyzer import URLAnalyzer
from core.risk_engine import RiskEngine
from core.history_manager import add_record
from utils.validators import sanitize_text, is_valid_url
from utils.risk_levels import get_risk_label

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

page_header("🔀", "Combined Risk Analysis",
            "Aggregate multiple signals into a unified threat assessment")

@st.cache_resource
def get_analyzers():
    return SMSAnalyzer(), URLAnalyzer(), RiskEngine()

sms_analyzer, url_analyzer, risk_engine = get_analyzers()

# ── Banner if no models ───────────────────────────────────────────────────
if not sms_analyzer.model_loaded and not url_analyzer.model_loaded:
    model_not_loaded_notice("sms_rf_model.pkl + url_rf_model.pkl")
    st.markdown("<br>", unsafe_allow_html=True)

# ── Input Panel ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ss-card">
    <p class="ss-card-title">📥 Multi-Signal Input</p>
    <p style="color:{COLORS['text_muted']};font-size:0.82rem;margin-bottom:1rem;">
        Provide one or more inputs. The Risk Engine combines all available signals.
    </p>
</div>
""", unsafe_allow_html=True)

tab_single, tab_batch = st.tabs(["Single Assessment", "Batch / Paste List"])

with tab_single:
    st.markdown(f"<p style='color:{COLORS['text_muted']};font-size:0.78rem;margin-bottom:0.4rem;'>Load test sample pairs:</p>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1:
        if st.button("🚨 Bank Phishing Sample", key="load_comb_1"):
            st.session_state["combined_sms"] = "URGENT: Your SBI net banking account has been locked due to pending KYC! Update immediately to prevent account closure."
            st.session_state["combined_url"] = "http://sbi-card-kyc-update.top/netbanking"
            st.rerun()
    with c_btn2:
        if st.button("🎁 Reward Scam Sample", key="load_comb_2"):
            st.session_state["combined_sms"] = "Congratulations! You were randomly selected to win a $1000 Walmart gift card! Claim your free reward right now."
            st.session_state["combined_url"] = "http://free-iphone15-winner.xyz/claim?id=192837"
            st.rerun()
    with c_btn3:
        if st.button("✅ Safe Order Sample", key="load_comb_3"):
            st.session_state["combined_sms"] = "Your Amazon package #AMZ-4819 has shipped and will arrive on Friday. View tracking in your Amazon app."
            st.session_state["combined_url"] = "https://www.amazon.com/dp/B09X4K9BSQ"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    sms_col, url_col = st.columns(2)
    with sms_col:
        sms_input = st.text_area("SMS / Message Text (optional)", height=130,
                                 placeholder="Paste the message here…", key="combined_sms")
    with url_col:
        url_input = st.text_input("URL (optional)",
                                  placeholder="https://example.com", key="combined_url")

    analyse_btn = st.button("🔍 Run Combined Analysis", type="primary", key="btn_combined")

    if analyse_btn:
        results     = {}
        has_input   = False

        sms_text = sanitize_text(sms_input or "")
        url_text = (url_input or "").strip()

        if sms_text:
            has_input = True
            with st.spinner("Analysing SMS…"):
                results["sms"] = sms_analyzer.predict(sms_text)
        if url_text:
            has_input = True
            if not is_valid_url(url_text):
                st.error("Invalid URL format. Please enter a valid URL or web domain.")
            else:
                with st.spinner("Analysing URL…"):
                    results["url"] = url_analyzer.predict(url_text)

        if not has_input:
            st.warning("Please provide at least one input (SMS or URL).")
        else:
            combined = risk_engine.combine(results)
            section_divider("COMBINED ASSESSMENT")

            g_col, d_col = st.columns([1, 2])
            with g_col:
                if combined.get("combined_score") is not None:
                    st.plotly_chart(
                        threat_gauge(combined["combined_score"], "Combined Threat Score"),
                        use_container_width=True
                    )
                else:
                    st.info("Load trained models to see a combined threat score.")

            with d_col:
                risk_badge(combined["risk_level"])
                st.markdown(f"""
                <p style="color:{COLORS['text_muted']};font-size:0.82rem;margin-top:0.75rem;">
                    Risk Level: <strong style="color:{COLORS['text_primary']};">
                    {get_risk_label(combined['risk_level'])}</strong>
                </p>
                """, unsafe_allow_html=True)

                if combined.get("combined_score") is not None:
                    confidence_bar(combined["combined_score"], "Aggregated Risk Score")

            # ── Component results ─────────────────────────────────────────
            section_divider("COMPONENT SIGNALS")
            comps = combined.get("components", {})
            if "sms" in comps and comps["sms"].get("status") == "ok":
                with st.expander("💬 SMS Component", expanded=True):
                    confidence_bar(comps["sms"]["confidence"], "SMS Scam Probability")
                    feature_table(comps["sms"].get("features", {}))
            if "url" in comps and comps["url"].get("status") == "ok":
                with st.expander("🌐 URL Component", expanded=True):
                    confidence_bar(comps["url"]["confidence"], "URL Phishing Probability")
                    feature_table(comps["url"].get("features", {}))

            add_record("Combined", f"SMS+URL combined", {
                "status":     combined.get("status"),
                "label":      "THREAT" if combined.get("threat_detected") else "SAFE",
                "confidence": combined.get("combined_score"),
                "risk_level": combined.get("risk_level"),
            })

with tab_batch:
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">📋 Batch URL Analysis</p>
        <p style="color:{COLORS['text_muted']};font-size:0.82rem;">
            Paste one URL per line for bulk analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    batch_input = st.text_area("URLs (one per line)", height=160,
                               placeholder="https://site1.com\nhttps://site2.com\n…",
                               key="batch_urls")
    batch_btn = st.button("🔍 Analyse Batch", type="primary", key="btn_batch")

    if batch_btn:
        lines = [l.strip() for l in (batch_input or "").splitlines() if l.strip()]
        if not lines:
            st.warning("Please enter at least one URL.")
        else:
            rows = []
            prog = st.progress(0, text="Analysing…")
            for i, line in enumerate(lines):
                prog.progress((i + 1) / len(lines), text=f"Analysing {i+1}/{len(lines)}")
                if is_valid_url(line):
                    res = url_analyzer.predict(line)
                    rows.append({
                        "URL":        line[:80],
                        "Status":     res.get("status"),
                        "Label":      res.get("label", "—"),
                        "Risk Level": res.get("risk_level", "—"),
                        "Confidence": f"{res.get('confidence',0)*100:.1f}%" if res.get("confidence") else "—",
                    })
                else:
                    rows.append({"URL": line[:80], "Status": "invalid", "Label": "—",
                                 "Risk Level": "—", "Confidence": "—"})

            prog.empty()
            section_divider("BATCH RESULTS")
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Export Results CSV", df.to_csv(index=False),
                               file_name="scamshield_batch.csv", mime="text/csv")
