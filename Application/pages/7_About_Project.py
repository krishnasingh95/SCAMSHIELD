"""
ScamShield — Page 7: About Project
Team info, methodology, tech stack, model descriptions.
"""
import streamlit as st
from config import PAGE_CONFIG, COLORS, APP_NAME, APP_VERSION, APP_SUBTITLE, TECH_STACK
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import page_header, section_divider

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

page_header("ℹ️", "About ScamShield", APP_SUBTITLE)

# ── Project Overview ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="ss-card">
    <p class="ss-card-title">🎯 Project Overview</p>
    <p style="color:{COLORS['text_primary']};font-size:0.93rem;line-height:1.7;">
        <strong style="color:{COLORS['accent_cyan']};">ScamShield</strong> is an
        AI-powered cybersecurity application that detects digital threats across multiple
        channels — SMS messages, URLs, and QR codes — using machine learning models trained
        on real-world scam and phishing datasets. The system provides real-time risk
        assessment with interpretable feature explanations.
    </p>
</div>
""", unsafe_allow_html=True)

section_divider("TECHNOLOGY STACK")

# ── Tech stack grid ───────────────────────────────────────────────────────
cols = st.columns(3)
for i, tech in enumerate(TECH_STACK):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="ss-card" style="text-align:center;padding:1rem;">
            <div style="font-size:2rem;">{tech['icon']}</div>
            <p style="color:{COLORS['accent_cyan']};font-weight:700;margin:0.4rem 0 0.1rem;
                      font-size:0.95rem;">{tech['name']}</p>
            <p style="color:{COLORS['text_muted']};font-size:0.75rem;margin:0;">{tech['role']}</p>
        </div>
        """, unsafe_allow_html=True)

section_divider("ML METHODOLOGY")

m1, m2 = st.columns(2)
with m1:
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">💬 SMS Scam Detector</p>
        <ul style="color:{COLORS['text_muted']};font-size:0.83rem;line-height:1.8;padding-left:1.2rem;margin:0;">
            <li>Algorithm: <strong style="color:{COLORS['text_primary']};">Random Forest Classifier</strong></li>
            <li>Features: character count, URL presence, keyword hits, uppercase ratio, digit ratio, special chars</li>
            <li>Dataset: SMS Spam Collection (UCI), augmented with phishing SMS samples</li>
            <li>Serialisation: <code>joblib</code> (.pkl)</li>
        </ul>
    </div>
    <div class="ss-card" style="margin-top:0;">
        <p class="ss-card-title">📐 Feature Extraction Pipeline</p>
        <ol style="color:{COLORS['text_muted']};font-size:0.82rem;line-height:1.8;padding-left:1.2rem;margin:0;">
            <li>Raw input → text normalisation</li>
            <li>Structural feature extraction (length, ratios, counts)</li>
            <li>Lexical feature extraction (keyword matching, URL parsing)</li>
            <li>Feature vector → StandardScaler → Random Forest</li>
            <li>Probability output → Risk Level mapping</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="ss-card">
        <p class="ss-card-title">🌐 URL Phishing Detector (V2.1 Multi-Dataset)</p>
        <ul style="color:{COLORS['text_muted']};font-size:0.83rem;line-height:1.8;padding-left:1.2rem;margin:0;">
            <li>Algorithm: <strong style="color:{COLORS['text_primary']};">Random Forest Classifier (200 Trees • Class Balanced)</strong></li>
            <li>Scale: <strong style="color:{COLORS['accent_cyan']};">1,349,127 Audited URLs</strong> (754K Safe, 595K Phishing)</li>
            <li>Evaluation: <strong style="color:{COLORS['risk_safe']};">85.25% Accuracy</strong> &nbsp;|&nbsp; <strong style="color:{COLORS['risk_safe']};">93.84% ROC-AUC</strong> &nbsp;|&nbsp; 83.35% F1</li>
            <li>Features: 14 structural & lexical properties (TLD, IP, depth, tokens, entropy, length, HTTPS)</li>
            <li>Datasets: 7 Curated Peer-Reviewed Benchmark Sources:
                <ul style="margin:4px 0 0 10px;font-size:0.78rem;">
                    <li>MURL Large-Scale Malicious URL Dataset (783K URLs)</li>
                    <li>PhiUSIIL Phishing URL Dataset (235K URLs)</li>
                    <li>Phishing URL Dataset (125K URLs)</li>
                    <li>URL-Phish V2 — Mendeley (114K URLs)</li>
                    <li>LegitPhish V2 — Mendeley (64K clean URLs)</li>
                    <li>CompPhish V4 — Mendeley (15K URLs)</li>
                    <li>Web Page Phishing Detection — Mendeley (11K URLs)</li>
                </ul>
            </li>
            <li>Serialisation: <code>joblib</code> (.pkl) with verified SHA-256 integrity</li>
        </ul>
    </div>
    <div class="ss-card" style="margin-top:0;">
        <p class="ss-card-title">🔀 Combined Risk Engine</p>
        <ul style="color:{COLORS['text_muted']};font-size:0.83rem;line-height:1.8;padding-left:1.2rem;margin:0;">
            <li>Weighted aggregation of SMS + URL signals</li>
            <li>SMS weight: <strong style="color:{COLORS['text_primary']};">45%</strong> &nbsp;|&nbsp; URL weight: <strong style="color:{COLORS['text_primary']};">55%</strong></li>
            <li>Risk thresholds: Safe &lt;40%, Medium 40–65%, High 65–85%, Critical &gt;85%</li>
            <li>QR codes are decoded first, then routed to the appropriate analyser</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

section_divider("SYSTEM ARCHITECTURE")

st.markdown(f"""
<div class="ss-card">
    <p class="ss-card-title">🏛️ Modular Design Principles</p>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-top:0.5rem;">
        <div>
            <p style="color:{COLORS['accent_blue']};font-weight:600;font-size:0.85rem;">🎨 UI Layer</p>
            <p style="color:{COLORS['text_muted']};font-size:0.78rem;">
                Streamlit pages + reusable components in <code>ui/</code>.
                Theme, cards, charts, and sidebar defined once.
            </p>
        </div>
        <div>
            <p style="color:{COLORS['accent_cyan']};font-weight:600;font-size:0.85rem;">⚙️ Core Layer</p>
            <p style="color:{COLORS['text_muted']};font-size:0.78rem;">
                Analyzers in <code>core/</code> expose a consistent
                <code>predict()</code> interface — models plug in without touching pages.
            </p>
        </div>
        <div>
            <p style="color:{COLORS['accent_purple']};font-weight:600;font-size:0.85rem;">🤖 Model Layer</p>
            <p style="color:{COLORS['text_muted']};font-size:0.78rem;">
                Drop trained <code>.pkl</code> files into <code>models/</code>.
                The app auto-detects them on startup.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

section_divider("HOW TO ADD YOUR MODELS")

st.markdown(f"""
<div class="ss-card">
    <p class="ss-card-title">🔌 Plugging in Trained Random Forest Models</p>
    <ol style="color:{COLORS['text_muted']};font-size:0.85rem;line-height:2;padding-left:1.5rem;margin:0;">
        <li>Train your model with Scikit-Learn and export with <code>joblib.dump(model, path)</code></li>
        <li>Place <code>sms_rf_model.pkl</code> in the <code>models/</code> directory</li>
        <li>Place <code>url_rf_model.pkl</code> in the <code>models/</code> directory</li>
        <li>(Optional) Place <code>sms_scaler.pkl</code> / <code>url_scaler.pkl</code> in <code>models/feature_scalers/</code></li>
        <li>Restart the Streamlit app — models are loaded automatically via <code>@st.cache_resource</code></li>
    </ol>
    <br>
    <code style="color:{COLORS['accent_cyan']};font-size:0.85rem;">
        # Example training export:<br>
        import joblib<br>
        joblib.dump(rf_model, "models/sms_rf_model.pkl")<br>
        joblib.dump(scaler,   "models/feature_scalers/sms_scaler.pkl")
    </code>
</div>
""", unsafe_allow_html=True)

section_divider()
st.markdown(f"""
<div style="text-align:center;color:{COLORS['text_muted']};font-size:0.78rem;padding:1rem 0;">
    {APP_NAME} v{APP_VERSION} &nbsp;·&nbsp; AIML College Project &nbsp;·&nbsp;
    Built with 🛡️ Python · Streamlit · Scikit-Learn
</div>
""", unsafe_allow_html=True)
