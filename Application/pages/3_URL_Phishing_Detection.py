"""
ScamShield — Page 3: URL Phishing Detection
"""
import streamlit as st
from config import PAGE_CONFIG, COLORS, SAMPLE_URLS
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import (page_header, risk_badge, model_not_loaded_notice,
                      confidence_bar, feature_table, section_divider, ai_analysis_card)
from ui.charts import feature_radar
from core.url_analyzer import URLAnalyzer
from core.ai_analyzer import AIAnalyzer
from core.history_manager import add_record
from utils.validators import is_valid_url, is_empty

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

page_header("🌐", "URL Phishing Detection",
            "Inspect URLs for phishing indicators and malicious patterns")

@st.cache_resource
def get_url_analyzer():
    return URLAnalyzer()

@st.cache_resource
def get_ai_analyzer():
    return AIAnalyzer()

analyzer    = get_url_analyzer()
ai_analyzer = get_ai_analyzer()

if not analyzer.model_loaded:
    model_not_loaded_notice("url_rf_model.pkl")
    st.markdown("<br>", unsafe_allow_html=True)
else:
    v_badge = analyzer.model_version
    meta = analyzer.model_info
    samples = meta.get("total_samples", 428993)
    auc_val = meta.get("roc_auc", 0.9888)
    st.markdown(f"""
    <div style="background:{COLORS['bg_card']};border:1px solid {COLORS['accent_cyan']}44;border-radius:10px;padding:0.65rem 1.1rem;margin-bottom:1.2rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="background:{COLORS['accent_cyan']}22;color:{COLORS['accent_cyan']};border:1px solid {COLORS['accent_cyan']}66;border-radius:20px;padding:2px 10px;font-size:0.75rem;font-weight:700;">MODEL V{v_badge} ACTIVE</span>
            <span style="color:{COLORS['text_primary']};font-size:0.85rem;font-weight:600;">Random Forest • 200 Trees • Class Balanced</span>
        </div>
        <div style="color:{COLORS['text_muted']};font-size:0.78rem;">
            Trained on <strong style="color:{COLORS['accent_cyan']};">{samples:,} URLs</strong> across 7 Datasets &nbsp;|&nbsp; ROC-AUC: <strong style="color:{COLORS['risk_safe']};">{auc_val:.2%}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Input ────────────────────────────────────────────────────────────────
col_in, col_sample = st.columns([3, 1])
with col_in:
    url_input = st.text_input(
        "Enter URL to analyse",
        placeholder="https://example.com/path?query=value",
        key="url_input",
    )
with col_sample:
    st.markdown(f"<p style='color:{COLORS['text_muted']};font-size:0.78rem;'>Load a sample:</p>",
                unsafe_allow_html=True)
    for i, sample in enumerate(SAMPLE_URLS, 1):
        if st.button(f"Sample {i}", key=f"sample_url_{i}"):
            st.session_state["url_input"] = sample
            st.rerun()

analyse_btn = st.button("🔍 Analyse URL", type="primary")

# ── Analysis ──────────────────────────────────────────────────────────────
if analyse_btn:
    url = (url_input or st.session_state.get("url_input", "")).strip()
    if is_empty(url):
        st.warning("Please enter a URL.")
    elif not is_valid_url(url):
        st.error("⚠️ Invalid URL format. Please enter a valid URL or domain.")
    else:
        with st.spinner("Extracting URL features and analysing…"):
            result = analyzer.predict(url)

        section_divider("ANALYSIS RESULT")

        # ── URL decomposition card ────────────────────────────────────────
        feats = result.get("features", {})
        st.markdown(f"""
        <div class="ss-card">
            <p class="ss-card-title">🔗 URL Decomposition</p>
            <div style="display:flex;gap:1rem;flex-wrap:wrap;">
                <span style="color:{COLORS['text_muted']};font-size:0.8rem;">Scheme:</span>
                <code style="color:{COLORS['accent_cyan']};font-size:0.85rem;">{feats.get('_scheme','?')}</code>
                <span style="color:{COLORS['text_muted']};font-size:0.8rem;">Domain:</span>
                <code style="color:{COLORS['accent_blue']};font-size:0.85rem;">{feats.get('_parsed_domain','?')}</code>
                <span style="color:{COLORS['text_muted']};font-size:0.8rem;">TLD:</span>
                <code style="color:{COLORS['accent_purple']};font-size:0.85rem;">{feats.get('_tld','?')}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Structural risk flags ─────────────────────────────────────────
        flags = []
        if feats.get("has_ip_address"):       flags.append("IP Address as domain")
        if feats.get("has_suspicious_tld"):   flags.append(f"Suspicious TLD ({feats.get('_tld','')})")
        if not feats.get("has_https"):         flags.append("No HTTPS")
        if feats.get("has_brand_keyword"):    flags.append("Brand keyword in domain")
        if feats.get("brand_in_subdomain"):   flags.append("Brand name in subdomain")
        if feats.get("has_redirect"):         flags.append("Redirect parameter detected")
        if feats.get("url_length", 0) > 100: flags.append("Unusually long URL")

        if flags:
            rh = COLORS["risk_high"]
            pills = "".join(
                f"<span style='background:{rh}22;color:{rh};"
                f"border:1px solid {rh}44;border-radius:99px;padding:2px 12px;"
                f"font-size:0.78rem;font-weight:600;margin:2px;display:inline-block;'>"
                f"⚠ {f}</span>"
                for f in flags
            )
            st.markdown(f"""
            <div class="ss-card">
                <p class="ss-card-title">🚩 Structural Risk Flags</p>
                <div style="display:flex;flex-wrap:wrap;gap:4px;">{pills}</div>
            </div>
            """, unsafe_allow_html=True)

        if result["status"] == "model_not_loaded":
            st.info("⚙️ Feature extraction done. Add the trained model for full predictions.")
            c1, c2 = st.columns(2)
            with c1:
                feature_table(feats)
            with c2:
                feat_num = {k: v for k, v in feats.items()
                            if not k.startswith("_") and isinstance(v, (int, float))}
                st.plotly_chart(feature_radar(feat_num, "URL Feature Radar"), use_container_width=True)
            add_record("URL", url, {**result, "label": None})

        elif result["status"] == "ok":
            r1, r2 = st.columns([1, 2])
            with r1:
                risk_badge(result["risk_level"])
                st.markdown(f"""
                <div style="margin-top:1rem;">
                    <p style="color:{COLORS['text_muted']};font-size:0.78rem;">Detection</p>
                    <p style="font-size:1.6rem;font-weight:800;
                       color:{'#FF3B3B' if result['label']=='PHISHING' else '#00C851'};">
                        {result['label']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                confidence_bar(result["confidence"], "Phishing Probability")

            c1, c2 = st.columns(2)
            with c1:
                feature_table(feats)
            with c2:
                feat_num = {k: v for k, v in feats.items()
                            if not k.startswith("_") and isinstance(v, (int, float))}
                st.plotly_chart(feature_radar(feat_num, "URL Feature Radar"), use_container_width=True)
            add_record("URL", url, result)

            # ── AI Analysis ───────────────────────────────────────────────
            section_divider("AI-POWERED EXPLANATION")
            if ai_analyzer.available:
                with st.spinner("🤖 Asking AI for a detailed explanation…"):
                    ai_result = ai_analyzer.explain(
                        content=url,
                        scan_type="URL",
                        rf_label=result["label"],
                        rf_confidence=result["confidence"],
                    )
            else:
                ai_result = {
                    "status":  "unavailable",
                    "message": "Add FREEMODEL_API_KEY to your .env file to enable AI explanations.",
                }
            ai_analysis_card(ai_result)

        else:
            st.error(f"Analysis error: {result.get('message')}")
