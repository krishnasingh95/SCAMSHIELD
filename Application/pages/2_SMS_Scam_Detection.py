"""
ScamShield — Page 2: SMS Scam Detection
"""
import streamlit as st
from config import PAGE_CONFIG, COLORS, SAMPLE_SMS_TEXTS
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import (page_header, risk_badge, model_not_loaded_notice,
                      confidence_bar, feature_table, keyword_highlight_card,
                      section_divider, ai_analysis_card)
from ui.charts import feature_radar
from core.sms_analyzer import SMSAnalyzer
from core.ai_analyzer import AIAnalyzer
from core.history_manager import add_record
from utils.validators import is_empty, sanitize_text

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

page_header("💬", "SMS Scam Detection",
            "Analyse text messages to identify scam and phishing attempts")

# ── Lazy-load analyzer (cached per session) ───────────────────────────────
@st.cache_resource
def get_sms_analyzer():
    return SMSAnalyzer()

@st.cache_resource
def get_ai_analyzer():
    return AIAnalyzer()

analyzer    = get_sms_analyzer()
ai_analyzer = get_ai_analyzer()

# ── Model status banner ───────────────────────────────────────────────────
if not analyzer.model_loaded:
    model_not_loaded_notice("sms_rf_model.pkl")
    st.markdown("<br>", unsafe_allow_html=True)

# ── Input section ─────────────────────────────────────────────────────────
col_in, col_sample = st.columns([3, 1])
with col_in:
    sms_text = st.text_area(
        "Enter SMS / message text",
        height=160,
        placeholder="Paste the suspicious SMS message here…",
        key="sms_input",
    )
with col_sample:
    st.markdown(f"<p style='color:{COLORS['text_muted']};font-size:0.78rem;'>Load a sample:</p>",
                unsafe_allow_html=True)
    for i, sample in enumerate(SAMPLE_SMS_TEXTS, 1):
        if st.button(f"Sample {i}", key=f"sample_sms_{i}"):
            st.session_state["sms_input"] = sample
            st.rerun()

analyse_btn = st.button("🔍 Analyse Message", type="primary", use_container_width=False)

# ── Analysis ──────────────────────────────────────────────────────────────
if analyse_btn:
    text = sanitize_text(sms_text or st.session_state.get("sms_input", ""))
    if is_empty(text):
        st.warning("Please enter a message to analyse.")
    else:
        with st.spinner("Extracting features and analysing…"):
            result = analyzer.predict(text)

        section_divider("ANALYSIS RESULT")

        if result["status"] == "model_not_loaded":
            st.info("⚙️ Feature extraction completed. ML prediction requires the trained model.")
            r1, r2 = st.columns(2)
            with r1:
                feature_table(result["features"])
            with r2:
                keyword_highlight_card(result.get("matched_keywords", []))
                feat_num = {k: v for k, v in result["features"].items()
                            if not k.startswith("_") and isinstance(v, (int, float))}
                st.plotly_chart(feature_radar(feat_num, "Feature Profile"), use_container_width=True)

            # Store partial record
            add_record("SMS", text[:80], {**result, "label": None})

        elif result["status"] == "ok":
            # Risk badge + confidence
            r1, r2 = st.columns([1, 2])
            with r1:
                risk_badge(result["risk_level"])
                st.markdown(f"""
                <div style="margin-top:1rem;">
                    <p style="color:{COLORS['text_muted']};font-size:0.78rem;">Detection</p>
                    <p style="font-size:1.6rem;font-weight:800;color:{'#FF3B3B' if result['label']=='SCAM' else '#00C851'};">
                        {result['label']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                confidence_bar(result["confidence"], "Scam Probability")

            section_divider("FEATURE ANALYSIS")
            f1, f2 = st.columns(2)
            with f1:
                feature_table(result["features"])
            with f2:
                keyword_highlight_card(result.get("matched_keywords", []))
                urls = result.get("extracted_urls", [])
                if urls:
                    st.markdown(f"**🔗 URLs found in message:**")
                    for u in urls:
                        st.code(u, language=None)

            feat_num = {k: v for k, v in result["features"].items()
                        if not k.startswith("_") and isinstance(v, (int, float))}
            st.plotly_chart(feature_radar(feat_num, "Feature Radar"), use_container_width=True)
            add_record("SMS", text[:80], result)

            # ── AI Analysis (Hybrid: RF verdict → AI explanation) ─────────
            section_divider("AI-POWERED EXPLANATION")
            if ai_analyzer.available:
                with st.spinner("🤖 Asking AI for a detailed explanation…"):
                    ai_result = ai_analyzer.explain(
                        content=text,
                        scan_type="SMS",
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
            st.error(f"Analysis error: {result.get('message', 'Unknown error')}")
