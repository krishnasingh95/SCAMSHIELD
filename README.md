# 🛡️ ScamShield

**AI-Powered Digital Threat Detection & Risk Assessment System**  
*An end-to-end multi-channel defense platform for detecting Phishing URLs, Smishing Messages, and Malicious QR Codes.*

---

## 📌 Project Summary

**ScamShield** addresses modern social engineering attacks that bypass conventional static firewalls. It provides an automated, multi-channel cyber-defense pipeline:
- **💬 SMS Smishing Detection:** Hybrid 4,028-dimensional pipeline combining sublinear word n-grams, character n-grams, and 28 behavioral signals (financial cues, manufactured urgency, threat words).
- **🌐 URL Phishing Detection:** Decomposes links into 14 structural features in <15ms without fetching live web content (zero drive-by download risk). Trained on **1.35 Million URLs** across 7 independent benchmark datasets (**85.25% test accuracy**, **93.84% ROC-AUC**).
- **📷 QR Code Scanner (Quishing):** Decodes optical QR codes using OpenCV and pyzbar, identifies payload types, and dispatches them to downstream classifiers.
- **🤖 Explainable Threat Intelligence:** Converts raw numerical classification probabilities into transparent, human-readable explanations, warning signs, and defensive advice.

---

## 🚀 Quick Start Guide

### 1. Installation
Ensure Python 3.10 or 3.11 is installed.

```bash
# Clone or navigate to the repository
cd ScamShield/Application

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Application
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

## 📂 Project Structure

```
ScamShield/
├── Application/                   # Production Streamlit Web Application
│   ├── app.py                     # Application entry point
│   ├── config.py                  # Global configurations & thresholds
│   ├── requirements.txt           # Python package dependencies
│   ├── .env.example               # Environment variables template
│   ├── core/                      # Business logic & threat engines (SMS, URL, QR, AI)
│   ├── models/                    # Deployed production models & vectorizers
│   ├── pages/                     # 7 Multi-Page Streamlit modules
│   ├── ui/                        # Reusable cards, themes, charts, and navigation
│   └── utils/                     # Feature extraction & validation helpers
│
├── Training/                      # Model Training, Datasets & Benchmarks
│   ├── datasets/                  # Raw & processed multi-source corpora
│   │   ├── raw/                   # SMSSpamCollection, PhiUSIIL raw benchmarks
│   │   └── v2/                    # 1.35M URL multi-dataset master features
│   ├── Models/                    # Serialized training outputs & metadata
│   ├── notebooks/                 # Training Jupyter notebooks & ablation scripts
│   ├── Reports/                   # Detailed cross-validation JSON evaluation reports
│   ├── retrain_sms_v2.py          # SMS model production training script
│   ├── retrain_url_v2.py          # URL model training & evaluation script
│   └── generate_presentation.py   # PowerPoint presentation generator
│
├── ScamShield_Academic_Presentation.pptx # Final 10-slide academic presentation
├── ScamShield_Final_Presentation.pptx    # Alternate presentation copy
└── README.md                      # Top-level project documentation
```

---

## 📊 Empirical Evaluation Summary

| Threat Vector | Training Scale | Evaluation Strategy | Performance Metrics |
| :--- | :--- | :--- | :--- |
| **URL Phishing Engine** | **1,349,127 URLs** (7 Datasets) | 269,826 Held-Out Records | **85.25% Accuracy** \| **93.84% ROC-AUC** |
| **SMS Scam Engine** | 4,028 Hybrid Dimensions | Balanced Smishing Benchmark | **88.75% Accuracy** \| **88.20% F1-Score** |
| **QR Code Engine** | OpenCV Optical Vision | Real-World Image Benchmark | **87.40% Decode Rate** \| **86.80% Threat Accuracy** |

---

## 🎯 Academic Presentation
A complete, 10-slide presentation matching academic evaluation criteria is available in the project root:
📁 **[`ScamShield_Academic_Presentation.pptx`](ScamShield_Academic_Presentation.pptx)**

Topics covered:
1. Title & Problem Statement
2. Objectives & Scope
3. Methodology & System Pipeline
4. Project Timeline & Milestones
5. Technical Resources & Zero-Fetch Risk Mitigation
6. Scaled Empirical Findings (1.35M URLs)
7. Application Walkthrough & Architecture
8. Limitations, Future Roadmap, and References
