"""
ScamShield — Global Configuration
AI-Powered Intelligent Digital Threat Detection and Risk Assessment System
"""

import os

# ─── App Identity ────────────────────────────────────────────────────────────
APP_NAME        = "ScamShield"
APP_SUBTITLE    = "AI-Powered Digital Threat Detection"
APP_VERSION     = "2.0.0"
APP_ICON        = "🛡️"

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR      = os.path.join(BASE_DIR, "models")
DATA_DIR        = os.path.join(BASE_DIR, "data")
ASSETS_DIR      = os.path.join(BASE_DIR, "assets")
HISTORY_FILE    = os.path.join(DATA_DIR, "history.json")

MODEL_PATHS = {
    "sms":              os.path.join(MODELS_DIR, "sms_rf_model.pkl"),
    "sms_vectorizer":   os.path.join(MODELS_DIR, "sms_tfidf_vectorizer.pkl"),
    "sms_metadata":     os.path.join(MODELS_DIR, "sms_feature_metadata.pkl"),
    "url":              os.path.join(MODELS_DIR, "url_rf_model.pkl"),
    "url_metadata":     os.path.join(MODELS_DIR, "url_feature_metadata.json"),
}

URL_MODEL_VERSION = "2.1.0"
URL_DATASETS_COUNT = 7
URL_TRAINING_SAMPLES = "1,349,127"
URL_MODEL_ROC_AUC = "93.84%"

# ─── Design Tokens ───────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#0A0E1A",
    "bg_secondary":  "#0D1B2A",
    "bg_tertiary":   "#112240",
    "bg_card":       "#0F1C32",
    "accent_blue":   "#1E90FF",
    "accent_cyan":   "#00D4FF",
    "accent_purple": "#7B61FF",
    "risk_critical": "#FF3B3B",
    "risk_high":     "#FF8C00",
    "risk_medium":   "#FFD700",
    "risk_low":      "#00C851",
    "risk_safe":     "#00C851",
    "text_primary":  "#E8F4FD",
    "text_muted":    "#8892A4",
    "border":        "#1A2E4A",
    "border_glow":   "#1E90FF44",
}

# ─── Risk Thresholds ─────────────────────────────────────────────────────────
RISK_THRESHOLDS = {
    "critical": 0.85,   # >= 85 % → CRITICAL
    "high":     0.65,   # >= 65 % → HIGH
    "medium":   0.40,   # >= 40 % → MEDIUM / SUSPICIOUS
    "low":      0.15,   # >= 15 % → LOW
    "safe":     0.00,   # <  15 % → SAFE
}

# ─── History Settings ────────────────────────────────────────────────────────
MAX_HISTORY_RECORDS = 500
HISTORY_EXPORT_FIELDS = [
    "timestamp", "scan_type", "input_preview",
    "risk_level", "confidence", "label",
]

# ─── Streamlit Page Config ───────────────────────────────────────────────────
PAGE_CONFIG = {
    "page_title":   f"{APP_NAME} — {APP_SUBTITLE}",
    "page_icon":    APP_ICON,
    "layout":       "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        "Get Help":     None,
        "Report a bug": None,
        "About":        f"### {APP_NAME} v{APP_VERSION}\nAI-Powered Digital Threat Detection System",
    },
}

# ─── Sample Data (for UI demonstration) ──────────────────────────────────────
SAMPLE_SMS_TEXTS = [
    "URGENT: Your SBI net banking account has been locked due to pending KYC! Update immediately at http://sbi-card-kyc-update.top/netbanking to prevent account closure.",
    "Congratulations! You were randomly selected to win a $1000 Walmart gift card! Claim your free reward right now: http://free-iphone15-winner.xyz/claim?id=94821",
    "FINAL WARNING: An unpaid toll fee of $12.50 is recorded on your vehicle. Pay immediately to avoid court summons: http://toll-service-pay.xyz/bill",
    "Hey Sarah, are we still meeting for lunch tomorrow at 1 PM near the office?",
    "Your Amazon package #AMZ-4819 has shipped and will arrive on Friday. View tracking in your Amazon app.",
]

SAMPLE_URLS = [
    "http://paypa1-secure-login.tk/account/verify",
    "http://sbi-card-kyc-update.top/netbanking",
    "http://192.168.1.1/admin/login?redirect=http://evil.com",
    "https://www.google.com",
    "https://en.wikipedia.org/wiki/Cybersecurity",
    "https://www.amazon.com/dp/B09X4K9BSQ",
]

# ─── Tech Stack (for About page) ─────────────────────────────────────────────
TECH_STACK = [
    {"name": "Python 3.11",      "icon": "🐍", "role": "Core Language"},
    {"name": "Streamlit",        "icon": "🌊", "role": "Web Framework"},
    {"name": "Scikit-Learn",     "icon": "🤖", "role": "ML Models (Random Forest)"},
    {"name": "OpenCV",           "icon": "👁️",  "role": "QR Image Processing"},
    {"name": "Pandas",           "icon": "🐼", "role": "Data Manipulation"},
    {"name": "NumPy",            "icon": "🔢", "role": "Numerical Computing"},
    {"name": "Joblib",           "icon": "💾", "role": "Model Serialisation"},
    {"name": "Plotly",           "icon": "📊", "role": "Interactive Visualisations"},
    {"name": "pyzbar",           "icon": "📷", "role": "QR / Barcode Decoding"},
]
