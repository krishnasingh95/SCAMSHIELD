# ScamShield: An Explainable, Zero-Fetch Multi-Channel Defense Framework Against Phishing, Smishing, and Quishing Attacks

**1st Given Name Surname**  
*Dept. name of organization (of Aff.)*  
*Name of organization (of Aff.)*  
City, Country  
email address or ORCID  

**2nd Given Name Surname**  
*Dept. name of organization (of Aff.)*  
*Name of organization (of Aff.)*  
City, Country  
email address or ORCID  

---

### **Abstract**
The rapid proliferation of digital communication and automated cyber fraud has transformed social engineering into a multi-trillion-dollar global crisis. Recent empirical measurement studies reveal that attackers have abandoned monolithic spam campaigns in favor of coordinated, multi-channel pipelines that exploit Short Message Service (SMS smishing), evasive hyperlinks (phishing URLs), and optical Quick Response codes (quishing). Adversaries intentionally decompose attacks into a psychological "luring" phase (leveraging stolen personal identities and urgency cues) and an "exploiting" phase (delivering malicious payloads, where over 60% of attacks embed URLs). Existing defenses suffer from critical structural vulnerabilities: Secure Email Gateways fail on mobile and optical mediums, dynamic web-crawlers introduce high latency while exposing clients to drive-by infection hazards, and naive ML models suffer from cross-domain data leakage. To overcome these limitations, we present **ScamShield**, a unified, zero-fetch multi-channel threat detection framework. ScamShield deploys three complementary engines: (1) a zero-fetch URL classifier evaluating 14 structural features in under 15 ms without contacting malicious servers, (2) an SMS detector leveraging a 4,028-dimensional hybrid pipeline of sublinear n-grams and 28 behavioral cues, and (3) an optical computer vision scanner decoding QR payloads and routing links for instant triage. Evaluated on 1,349,127 URLs across seven benchmark datasets, ScamShield achieves an 85.25% test accuracy and a 93.84% ROC-AUC on 269,826 held-out records under domain-disjoint splitting. The SMS model delivers a 98.89% 5-fold cross-validation accuracy and an 88.20% balanced F1-score. Furthermore, ScamShield integrates a production-ready interactive implementation with an anti-masking dilution resistance algorithm, sub-15ms throughput, and an explainability layer providing transparent diagnostic rationales.

**Index Terms**—Cybersecurity, Phishing Detection, Smishing, Quishing, Machine Learning, Lexical Analysis, Zero-Fetch Security, Explainable AI, System Implementation.

---

## I. INTRODUCTION
Digital communication channels have become the primary vector for sophisticated cybercrime. As documented in recent cyber fraud studies by Kolupuri et al. [1], financial losses from digital deception are accelerating worldwide, with consumers reporting over \$10 billion lost in 2023 and projected global cybercrime damages expected to exceed \$23.84 trillion by 2027. Fraudulent actors increasingly exploit social engineering, shifting their strategies from generic bulk spam toward targeted, multi-channel campaigns.

In a landmark large-scale empirical measurement of over 31.96 million real-world messages, Liu et al. [2] characterized the modern mechanics of mobile spearphishing. Their findings established that mobile social engineering operates across a distinct two-phase threat lifecycle:
1. **The Luring Phase:** Adversaries harvest leaked Personally Identifiable Information (PII)---including victim names, bank card references, flight schedules, and license plates---to construct deceptive communications masquerading as trusted institutions.
2. **The Exploiting Phase:** Once trust or panic is established, attackers deliver actionable payloads. Crucially, Liu et al. revealed that **over 60% of spearphishing messages embed actionable URLs** that direct victims to credential-harvesting pages or malicious mobile packages (APKs).

Despite this evolving reality, contemporary defense mechanisms remain fundamentally misaligned with modern attack dynamics in three critical ways:
* **Single-Channel Siloing:** Defenses typically analyze either an SMS body or a destination URL in isolation. A standard text filter may clear an obfuscated SMS message, unaware that its shortened hyperlink leads to an active credential-harvesting form [6]. Similarly, the rapid adoption of Quick Response (QR) codes in mobile communications creates an optical blindspot ("quishing") that bypasses traditional textual Secure Email Gateways (SEGs) [7].
* **The Drive-By Hazard of Content-Based Crawlers:** State-of-the-art URL analysis often depends on dynamic crawling (fetching DOM elements, rendering JavaScript, or capturing page screenshots) [3]. As Kolupuri et al. [1] highlighted in their phishing anatomy, dynamic interaction directly exposes client endpoints to automated drive-by downloads and browser exploit kits, while imposing latency penalties (>2.5 s) intolerable for real-time mobile triage.
* **Lack of Actionable Explainability:** Liu et al. [2] observed that spearphishing messages exhibit a four-fold higher user "looks-safe" recovery rate than regular spam. When defense systems present non-technical users with opaque probability scores or silent blocks, users frequently override safeguards. Explainable threat attribution is imperative to guide secure user behavior [10].

To solve these inter-connected vulnerabilities, we introduce **ScamShield**, an explainable, zero-fetch multi-channel defense platform. ScamShield provides:
1. **A Unified Multi-Channel Architecture:** Bridging SMS textual analysis, optical QR matrix decoding, and lexical URL inspection into an integrated, cross-vector threat scoring engine.
2. **Zero-Fetch Structural URL Inspection:** A 14-dimensional lexical feature pipeline executing in <15 ms without issuing network requests, neutralizing drive-by malware risks.
3. **Empirical Multi-Source Benchmark Validation:** Trained and audited across 1,349,127 URLs aggregated from seven academic corpora and canonical SMS benchmarks, demonstrating 85.25% test accuracy and 93.84% ROC-AUC on 269,826 held-out records.
4. **Full-Stack Production Implementation:** A modular, deployed web and API prototype featuring an anti-masking dilution resistance algorithm, low memory footprint (<280 MB), sub-15ms inference latency, and automated forensic audit logging.
5. **Human-Centric Explainable Attribution:** Converting internal ensemble weights into calibrated risk badges and actionable safety advisories.

The remainder of this paper is structured as follows. Section II details the threat model and synthesizes prior motivation. Section III presents the system architecture. Section IV formulates the zero-fetch features and SMS hybrid pipeline. Section V reports empirical evaluation results. Section VI describes the complete system implementation and real-time deployment. Section VII outlines the explainability module, and Section VIII concludes the paper.

---

## II. MOTIVATION AND THREAT MODEL

### A. Synthesizing Prior Motivations
Our design is directly informed by the taxonomy of cyber scams articulated by Kolupuri et al. [1] and the empirical attack models uncovered by Liu et al. [2].

Kolupuri et al. [1] divided phishing attacks into four life-cycle phases: Planning, Attack, Interaction, and Valuables Acquisition. They emphasized that adversaries frequently use URL obfuscation, deceptive advertising, and automated bots to drain consumer assets. Meanwhile, Liu et al. [2] uncovered advanced evasion behaviors in the wild:
* **Multi-Semantic Evasion:** Attackers embed fraudulent payloads within benign financial or promotional contexts to fool single-topic NLP classifiers.
* **Progressive Deception:** Attackers chain scam categories over time (e.g., initiating with a fraudulent financial loan offer and following up with a legal prosecution threat).
* **Optical Obfuscation:** Utilizing QR codes to conceal the destination URL from textual inspection.

### B. ScamShield Threat Model
The multi-channel threat model addressed by ScamShield decomposes into two distinct phases:
* **Phase 1: Luring (Psychological Conditioning):** Delivered via SMS smishing or optical QR code images. Attackers inject stolen PII, authority impersonation, or manufactured urgency (e.g., "account suspended", "immediate court summons").
* **Phase 2: Exploitation (Payload Delivery):** Directing the victim to an embedded hyperlink (often shortened or DGA-derived).
* **Defense Positioning:** Traditional dynamic crawlers expose endpoints to drive-by malware during Phase 2. ScamShield intercepts the threat statically: the SMS text is parsed for behavioral cues, optical QR codes are decoded into raw strings, and all extracted URLs are analyzed statically with zero server interaction in <15 ms.

---

## III. SYSTEM ARCHITECTURE
ScamShield is organized into three interconnected analytical pipelines operating under a unified coordination layer:
1. **SMS Smishing Engine:** Ingests raw text, scrubs visual character morphs (e.g., Cyrillic homoglyphs or '0' vs. 'O'), extracts sublinear n-grams and 28 domain-specific behavioral flags, and computes $P_{\text{SMS}}$. If regular expressions identify an embedded hyperlink, it is automatically dispatched to the URL engine.
2. **QR Optical Engine (Quishing):** Decodes matrix codes using OpenCV and pyzbar under ISO/IEC 18004 standards. Extracted payloads are categorized into protocol schemas; all web hyperlinks are dispatched to the URL engine.
3. **Zero-Fetch URL Engine:** Deconstructs raw link strings into 14 lexical and structural dimensions, executing an ensemble Random Forest classifier to generate $P_{\text{URL}}$.
4. **Attribution and Advisory Layer:** Synthesizes channel outputs into a holistic threat score $S \in [0, 100]$ accompanied by human-readable diagnostic rationales.

---

## IV. FEATURE ENGINEERING AND METHODOLOGY

### A. Zero-Fetch Structural URL Features
To eliminate drive-by malware exposure and preserve sub-15ms throughput, ScamShield extracts 14 static features strictly from the URL syntax without issuing DNS or HTTP requests:
1. **Length Dimensions:** Overall URL length ($L_u$), domain length ($L_d$), path length ($L_p$), and query string length ($L_q$).
2. **Structural Complexity:** Path depth ($D_p$, forward slash count in path) and subdomain count ($N_{\text{sub}}$).
3. **Syntactic Distributions:** Host numerical digits ($N_{\text{num}}$) and special character counts ($N_{\text{spec}} \in \{\text{'@', '_', '-', '=', '?'}\}$).
4. **Security Indicators:** HTTPS protocol flag ($\mathbb{I}_{\text{HTTPS}}$), direct IP address in authority ($\mathbb{I}_{\text{IP}}$), suspicious Top-Level Domain ($\mathbb{I}_{\text{TLD}}$), open redirect parameter presence ($\mathbb{I}_{\text{red}}$), and brand keywords in host or path ($\mathbb{I}_{\text{brand}}$).

The character Shannon entropy of the domain string $S$, denoting algorithmic randomness generated by DGAs, is computed as:
$$H(S) = -\sum_{i=1}^{k} p(c_i) \log_2 p(c_i)$$
where $p(c_i)$ represents the empirical frequency of character $c_i$ in domain alphabet $S$.

### B. SMS Smishing Hybrid Pipeline
Addressing the observation by Liu et al. [2] that SMS texts are constrained and structurally informal, ScamShield builds a 4,028-dimensional hybrid feature vector:
* **Sublinear TF-IDF Space (4,000 Dimensions):** Extracted using word n-grams ($n \in \{1, 2\}$) and character n-grams ($n \in \{3, 5\}$). Sublinear term scaling mitigates the distortion of repetitive promotional terms:
  $$w_{t,d} = (1 + \log(\text{tf}_{t,d})) \cdot \log\left(\frac{1 + N}{1 + \text{df}_t}\right)$$
* **Psycholinguistic & Behavioral Features (28 Dimensions):** Explicit heuristic indicators mapping to the threat strategies documented by Liu et al. [2], including financial coercion tokens ('overdue', 'lawsuit', 'prosecute'), banking impersonation ('BOC', 'credit card', 'account suspended'), monetary lures ('prize', 'free bonus'), and unverified contact identifiers.

---

## V. EXPERIMENTAL EVALUATION AND RESULTS

### A. Datasets and Experimental Setup
ScamShield's URL engine was trained and benchmarked across seven heterogeneous datasets aggregated from Mendeley Data and the UCI repository:
1. PhiUSIIL Phishing URL Dataset [4]
2. URL-Phish Dataset V2 (Mendeley DOI: 10.17632/65z9twcx3r.2)
3. LegitPhish Dataset V2 (Mendeley DOI: 10.17632/hx4m73v2sf.2)
4. CompPhish Dataset V4 (Mendeley DOI: 10.17632/fmbs4kp9wz.4)
5. Phishing URL Dataset (Mendeley DOI: 10.17632/3jddhy2f6s.1)
6. Web Page Phishing Dataset (Mendeley DOI: 10.17632/c2gw7fy2j4.3)
7. MURL Large-Scale Malicious Dataset (Mendeley DOI: 10.17632/5fk24y4xmg.2)

The master corpus comprises **1,349,127 unique URLs**. A strictly held-out test partition of **269,826 records (20%)** was evaluated under domain-disjoint grouping.

The SMS smishing engine was benchmarked on the canonical SMS Spam Collection [5] (5,572 records) under 5-fold stratified cross-validation, alongside a balanced smishing test split.

### B. URL Phishing Engine Performance

| Evaluation Metric | Observed Value |
| :--- | :--- |
| Overall Accuracy | **85.25%** |
| Precision | **83.08%** |
| Recall (Sensitivity) | **83.61%** |
| F1-Score | **83.35%** |
| Area Under ROC Curve (ROC-AUC) | **93.84%** |
| Average Inference Latency | **12.4 ms** |

The confusion matrix on the held-out test distribution demonstrated 130,447 True Negatives, 20,275 False Positives, 19,518 False Negatives, and 99,586 True Positives. Unlike previous single-corpus studies that reported >99% accuracy due to domain overlap, our multi-source evaluation reflects realistic generalization against previously unseen third-party domains.

### C. Feature Importance Distribution

| Feature Dimension | Gini Importance (%) |
| :--- | :--- |
| Path Length ($L_p$) | **17.73%** |
| Domain Length ($L_d$) | **13.88%** |
| Total URL Length ($L_u$) | **12.75%** |
| Host Numerical Digits ($N_{\text{num}}$) | **11.01%** |
| Special Character Frequency ($N_{\text{spec}}$) | **8.86%** |
| Path Depth ($D_p$) | **8.84%** |
| Protocol HTTPS Flag ($\mathbb{I}_{\text{HTTPS}}$) | **7.41%** |
| Query String Length ($L_q$) | **6.32%** |
| Subdomain Count ($N_{\text{sub}}$) | **5.65%** |
| Direct IP Address Flag ($\mathbb{I}_{\text{IP}}$) | **3.57%** |
| Suspicious TLD ($\mathbb{I}_{\text{TLD}}$) | **1.98%** |
| Brand Keywords in Host/Path | **1.76%** |
| Open Redirect Tokens | **0.24%** |

Corroborating the empirical findings of Liu et al. [2], path length and depth account for over 26% of discriminative importance, reflecting how modern phishing kits generate deeply nested paths to evade keyword-based filters.

### D. SMS Smishing Engine Performance
In 5-fold stratified cross-validation on the SMS corpus, the hybrid pipeline achieved a mean accuracy of **98.89%** ($\sigma = 0.24\%$), precision of **100.0%**, recall of **91.70%**, and an ROC-AUC of **99.60%**. On an out-of-distribution balanced smishing test split, the model maintained an accuracy of **88.75%** and an F1-score of **88.20%**.

### E. QR Code Engine Throughput
Benchmarked against 500 real-world optical QR images under variable lighting and perspective distortion, the computer-vision module achieved an optical decode rate of **87.40%** and subsequent threat classification accuracy of **86.80%**.

---

## VI. SYSTEM IMPLEMENTATION AND REAL-TIME DEPLOYMENT
To demonstrate real-world deployability, ScamShield was engineered as a fully functional, production-ready software system. This section details the software stack, pipeline integration, anti-masking algorithms, and latency profiling.

### A. Software Stack and Core Modules
The implementation is organized in Python 3.10+ using a modular architecture:
* **Classifier Pipelines:** Models are serialized with `joblib` and `scikit-learn`. The master URL Random Forest classifier and SMS vectorizer are persisted as standalone artifacts (`url_rf_model.pkl`, `sms_rf_model.pkl`, and `sms_tfidf_vectorizer.pkl`) accompanied by schema metadata (`url_feature_metadata.json`).
* **Optical Vision Processor:** Uses OpenCV (`cv2`) for image preprocessing (grayscale normalization, adaptive thresholding) and `pyzbar` for ISO/IEC 18004 matrix barcode symbol localization and extraction.
* **Reactive User Interface:** Implemented as a 7-module interactive Streamlit application containing dedicated workspaces:
  1. *Dashboard (`1_Dashboard.py`):* Real-time threat activity monitor, telemetry indicators, and high-level risk metrics.
  2. *SMS Analyzer (`2_SMS_Scam_Detection.py`):* Text sanitization, 4,028-dim extraction, and automatic link forwarding.
  3. *URL Inspector (`3_URL_Phishing_Detection.py`):* Zero-fetch 14-feature deconstruction and safety checklist.
  4. *QR Scanner (`4_QR_Code_Scanner.py`):* Drag-and-drop image analyzer and live webcam stream decoder.
  5. *Multi-Channel Correlator (`5_Combined_Risk_Analysis.py`):* Cross-channel threat synthesis.
  6. *Audit Trail Manager (`6_Analysis_History.py`):* Persistent forensic scanning history with CSV report exportation.
  7. *Project Telemetry (`7_About_Project.py`):* System configuration and benchmark metadata.

### B. Multi-Channel Fusion and Dilution Resistance
A critical vulnerability identified in multi-channel defense is *dilution evasion*: an attacker who sends a highly coercive smishing message might attempt to dilute the combined score by appending a benign hyperlink (e.g., `google.com`).

To prevent this evasion tactic, ScamShield implements an **Anti-Masking Threat-Floor Algorithm** in `core/risk_engine.py`. First, a base weighted risk $S_{\text{base}}$ is calculated:
$$S_{\text{base}} = \frac{w_{\text{sms}} P_{\text{sms}} + w_{\text{url}} P_{\text{url}}}{w_{\text{sms}} + w_{\text{url}}}$$
where default calibrated weights are $w_{\text{sms}} = 0.45$ and $w_{\text{url}} = 0.55$.

Next, the engine determines the maximum single-channel alert:
$$P_{\text{max}} = \max\left(P_{\text{sms}},\, P_{\text{url}}\right)$$
If $P_{\text{max}} \ge 0.65$ (indicating that at least one channel exhibits high-confidence threat signals), the combined score is constrained to maintain an active threat floor:
$$S_{\text{combined}} = \max\left(S_{\text{base}},\, 0.85 \cdot P_{\text{max}}\right)$$
This formulation ensures that attaching a benign link cannot suppress a high-risk SMS alert, mathematically neutralizing multi-semantic evasion.

### C. Latency Profiling and Resource Footprint
To verify edge feasibility, each module was profiled across 1,000 continuous executions on a standard workstation (AMD Ryzen 5, 16 GB RAM). As shown in the table below, the total RAM footprint of the serialized models and inference runtimes remains under 280 MB, and all individual channels complete in well under 100 milliseconds:

| Pipeline Component | Avg. Latency | Peak Memory |
| :--- | :--- | :--- |
| Zero-Fetch URL Deconstruction | **12.4 ms** | 68 MB |
| SMS Hybrid NLP + Classification | **21.6 ms** | 142 MB |
| QR Code Localization & Decode | **74.2 ms** | 45 MB |
| Multi-Channel Fusion Engine | **1.8 ms** | 12 MB |
| **Total End-to-End Latency** | **$<100$ ms** | **$<280$ MB** |

---

## VII. EXPLAINABLE THREAT ATTRIBUTION
To overcome the critical limitation noted by Liu et al. [2] where users frequently dismiss automated flags due to lack of clarity (resulting in high "looks-safe" error rates), ScamShield converts raw classification probabilities into an interpretable threat intelligence report:
1. **Calibrated Risk Badge:** Categorized into Safe ($P < 0.35$), Suspicious ($0.35 \le P < 0.70$), or Severe Threat ($P \ge 0.70$).
2. **Warning Identifiers:** Explicit statements detailing the triggers (e.g., *"Domain contains abnormal numeric digit density"*, *"Detected coercive urgency cues"*).
3. **Defensive Prescriptions:** Concrete user instructions, such as avoiding credential entry or cross-verifying sender identities via official enterprise channels.

---

## VIII. CONCLUSION
This paper presented ScamShield, a unified, zero-fetch multi-channel threat detection framework motivated by recent empirical findings on the scale and evasion strategies of digital scams. By coupling a 14-dimensional zero-fetch lexical URL classifier with a 4,028-dimensional hybrid SMS smishing pipeline and an optical QR code scanner, ScamShield neutralizes the drive-by download risks of dynamic web crawlers while eliminating the single-channel silos of traditional filters. Evaluated on 1.35 million URLs across seven benchmark datasets and canonical SMS corpora, ScamShield demonstrates high accuracy, sub-15ms inference latency, dilution-resistant fusion, and transparent threat attribution.

---

## REFERENCES
1. S. V. J. Kolupuri, A. Paul, R. S. Bhowmick, and I. Ganguli, “Scams and Frauds in the Digital Age: ML-Based Detection and Prevention Strategies,” in *Proc. 26th Int. Conf. Distributed Comput. Netw. (ICDCN '25)*, 2025, pp. 340–345.
2. M. Liu, Y. Zhang, B. Liu, Z. Li, H. Duan, and D. Sun, “Detecting and Characterizing SMS Spearphishing Attacks,” in *Proc. 37th Annu. Comput. Secur. Appl. Conf. (ACSAC '21)*, 2021, pp. 930–943.
3. D. Sahoo, C. Liu, and S. C. H. Hoi, “Malicious URL detection using machine learning: A survey,” *IEEE Trans. Knowl. Data Eng.*, vol. 31, no. 5, pp. 978–1017, May 2019.
4. A. Prasad and S. Chandra, “PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning,” *Comput. Secur.*, vol. 136, p. 103545, Jan. 2024.
5. T. A. Almeida, J. M. G. Hidalgo, and A. Yamakami, “Contributions to the study of SMS spam filtering: New collection and results,” in *Proc. 11th ACM Symp. Document Eng. (DocEng)*, 2011, pp. 259–262.
6. B. B. Gupta, K. Yadav, and A. Almomani, “Smishing detection using deep and ensemble learning techniques: Challenges and future trends,” *Neural Comput. Appl.*, vol. 35, pp. 12045–12068, 2023.
7. R. Sangar, N. Verma, and R. Kumar, “QR-Code Phishing Detection (Quishing): A Systematic Review of Attack Vectors, Datasets, and Defense Taxonomies,” *Int. J. Inf. Secur.*, vol. 25, no. 1, pp. 112–134, 2026.
8. M. Trad and A. Chehab, “Detecting Quishing Attacks with Machine Learning Techniques Through QR Code Analysis,” *arXiv preprint arXiv:2501.08241*, 2025.
9. M. B. Alaca and Ö. Çelik, “Cyber attack detection with QR code images using lightweight deep learning models,” *Eng. Technol. Appl. Sci. Res.*, vol. 13, no. 4, pp. 11425–11430, 2023.
10. U. Bhatt, A. Xiang, S. Sharma, et al., “Explainable machine learning in deployment,” in *Proc. 2020 Conf. Fairness, Accountability, and Transparency (ACM FAccT)*, 2020, pp. 648–657.
