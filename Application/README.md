# 🛡️ ScamShield — Application Suite

**AI-Powered Digital Threat Detection & Risk Assessment System**  
*College Capstone AIML Project | Python 3.10+ · Streamlit · Scikit-Learn · OpenCV*

---

## 📌 Overview

**ScamShield** is a multi-channel cybersecurity defense platform designed to protect users against modern social engineering attacks:
1. **💬 SMS Smishing Detection:** Evaluates messages using a 4,028-dimensional pipeline combining sublinear word n-grams, character n-grams, and 28 behavioral signals (financial cues, manufactured urgency, threat keywords).
2. **🌐 URL Phishing Detection:** Decomposes links into 14 structural features in <15ms without fetching web content (preventing drive-by malware). Trained on **1.35 Million URLs** across 7 independent datasets with **85.25% test accuracy** and **93.84% ROC-AUC**.
3. **📷 QR Code Scanner (Anti-Quishing):** Decodes optical QR matrices via OpenCV and pyzbar, analyzes the embedded payload, and routes it to the appropriate detection engine.
4. **🤖 AI Explanation Layer:** Translates raw machine learning probability scores into plain-English reasoning, red-flag warning indicators, and actionable safety tips.
5. **📊 Audit Trail & History:** Logs all scans with timestamps, risk ratings, confidence values, and offers CSV export.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.10** or **3.11** installed.

### 2. Setup Virtual Environment
```bash
# Navigate to Application directory
cd Application

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Environment Variables
Copy `.env.example` to `.env` if you wish to configure the optional AI reasoning layer:
```bash
copy .env.example .env
```

### 5. Launch Application
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 📁 Application Directory Structure

```
Application/
├── app.py                  # Main entry point (redirects to Dashboard)
├── config.py               # Global design tokens, risk thresholds, and metadata
├── requirements.txt        # Python dependency manifest
├── .env.example            # Environment variables template
├── core/                   # Core business & threat inference logic
│   ├── sms_analyzer.py     # SMS TF-IDF & Random Forest inference (v2.1)
│   ├── url_analyzer.py     # URL structural feature extraction & inference (v2.1)
│   ├── qr_analyzer.py      # OpenCV image processing & optical QR decoding
│   ├── ai_analyzer.py      # AI explainability & risk breakdown layer
│   ├── history_manager.py  # Session log manager & CSV export
│   └── risk_engine.py      # Composite multi-vector scoring
├── models/                 # Serialized production models
│   ├── sms_rf_model.pkl    # Retrained SMS Random Forest model
│   ├── sms_tfidf_vectorizer.pkl # FeatureUnion text vectorizer
│   ├── sms_feature_metadata.pkl # 28-feature metadata schema
│   ├── url_rf_model.pkl    # 1.35M dataset URL Random Forest model
│   └── url_feature_metadata.json # 14-feature URL metadata
├── pages/                  # Streamlit Multi-Page UI
│   ├── 1_Dashboard.py      # Threat analytics & global metrics
│   ├── 2_SMS_Scam_Detection.py # Text message scanner & radar charts
│   ├── 3_URL_Phishing_Detection.py # Structural link inspector
│   ├── 4_QR_Code_Scanner.py # Optical code upload & evaluation
│   ├── 5_Combined_Risk_Analysis.py # Multi-signal aggregation
│   ├── 6_Analysis_History.py # Historical audit logs & CSV export
│   └── 7_About_Project.py  # System architecture & model statistics
├── ui/                     # UI components, dark-mode CSS, radar charts, sidebar
└── utils/                  # Feature extractors, validators, logging
```

---

## 📊 Application Pages Overview

| # | Page | Capabilities |
|---|---|---|
| **1** | **Dashboard** | Real-time threat counters, risk level distributions, and quick status overview. |
| **2** | **SMS Scam Detection** | Interactive text analysis, sample attack library, keyword pill tags, and feature radar chart. |
| **3** | **URL Phishing Detection** | URL decomposition (Scheme, Host, TLD), 14 structural flags, and confidence indicators. |
| **4** | **QR Code Scanner** | Image drag-and-drop, OpenCV adaptive thresholding, payload routing, and threat verdict. |
| **5** | **Combined Risk Analysis** | Evaluates compound multi-channel attacks (e.g. SMS message containing an embedded URL). |
| **6** | **Analysis History** | Filterable history table, individual record inspection, and one-click CSV export. |
| **7** | **About Project** | Complete breakdown of datasets, academic methodology, and engineering credits. |

---

## 🛡️ Model Specifications

* **URL Model (v2.1.0):**
  * Training Volume: **1,349,127 URLs** across 7 Mendeley & benchmark corpora.
  * Held-Out Test Evaluation: **85.25% Accuracy**, **93.84% ROC-AUC**.
  * Features: 14 structural metrics (zero network socket call required).
* **SMS Model (v2.1.0):**
  * Architecture: `FeatureUnion` (4,000 TF-IDF features) + 28 Heuristic Domain Indicators.
  * Balanced Benchmark Performance: **88.75% Accuracy**, **88.20% F1-Score**, **87.50% Recall**.
* **QR Code Scanner:**
  * Vision Pipeline: OpenCV Gaussian Binarization + pyzbar optical matrix decoding.
  * Benchmark Performance: **87.40% Optical Decoding Rate**, **86.80% End-to-End Threat Accuracy**.
