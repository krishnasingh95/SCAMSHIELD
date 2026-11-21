"""
ScamShield — Page 4: QR Code Scanner
Decode QR → analyse embedded URL or text.
"""
import streamlit as st
from config import PAGE_CONFIG, COLORS
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import (page_header, risk_badge, model_not_loaded_notice,
                      confidence_bar, feature_table, section_divider, ai_analysis_card)
from core.qr_analyzer import QRAnalyzer
from core.url_analyzer import URLAnalyzer
from core.sms_analyzer import SMSAnalyzer
from core.ai_analyzer import AIAnalyzer
from core.history_manager import add_record

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

page_header("📷", "QR Code Scanner",
            "Upload a QR code image to decode and analyse its embedded content")

@st.cache_resource
def get_qr_analyzer():   return QRAnalyzer()
@st.cache_resource
def get_url_analyzer():  return URLAnalyzer()
@st.cache_resource
def get_sms_analyzer():  return SMSAnalyzer()
@st.cache_resource
def get_ai_analyzer():   return AIAnalyzer()

qr_analyzer  = get_qr_analyzer()
url_analyzer = get_url_analyzer()
sms_analyzer = get_sms_analyzer()
ai_analyzer  = get_ai_analyzer()

# ── Upload ────────────────────────────────────────────────────────────────
col_up, col_info = st.columns([2, 1])
with col_up:
    uploaded = st.file_uploader(
        "Upload QR Code Image",
        type=["png", "jpg", "jpeg", "bmp", "gif", "webp"],
        help="Supported formats: PNG, JPG, JPEG, BMP, GIF, WebP",
    )
with col_info:
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">ℹ How It Works</p>
        <ol style="color:{COLORS['text_muted']};font-size:0.82rem;padding-left:1.2rem;margin:0;">
            <li>Upload a QR code image</li>
            <li>OpenCV pre-processes the image</li>
            <li>pyzbar decodes the QR content</li>
            <li>Decoded text is analysed for threats</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

if uploaded:
    image_bytes = uploaded.read()

    img_col, result_col = st.columns([1, 2])
    with img_col:
        st.image(image_bytes, caption="Uploaded QR Code", use_container_width=True)

    with result_col:
        with st.spinner("Decoding QR code…"):
            decode_result = qr_analyzer.decode_image(image_bytes)

        section_divider("DECODE RESULT")

        status = decode_result.get("status")
        if status == "no_qr_found":
            st.warning("🔍 No QR code detected in the image. Try a clearer or higher-resolution image.")
        elif status == "error":
            st.error(f"❌ Decode error: {decode_result.get('message')}")
        elif status == "ok":
            decoded_data  = decode_result["data"]
            data_type     = decode_result["data_type"]
            barcode_type  = decode_result.get("barcode_type", "QR")

            st.markdown(f"""
            <div class="ss-card">
                <p class="ss-card-title">📋 Decoded Content ({barcode_type})</p>
                <code style="color:{COLORS['accent_cyan']};font-size:0.9rem;word-break:break-all;">
                    {decoded_data}
                </code>
                <br><br>
                <span style="background:{COLORS['bg_tertiary']};color:{COLORS['text_muted']};
                      border-radius:99px;padding:2px 10px;font-size:0.75rem;">
                    Content type: {data_type.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # ── Downstream analysis ───────────────────────────────────────
            section_divider("THREAT ANALYSIS")

            if data_type == "url":
                st.info(f"🌐 Analysing embedded URL with URL Phishing Detector…")
                if not url_analyzer.model_loaded:
                    model_not_loaded_notice("url_rf_model.pkl")
                result = url_analyzer.predict(decoded_data)
                result["qr_source"] = True
            else:
                st.info(f"💬 Analysing embedded text with SMS Scam Detector…")
                if not sms_analyzer.model_loaded:
                    model_not_loaded_notice("sms_rf_model.pkl")
                result = sms_analyzer.predict(decoded_data)
                result["qr_source"] = True

            if result["status"] in ("ok", "model_not_loaded"):
                if result["status"] == "ok":
                    r1, r2 = st.columns([1, 2])
                    with r1:
                        risk_badge(result["risk_level"])
                        st.markdown(f"""
                        <p style="font-size:1.4rem;font-weight:800;
                           color:{'#FF3B3B' if result.get('label') in ('SCAM','PHISHING') else '#00C851'};">
                            {result.get('label','—')}
                        </p>
                        """, unsafe_allow_html=True)
                    with r2:
                        confidence_bar(result.get("confidence"), "Threat Probability")
                else:
                    st.info("⚙️ Feature extraction complete. Load a trained model for predictions.")

                feature_table(result.get("features", {}))
                add_record("QR", decoded_data[:80], result)

                # ── AI Analysis ───────────────────────────────────────────
                if result["status"] == "ok":
                    section_divider("AI-POWERED EXPLANATION")
                    scan_type = "URL" if data_type == "url" else "SMS"
                    if ai_analyzer.available:
                        with st.spinner("🤖 Asking AI for a detailed explanation…"):
                            ai_result = ai_analyzer.explain(
                                content=decoded_data,
                                scan_type=scan_type,
                                rf_label=result.get("label", "UNKNOWN"),
                                rf_confidence=result.get("confidence", 0.5),
                            )
                    else:
                        ai_result = {
                            "status":  "unavailable",
                            "message": "Add FREEMODEL_API_KEY to your .env to enable AI explanations.",
                        }
                    ai_analysis_card(ai_result)
