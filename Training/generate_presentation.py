"""
ScamShield — Professional Academic Presentation Generator (16:9 Widescreen)
=============================================================================
Built strictly according to standard academic guidelines:
1. Title and Introduction
2. Problem Statement
3. Objectives and Scope
4. Methodology / Architecture & Technologies
5. Timeline and Milestones
6. Resources, Tools, and Risk Mitigation
7. Results & Verified Accuracies (Prominently Featured)
8. Application Prototype (Dashboard & SMS Scanner Screenshots)
9. Application Prototype (URL Inspector & QR Scanner Screenshots)
10. Limitations and Future Work
11. Conclusion and References

Theme: Clean, high-contrast academic light theme with deep navy & royal blue accents.
Typography: Significantly increased font sizes for maximum legibility.
Screenshots: Real, live application captures embedded directly onto slides.
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "ScamShield_Presentation_v2.pptx"
ACADEMIC_FILE = Path(__file__).resolve().parent.parent / "ScamShield_Academic_Presentation.pptx"
FINAL_FILE = Path(__file__).resolve().parent.parent / "ScamShield_Final_Presentation.pptx"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "Application" / "assets"

# ── Color Palette (Academic Executive Light Theme) ───────────────────────────
C_BG        = RGBColor(248, 250, 252)   # #F8FAFC Clean off-white
C_CARD      = RGBColor(255, 255, 255)   # #FFFFFF Crisp white card fill
C_CARD_HI   = RGBColor(241, 245, 249)   # #F1F5F9 Highlight card fill
C_BORDER    = RGBColor(203, 213, 225)   # #CBD5E1 Card border
C_NAVY      = RGBColor(15, 32, 66)      # #0F2042 Deep Executive Navy
C_BLUE      = RGBColor(29, 78, 216)     # #1D4ED8 Royal Blue Accent
C_TEAL      = RGBColor(2, 132, 199)     # #0284C7 Cyber Teal
C_GREEN     = RGBColor(22, 163, 74)     # #16A34A Verified Emerald Green
C_RED       = RGBColor(220, 38, 38)     # #DC2626 Warning Red
C_TEXT_MAIN = RGBColor(15, 23, 42)      # #0F172A Primary Dark Slate Text
C_TEXT_MUTED= RGBColor(71, 85, 105)     # #475569 Secondary Slate Text

FONT_HEAD = "Segoe UI"
FONT_BODY = "Segoe UI"

prs = pptx.Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]


def create_slide(category: str, title: str, subtitle: str = ""):
    """Creates a base slide with academic styling, top accent bar, and large headers."""
    slide = prs.slides.add_slide(blank_layout)

    # Clean light background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()

    # Top royal blue accent bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_BLUE
    top_bar.line.fill.background()

    # Category Eyebrow
    if category:
        pill = slide.shapes.add_textbox(Inches(0.9), Inches(0.42), Inches(11), Inches(0.4))
        p = pill.text_frame.paragraphs[0]
        p.text = category.upper()
        p.font.name = FONT_HEAD
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_BLUE

    # Slide Title
    t_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.78), Inches(11.5), Inches(0.7))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEAD
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY

    # Subtitle
    if subtitle:
        s_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.48), Inches(11.5), Inches(0.45))
        tf_s = s_box.text_frame
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(15)
        p_s.font.color.rgb = C_TEXT_MUTED

    return slide


def add_card(slide, left, top, width, height, title="", title_color=C_NAVY, bg_color=C_CARD, border_color=C_BORDER):
    """Draws a clean, high-contrast card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if title:
        tb = slide.shapes.add_textbox(Inches(left + 0.3), Inches(top + 0.22), Inches(width - 0.6), Inches(0.5))
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEAD
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = title_color

    return card


# =============================================================================
# SLIDE 1: TITLE AND INTRODUCTION
# =============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg1.fill.solid()
bg1.fill.fore_color.rgb = C_NAVY
bg1.line.fill.background()

top_bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.14))
top_bar1.fill.solid()
top_bar1.fill.fore_color.rgb = C_TEAL
top_bar1.line.fill.background()

tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p_eyebrow = tf1.paragraphs[0]
p_eyebrow.text = "AIML CAPSTONE PROJECT  •  CYBER DEFENSE & THREAT INTELLIGENCE"
p_eyebrow.font.name = FONT_HEAD
p_eyebrow.font.size = Pt(14)
p_eyebrow.font.bold = True
p_eyebrow.font.color.rgb = C_TEAL
p_eyebrow.space_after = Pt(20)

p_title = tf1.add_paragraph()
p_title.text = "ScamShield"
p_title.font.name = FONT_HEAD
p_title.font.size = Pt(50)
p_title.font.bold = True
p_title.font.color.rgb = RGBColor(255, 255, 255)
p_title.space_after = Pt(14)

p_sub = tf1.add_paragraph()
p_sub.text = "AI-Powered Digital Threat Detection & Risk Assessment System"
p_sub.font.name = FONT_HEAD
p_sub.font.size = Pt(24)
p_sub.font.bold = True
p_sub.font.color.rgb = RGBColor(226, 232, 240)
p_sub.space_after = Pt(22)

p_hook = tf1.add_paragraph()
p_hook.text = "An intelligent multi-channel platform to detect and neutralize Phishing URLs, SMS Scams,\nand Malicious QR Codes in real-time before users interact with dangerous payloads."
p_hook.font.name = FONT_BODY
p_hook.font.size = Pt(16)
p_hook.font.color.rgb = RGBColor(148, 163, 184)


# =============================================================================
# SLIDE 2: PROBLEM STATEMENT
# =============================================================================
s2 = create_slide(
    "01 / Problem Statement",
    "Digital Deception In Everyday Communications",
    "Modern social engineering attacks target users across three everyday interaction vectors."
)

col_w = 3.65
# Card 1: SMS Smishing
add_card(s2, 0.9, 2.05, col_w, 4.8, "💬 SMS Smishing", C_RED)
tb = s2.shapes.add_textbox(Inches(1.15), Inches(2.75), Inches(col_w - 0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Deceptive Messages & Bank Spoofing"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(15)
tf.paragraphs[0].font.color.rgb = C_NAVY
pts_sms = [
    "Attackers send fake KYC, lottery wins, and account suspension alerts.",
    "Bypasses standard telecom filters using lookalike text and keyword evasion.",
    "Coerces victims with extreme urgency to elicit quick panic reactions."
]
for pt in pts_sms:
    p = tf.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEXT_MUTED
    p.space_before = Pt(10)

# Card 2: Phishing URLs
add_card(s2, 4.85, 2.05, col_w, 4.8, "🌐 Phishing URLs", C_BLUE)
tb = s2.shapes.add_textbox(Inches(5.1), Inches(2.75), Inches(col_w - 0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Credential Harvesting Domains"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(15)
tf.paragraphs[0].font.color.rgb = C_NAVY
pts_url = [
    "Lookalike domains mimicking legitimate banks and brands (e.g. paypa1.com).",
    "Abuses cheap, obscure TLDs (.tk, .xyz, .top) and multiple redirection chains.",
    "Traditional static security blacklists fail against zero-day phishing sites."
]
for pt in pts_url:
    p = tf.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEXT_MUTED
    p.space_before = Pt(10)

# Card 3: QR Phishing (Quishing)
add_card(s2, 8.8, 2.05, col_w, 4.8, "📷 Quishing (QR Codes)", C_NAVY)
tb = s2.shapes.add_textbox(Inches(9.05), Inches(2.75), Inches(col_w - 0.5), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Invisible Optical Traps"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(15)
tf.paragraphs[0].font.color.rgb = C_NAVY
pts_qr = [
    "QR codes placed on parking meters, flyers, tables, and email attachments.",
    "Humans cannot visually inspect or verify where a QR code leads before scanning.",
    "Instantly launches phishing links or rogue payment prompts upon mobile scan."
]
for pt in pts_qr:
    p = tf.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEXT_MUTED
    p.space_before = Pt(10)


# =============================================================================
# SLIDE 3: OBJECTIVES AND SCOPE
# =============================================================================
s3 = create_slide(
    "02 / Objectives & Scope",
    "Project Objectives & Operational Boundaries",
    "Defines the system goals, supported deliverables, and operational boundaries."
)

# Left: Objectives
add_card(s3, 0.9, 2.05, 5.6, 4.8, "🎯 Core Objectives", C_BLUE)
tb = s3.shapes.add_textbox(Inches(1.2), Inches(2.75), Inches(5.0), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
objs = [
    ("Unified Multi-Channel System", "Analyze SMS messages, URLs, and QR codes through one integrated application."),
    ("Zero-Fetch Structural URL Safety", "Compute 14 URL indicators purely from string structure without fetching web content (eliminating drive-by download risks)."),
    ("Scaled Real-World Training", "Train on over 1.35 million verified data samples for reliable generalization."),
    ("Actionable Visual Risk Guidance", "Deliver clear, colored risk levels and radar breakdowns rather than opaque numbers.")
]
for t, d in objs:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "✔ " + t
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = d
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED

# Right: Scope
add_card(s3, 6.85, 2.05, 5.6, 4.8, "📋 Scope Specification", C_NAVY)
tb = s3.shapes.add_textbox(Inches(7.15), Inches(2.75), Inches(5.0), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True
scopes = [
    ("IN SCOPE: SMS Threat Analysis", "4,028 NLP features combining word n-grams, character n-grams, and 28 behavioral signals."),
    ("IN SCOPE: Structural URL Inspection", "14 lexical and structural domain parameters analyzed in under 15ms."),
    ("IN SCOPE: Optical QR Processing", "OpenCV image preprocessing, binarization, optical decoding, and automated routing."),
    ("OUT OF SCOPE: Network Packet Sniffing", "System evaluates user-submitted input; does not run passive background hardware packet capture.")
]
for t, d in scopes:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "• " + t
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = d
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 4: SYSTEM ARCHITECTURE & TECHNOLOGIES
# =============================================================================
s4 = create_slide(
    "03 / Architecture & Technologies",
    "System Architecture & Technology Stack",
    "Full technical stack and four-tier pipeline architecture powering ScamShield."
)

# Left Box: Tech Stack Breakdown
add_card(s4, 0.9, 2.05, 4.8, 4.8, "🛠️ Technologies Used", C_BLUE)
tb = s4.shapes.add_textbox(Inches(1.15), Inches(2.75), Inches(4.3), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

tech_list = [
    ("Core Language", "Python 3.10 / 3.11", C_NAVY),
    ("Web Framework", "Streamlit (Multi-Page Reactive UI)", C_BLUE),
    ("Machine Learning", "Scikit-Learn (Random Forest, TF-IDF)", C_TEAL),
    ("Computer Vision", "OpenCV & pyzbar (QR Binarization)", C_NAVY),
    ("Data Processing", "Pandas & NumPy (Vector Transforms)", C_BLUE),
    ("Visualizations", "Plotly (Interactive Radar & Gauges)", C_TEAL),
    ("Serialization", "Joblib (Optimized Model Deployment)", C_NAVY)
]
for role, name, col in tech_list:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = f"• {role}: "
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = col
    p.space_before = Pt(4)
    p2 = tf.add_paragraph()
    p2.text = f"   {name}"
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_MUTED

# Right Box: 4-Tier Pipeline Architecture
add_card(s4, 6.0, 2.05, 6.45, 4.8, "🏗️ Multi-Tier Architecture Pipeline", C_NAVY)
tb = s4.shapes.add_textbox(Inches(6.25), Inches(2.75), Inches(5.95), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

arch_tiers = [
    ("1. Presentation Tier (Streamlit Web App)", "Multi-page responsive frontend with dark-mode theme, drag-and-drop file uploaders, and interactive input forms."),
    ("2. Preprocessing & Vision Tier (OpenCV / pyzbar)", "Extracts optical QR payloads via adaptive thresholding; performs lexical URL decomposition and NLP text sanitization."),
    ("3. Threat Inference Tier (Random Forest Ensembles)", "Runs 200-300 tree class-balanced classifiers on extracted feature vectors to calculate threat probabilities in milliseconds."),
    ("4. Risk Assessment & Audit Tier", "Synthesizes multi-signal confidence scores into unified risk tiers (Safe to Critical) and logs persistent JSON audit history.")
]
for title, desc in arch_tiers:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = title
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(6)
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 5: TIMELINE AND MILESTONES
# =============================================================================
s5 = create_slide(
    "04 / Project Timeline",
    "Development Phases & Key Milestones",
    "Structured project progression from initial literature review to production deployment."
)

milestones = [
    ("Phase 1: Research, Audit & Benchmark Sourcing", "Weeks 1 - 2", "Reviewed academic smishing & phishing publications; acquired multi-source benchmarks from Mendeley Data and UCI repository."),
    ("Phase 2: Scaled Dataset Pipeline (1.35M Records)", "Weeks 3 - 4", "Preprocessed 1,349,127 URL samples across 7 diverse repositories; extracted 14 structural features and built stratified splits."),
    ("Phase 3: Model Architecture & Cross-Validation", "Weeks 5 - 6", "Built 4,028-feature SMS pipeline; trained class-balanced Random Forest models using Stratified 5-Fold Cross-Validation."),
    ("Phase 4: Streamlit UI, QR Vision & Verification", "Weeks 7 - 8", "Integrated OpenCV optical QR decoding; built interactive Streamlit multi-page interface; verified end-to-end performance.")
]

y_start = 2.05
for i, (title, duration, desc) in enumerate(milestones):
    card_y = y_start + (i * 1.25)
    add_card(s5, 0.9, card_y, 11.55, 1.05, "", C_NAVY)

    tb = s5.shapes.add_textbox(Inches(1.2), Inches(card_y + 0.15), Inches(11.0), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = f"{title}   [{duration}]"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = C_NAVY

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED
    p2.space_before = Pt(4)


# =============================================================================
# SLIDE 6: RESOURCES & RISK MITIGATION
# =============================================================================
s6 = create_slide(
    "05 / Resources & Mitigation",
    "Resource Requirements & Strategic Safeguards",
    "Detailed accounting of technical requirements and proactive architectural safeguards."
)

# Left: Technical Requirements
add_card(s6, 0.9, 2.05, 5.6, 4.8, "💻 System Requirements", C_BLUE)
tb = s6.shapes.add_textbox(Inches(1.2), Inches(2.75), Inches(5.0), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

sys_reqs = [
    ("Compute & Runtime", "Standard multi-core CPU (Intel i5/AMD Ryzen or higher), 4GB+ RAM, Python 3.10+."),
    ("Storage Allocation", "Lightweight runtime footprint (<500MB total) including all serialized models and vectorizers."),
    ("Network Independence", "Full offline operational capability — zero dependence on third-party live DNS blacklists."),
    ("Operating System Support", "Cross-platform compatibility (Windows, macOS, Linux).")
]
for t, d in sys_reqs:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "• " + t
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = d
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED

# Right: Risk Mitigations
add_card(s6, 6.85, 2.05, 5.6, 4.8, "🛡️ Operational Risk Mitigation", C_NAVY)
tb = s6.shapes.add_textbox(Inches(7.15), Inches(2.75), Inches(5.0), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

mitigations = [
    ("Risk: Drive-By Malware Execution", "Mitigation: Zero-fetch string evaluation parses lexical indicators without opening socket connections to untrusted domains."),
    ("Risk: Adversarial Text Obfuscation", "Mitigation: Character n-grams (`char_wb`) paired with sublinear word tokens detect symbol substitutions and typosquats."),
    ("Risk: Distorted or Skewed QR Photos", "Mitigation: OpenCV adaptive Gaussian binarization cleans shadows and low-contrast optical matrices prior to decoding.")
]
for t, d in mitigations:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "✔ " + t
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_GREEN
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = d
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 7: RESULTS & EMPIRICAL ACCURACY (PROMINENT ACCURACY METRICS!)
# =============================================================================
s7 = create_slide(
    "06 / Results & Accuracy",
    "Verified Performance & Model Evaluation",
    "Rigorous empirical evaluation confirms high precision, recall, and ROC-AUC across all modules."
)

col3_w = 3.65
# Card 1: URL Accuracy
add_card(s7, 0.9, 2.05, col3_w, 4.8, "🌐 URL Phishing Detector", C_BLUE)
tb = s7.shapes.add_textbox(Inches(1.1), Inches(2.75), Inches(col3_w - 0.4), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

p_acc = tf.paragraphs[0]
p_acc.text = "85.25%"
p_acc.font.bold = True
p_acc.font.size = Pt(36)
p_acc.font.color.rgb = C_BLUE
p_lbl = tf.add_paragraph()
p_lbl.text = "Test Accuracy (269,826 Records)"
p_lbl.font.size = Pt(13)
p_lbl.font.color.rgb = C_TEXT_MUTED
p_lbl.space_after = Pt(12)

url_stats = [
    ("93.84%", "ROC-AUC Score (High Separability)"),
    ("1,349,127", "Total Dataset Scale (7 Repositories)"),
    ("14 Features", "Extracted in <15ms without web fetch"),
    ("200 Trees", "Class-Balanced Random Forest")
]
for val, lbl in url_stats:
    p = tf.add_paragraph()
    p.text = f"✔ {val} — {lbl}"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)

# Card 2: SMS Accuracy
add_card(s7, 4.85, 2.05, col3_w, 4.8, "💬 SMS Scam Detector", C_GREEN)
tb = s7.shapes.add_textbox(Inches(5.05), Inches(2.75), Inches(col3_w - 0.4), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

p_acc2 = tf.paragraphs[0]
p_acc2.text = "88.75%"
p_acc2.font.bold = True
p_acc2.font.size = Pt(36)
p_acc2.font.color.rgb = C_GREEN
p_lbl2 = tf.add_paragraph()
p_lbl2.text = "Balanced Benchmark Accuracy"
p_lbl2.font.size = Pt(13)
p_lbl2.font.color.rgb = C_TEXT_MUTED
p_lbl2.space_after = Pt(12)

sms_stats = [
    ("88.20%", "Balanced Test F1-Score"),
    ("87.50%", "Recall (Consistently catches attacks)"),
    ("94.10%", "ROC-AUC Discriminative Score"),
    ("4,028 Dims", "Word + Char TF-IDF + 28 Heuristics")
]
for val, lbl in sms_stats:
    p = tf.add_paragraph()
    p.text = f"✔ {val} — {lbl}"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)

# Card 3: QR Optical Accuracy
add_card(s7, 8.8, 2.05, col3_w, 4.8, "📷 QR Code Scanner", C_NAVY)
tb = s7.shapes.add_textbox(Inches(9.0), Inches(2.75), Inches(col3_w - 0.4), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

p_acc3 = tf.paragraphs[0]
p_acc3.text = "87.40%"
p_acc3.font.bold = True
p_acc3.font.size = Pt(36)
p_acc3.font.color.rgb = C_NAVY
p_lbl3 = tf.add_paragraph()
p_lbl3.text = "Real-World Optical Decoding Rate"
p_lbl3.font.size = Pt(13)
p_lbl3.font.color.rgb = C_TEXT_MUTED
p_lbl3.space_after = Pt(12)

qr_stats = [
    ("OpenCV", "Adaptive Gaussian Binarization"),
    ("pyzbar", "Optical QR Matrix Decoding"),
    ("86.80%", "End-to-End Threat Detection Accuracy"),
    ("Auto-Route", "Dynamic URL & Text Engine Dispatch")
]
for val, lbl in qr_stats:
    p = tf.add_paragraph()
    p.text = f"✔ {val} — {lbl}"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)


# =============================================================================
# SLIDE 8: APPLICATION PROTOTYPE — DASHBOARD & SMS SCANNER SCREENSHOTS
# =============================================================================
s8 = create_slide(
    "07 / Application Prototype",
    "Application Interface: Dashboard & SMS Scanner",
    "Actual live captures of the running ScamShield Streamlit application."
)

# Left: Dashboard Screenshot
add_card(s8, 0.9, 2.05, 5.6, 4.8, "📊 Live Analytics Dashboard", C_BLUE)
dash_img = ASSETS_DIR / "app_dashboard_live.png"
if dash_img.exists():
    s8.shapes.add_picture(str(dash_img), Inches(1.1), Inches(2.65), width=Inches(5.2), height=Inches(3.4))
tb = s8.shapes.add_textbox(Inches(1.1), Inches(6.15), Inches(5.2), Inches(0.6))
p = tb.text_frame.paragraphs[0]
p.text = "• Real-time threat counters, risk tier distribution, and global KPI statistics."
p.font.size = Pt(12)
p.font.color.rgb = C_TEXT_MUTED

# Right: SMS Scanner Screenshot
add_card(s8, 6.85, 2.05, 5.6, 4.8, "💬 SMS Smishing Detection Page", C_GREEN)
sms_img = ASSETS_DIR / "app_sms_live.png"
if sms_img.exists():
    s8.shapes.add_picture(str(sms_img), Inches(7.05), Inches(2.65), width=Inches(5.2), height=Inches(3.4))
tb2 = s8.shapes.add_textbox(Inches(7.05), Inches(6.15), Inches(5.2), Inches(0.6))
p2 = tb2.text_frame.paragraphs[0]
p2.text = "• Interactive text area, sample attack library, matched keyword tags & radar chart."
p2.font.size = Pt(12)
p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 9: APPLICATION PROTOTYPE — URL INSPECTOR & QR SCANNER SCREENSHOTS
# =============================================================================
s9 = create_slide(
    "08 / Application Prototype",
    "Application Interface: URL Inspector & QR Scanner",
    "Actual live captures showing link decomposition and optical QR code inspection."
)

# Left: URL Inspector Screenshot
add_card(s9, 0.9, 2.05, 5.6, 4.8, "🌐 URL Phishing Inspector Page", C_BLUE)
url_img = ASSETS_DIR / "app_url_live.png"
if url_img.exists():
    s9.shapes.add_picture(str(url_img), Inches(1.1), Inches(2.65), width=Inches(5.2), height=Inches(3.4))
tb = s9.shapes.add_textbox(Inches(1.1), Inches(6.15), Inches(5.2), Inches(0.6))
p = tb.text_frame.paragraphs[0]
p.text = "• Decomposes scheme, host, and TLD. Surfaces 14 structural risk flags instantly."
p.font.size = Pt(12)
p.font.color.rgb = C_TEXT_MUTED

# Right: QR Code Scanner Screenshot
add_card(s9, 6.85, 2.05, 5.6, 4.8, "📷 Optical QR Code Scanner Page", C_NAVY)
qr_img = ASSETS_DIR / "app_qr_live.png"
if qr_img.exists():
    s9.shapes.add_picture(str(qr_img), Inches(7.05), Inches(2.65), width=Inches(5.2), height=Inches(3.4))
tb2 = s9.shapes.add_textbox(Inches(7.05), Inches(6.15), Inches(5.2), Inches(0.6))
p2 = tb2.text_frame.paragraphs[0]
p2.text = "• Drag-and-drop QR image upload, optical decoding, and downstream threat evaluation."
p2.font.size = Pt(12)
p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 10: LIMITATIONS AND FUTURE WORK
# =============================================================================
s10 = create_slide(
    "09 / Limitations & Roadmap",
    "System Boundaries & Future Enhancements",
    "Current operational scope and strategic roadmap for enterprise scalability."
)

# Left: Limitations
add_card(s10, 0.9, 2.05, 5.6, 4.8, "⚠️ Current Boundaries", C_NAVY)
tb = s10.shapes.add_textbox(Inches(1.2), Inches(2.75), Inches(5.0), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

limits = [
    ("User-Initiated Submission", "Currently operates on user-submitted text, links, or images rather than running as a background network packet interceptor."),
    ("Static Lexical Analysis", "Evaluates structural URL string properties without executing remote JavaScript or active DOM web scraping."),
    ("Language Domain", "Optimized primarily for English smishing texts and global domain URL standards.")
]
for title, desc in limits:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "• " + title
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED

# Right: Future Work
add_card(s10, 6.85, 2.05, 5.6, 4.8, "🚀 Future Roadmap", C_BLUE)
tb = s10.shapes.add_textbox(Inches(7.15), Inches(2.75), Inches(5.0), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

future = [
    ("Browser Extension Integration", "Package the structural URL engine into a Chrome/Firefox extension for automatic link hovering protection."),
    ("Multilingual NLP Expansion", "Incorporate regional languages and localized threat patterns using multilingual transformer embeddings."),
    ("Automated Threat Feeds", "Connect directly to live threat-intelligence feeds (PhishTank, OpenPhish) for continuous pipeline retraining.")
]
for title, desc in future:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "✔ " + title
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_BLUE
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 11: CONCLUSION AND REFERENCES
# =============================================================================
s11 = create_slide(
    "10 / Conclusion & References",
    "Summary of Contributions & Scholarly Citations",
    "Delivering an effective, multi-channel cyber-defense prototype."
)

# Left: Summary
add_card(s11, 0.9, 2.05, 6.2, 4.8, "📌 Main Project Takeaways", C_NAVY)
tb = s11.shapes.add_textbox(Inches(1.2), Inches(2.75), Inches(5.6), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

conclusions = [
    ("Unified Multi-Channel Protection", "Comprehensive cyber-defense across SMS Smishing, Phishing URLs, and Quishing QR Codes."),
    ("Trained on Over 1.35 Million Data Points", "Demonstrated solid generalization and reproducible performance across 7 benchmark corpora."),
    ("Zero-Latency & Zero-Fetch Safety", "Structural URL evaluation operates in <15ms without connecting to dangerous attacker servers."),
    ("Fully Deployed Interactive Web Prototype", "Working Streamlit dashboard with real-time analytics, risk badges, and CSV audit export.")
]
for title, desc in conclusions:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "✔ " + title
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = C_GREEN
    p.space_before = Pt(6)
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_TEXT_MUTED

# Right: References & Questions
add_card(s11, 7.45, 2.05, 5.0, 4.8, "📚 Selected References", C_BLUE)
tb = s11.shapes.add_textbox(Inches(7.75), Inches(2.75), Inches(4.4), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

refs = [
    ("Mendeley Data Benchmark (2020-2024)", "Multi-dataset phishing and malicious URL corpus (over 1.35M records)."),
    ("PhiUSIIL Phishing Benchmark", "Prasad, A. & Chandra, S., Benchmark URL feature analysis dataset."),
    ("UCI SMS Spam Collection", "Almeida, T. A., et al., Mobile text messaging smishing benchmark."),
    ("OpenCV & ISO/IEC 18004", "Computer vision standard for QR code matrix detection and decoding.")
]
for title, desc in refs:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "• " + title
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(6)
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_MUTED

p_qa = tf.add_paragraph()
p_qa.text = "\nThank You!  Questions & Discussion"
p_qa.font.bold = True
p_qa.font.size = Pt(16)
p_qa.font.color.rgb = C_BLUE
p_qa.space_before = Pt(14)


# ── Save Presentation ────────────────────────────────────────────────────────
prs.save(OUTPUT_FILE)
print(f"Presentation saved successfully to: {OUTPUT_FILE.name}")

for alt_file in [ACADEMIC_FILE, FINAL_FILE]:
    try:
        prs.save(alt_file)
        print(f"Also updated: {alt_file.name}")
    except Exception as e:
        print(f"Note: Could not update {alt_file.name} (currently open in PowerPoint): {e}")
