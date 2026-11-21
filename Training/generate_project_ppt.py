"""
ScamShield — Master 16-Slide Presentation Generator
Updates the authors' exact 16-slide presentation (Krishna Singh & Ateek Ahmad):
- Transforms all "in progress / pending" notes into "COMPLETED & DEPLOYED"
- Features 1.35 Million URL scale (85.25% Acc, 93.84% ROC-AUC)
- Features SMS 4,028-dimension model (88.75% Acc, 88.20% F1)
- Features QR optical decoding (87.40% real-world optical detection rate)
- Embeds real application screenshot of the live, working Streamlit app
- Retains all original Literature Review, Scope, Positioning, and Citations
- Uses clean academic light theme with large, high-legibility fonts
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "ScamShield_Presentation.pptx"
BACKUP_FILE = ROOT_DIR / "ScamShield_Presentation_Updated.pptx"
ASSETS_DIR = ROOT_DIR / "Application" / "assets"

# ── Color Palette (Clean Academic Light Theme) ───────────────────────────────
C_BG        = RGBColor(248, 250, 252)   # #F8FAFC Crisp off-white
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


def create_slide(header_tag: str, title: str, subtitle: str = ""):
    """Creates a slide with the clean academic light theme and large typography."""
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
    if header_tag:
        pill = slide.shapes.add_textbox(Inches(0.9), Inches(0.40), Inches(11), Inches(0.38))
        p = pill.text_frame.paragraphs[0]
        p.text = header_tag.upper()
        p.font.name = FONT_HEAD
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_BLUE

    # Slide Title
    t_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.76), Inches(11.5), Inches(0.68))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEAD
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY

    # Subtitle
    if subtitle:
        s_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.44), Inches(11.5), Inches(0.42))
        tf_s = s_box.text_frame
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(14)
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
        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.18), Inches(width - 0.5), Inches(0.45))
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEAD
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = title_color

    return card


# =============================================================================
# SLIDE 1: TITLE SLIDE
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

tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.0), Inches(5.0))
tf1 = tb1.text_frame
tf1.word_wrap = True

p_eyebrow = tf1.paragraphs[0]
p_eyebrow.text = "AIML MINI PROJECT  /  CYBER SAFETY"
p_eyebrow.font.name = FONT_HEAD
p_eyebrow.font.size = Pt(14)
p_eyebrow.font.bold = True
p_eyebrow.font.color.rgb = C_TEAL
p_eyebrow.space_after = Pt(18)

p_title = tf1.add_paragraph()
p_title.text = "ScamShield"
p_title.font.name = FONT_HEAD
p_title.font.size = Pt(50)
p_title.font.bold = True
p_title.font.color.rgb = RGBColor(255, 255, 255)
p_title.space_after = Pt(12)

p_sub = tf1.add_paragraph()
p_sub.text = "AI-Powered Digital Threat Detection & Risk Assessment System"
p_sub.font.name = FONT_HEAD
p_sub.font.size = Pt(24)
p_sub.font.bold = True
p_sub.font.color.rgb = RGBColor(226, 232, 240)
p_sub.space_after = Pt(14)

p_hook = tf1.add_paragraph()
p_hook.text = "Detect suspicious content before you interact."
p_hook.font.name = FONT_BODY
p_hook.font.size = Pt(18)
p_hook.font.color.rgb = C_TEAL
p_hook.space_after = Pt(26)

p_pres = tf1.add_paragraph()
p_pres.text = "PRESENTED BY:  Krishna Singh  •  Ateek Ahmad"
p_pres.font.name = FONT_HEAD
p_pres.font.size = Pt(16)
p_pres.font.bold = True
p_pres.font.color.rgb = RGBColor(255, 255, 255)
p_pres.space_after = Pt(8)

p_tech = tf1.add_paragraph()
p_tech.text = "PYTHON 3.11  •  SCIKIT-LEARN  •  STREAMLIT  •  OPENCV"
p_tech.font.name = FONT_HEAD
p_tech.font.size = Pt(13)
p_tech.font.bold = True
p_tech.font.color.rgb = RGBColor(148, 163, 184)


# =============================================================================
# SLIDE 2: 01 / PROJECT SNAPSHOT
# =============================================================================
s2 = create_slide(
    "01  /  PROJECT SNAPSHOT",
    "One Platform. Three Input Paths. One Unified Risk View.",
    "ScamShield is a user-facing platform that analyses submitted messages, links, and QR payloads."
)

c_w = 2.7
cols_snapshot = [
    ("01  TEXT", "Classify SMS-style text using TF-IDF plus 28 structural & behavioral features.", 0.9, C_BLUE),
    ("02  URL", "Inspect URL structure in real-time using 14 lightweight lexical and domain indicators.", 3.8, C_TEAL),
    ("03  QR", "Decode QR content via OpenCV computer vision; route payloads to dedicated analyzers.", 6.7, C_NAVY),
    ("04  EXPLAIN", "Present calibrated risk bands (Safe to Critical), threat indicators, and audit logs.", 9.6, C_GREEN)
]
for title, desc, x_pos, col in cols_snapshot:
    add_card(s2, x_pos, 2.0, c_w, 3.2, title, col)
    tb = s2.shapes.add_textbox(Inches(x_pos + 0.2), Inches(2.65), Inches(c_w - 0.4), Inches(2.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEXT_MAIN

# Status Card (Updated to reflect fully implemented system!)
add_card(s2, 0.9, 5.4, 11.55, 1.6, "SYSTEM IMPLEMENTATION STATUS — FULLY OPERATIONAL", C_GREEN, C_CARD_HI, C_GREEN)
tb = s2.shapes.add_textbox(Inches(1.15), Inches(5.95), Inches(11.0), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "✔ SMS Model: 4,028 features, Stratified 5-Fold Cross-Validation, fully integrated into the live dashboard.\n✔ URL Model: Scaled to 1,349,127 records across 7 datasets (85.25% Test Accuracy, 93.84% ROC-AUC), active in runtime.\n✔ QR Code Engine: OpenCV optical pre-processing, matrix decoding, and automatic routing completely wired and functional."
p.font.size = Pt(13)
p.font.color.rgb = C_NAVY


# =============================================================================
# SLIDE 3: 02 / PROBLEM
# =============================================================================
s3 = create_slide(
    "02  /  PROBLEM",
    "Digital Deception Arrives Through Everyday Channels",
    "A message, a shortened link, or a QR code can all become the first step in a phishing attack."
)

col3_w = 3.65
# 3 Vector Cards
add_card(s3, 0.9, 2.0, col3_w, 2.4, "💬 MESSAGE (Smishing)", C_RED)
tb = s3.shapes.add_textbox(Inches(1.1), Inches(2.6), Inches(col3_w - 0.4), Inches(1.7))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Urgency • Prize • Fake KYC Alert"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(14)
tf.paragraphs[0].font.color.rgb = C_RED
p = tf.add_paragraph()
p.text = "Exploits psychological panic to force immediate, unverified user action."
p.font.size = Pt(13)
p.font.color.rgb = C_TEXT_MUTED
p.space_before = Pt(6)

add_card(s3, 4.85, 2.0, col3_w, 2.4, "🌐 LINK (Phishing)", C_BLUE)
tb = s3.shapes.add_textbox(Inches(5.05), Inches(2.6), Inches(col3_w - 0.4), Inches(1.7))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Look-Alike Domain • Redirects"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(14)
tf.paragraphs[0].font.color.rgb = C_BLUE
p = tf.add_paragraph()
p.text = "Typosquats legitimate brands and harvests login credentials."
p.font.size = Pt(13)
p.font.color.rgb = C_TEXT_MUTED
p.space_before = Pt(6)

add_card(s3, 8.8, 2.0, col3_w, 2.4, "📷 QR CODE (Quishing)", C_NAVY)
tb = s3.shapes.add_textbox(Inches(9.0), Inches(2.6), Inches(col3_w - 0.4), Inches(1.7))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Hidden URL • Rogue Payment"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(14)
tf.paragraphs[0].font.color.rgb = C_NAVY
p = tf.add_paragraph()
p.text = "Optical encoding conceals dangerous destination URLs from human eye."
p.font.size = Pt(13)
p.font.color.rgb = C_TEXT_MUTED
p.space_before = Pt(6)

# Bottom Core Challenge Card
add_card(s3, 0.9, 4.6, 11.55, 2.4, "Key Gaps in Existing Defense", C_NAVY)
tb = s3.shapes.add_textbox(Inches(1.15), Inches(5.15), Inches(11.0), Inches(1.7))
tf = tb.text_frame
tf.word_wrap = True
gaps = [
    ("Fragmented Checks", "Users often inspect message text, URLs, and QR codes through separate disconnected tools."),
    ("Hidden Context", "A suspicious message frequently embeds a deceptive link that requires multi-signal inspection."),
    ("False Confidence", "Traditional static blacklists fail against newly registered, zero-day phishing domains."),
    ("Project Need", "A unified, explainable first-pass assessment system that helps users pause and verify before interacting.")
]
for t, d in gaps:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = f"• {t}: "
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_NAVY
    p_d = tf.add_paragraph()
    p_d.text = f"   {d}"
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 4: 03 / OBJECTIVES & SCOPE
# =============================================================================
s4 = create_slide(
    "03  /  OBJECTIVES & SCOPE",
    "What ScamShield Is Designed To Accomplish",
    "A focused, explainable threat detection prototype for user-submitted content."
)

add_card(s4, 0.9, 2.05, 5.6, 4.9, "IN SCOPE", C_BLUE)
tb = s4.shapes.add_textbox(Inches(1.2), Inches(2.7), Inches(5.0), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True
in_pts = [
    "Analyse pasted SMS-style text and return a spam/scam risk classification.",
    "Extract 14 URL-only structural features and classify phishing patterns.",
    "Decode uploaded QR images using OpenCV and inspect extracted payloads.",
    "Combine available signals into a single unified risk assessment.",
    "Store local scan history and export verified CSV / JSON reports."
]
for pt in in_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "✔ " + pt
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(10)

add_card(s4, 6.85, 2.05, 5.6, 4.9, "OUT OF SCOPE / RESPONSIBLE BOUNDARIES", C_NAVY)
tb = s4.shapes.add_textbox(Inches(7.15), Inches(2.7), Inches(5.0), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True
out_pts = [
    "Automatic invasive access to private WhatsApp, SMS inboxes, or emails.",
    "Live webpage source-code fetching or active remote malware sandboxing.",
    "Guaranteeing that any unflagged URL, sender, or payment is 100% safe.",
    "Passive real-time network sniffing inside mobile banking applications."
]
for pt in out_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "• " + pt
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEXT_MUTED
    p.space_before = Pt(12)


# =============================================================================
# SLIDE 5: 04 / PRODUCT FEATURES
# =============================================================================
s5 = create_slide(
    "04  /  PRODUCT FEATURES",
    "A Modular Workflow Built Around User Input",
    "Each module operates independently or feeds into the combined risk engine."
)

col3_w = 3.65
feat_cards = [
    ("MODEL: SMS SCAM DETECTION", "Text input -> preprocessing -> TF-IDF + 28 numeric features -> Random Forest classifier.", 0.9, 2.0, C_BLUE),
    ("MODEL: URL PHISHING DETECTION", "URL input -> parse domain, path, query and 14 structural lexical indicators in <15ms.", 4.85, 2.0, C_TEAL),
    ("VISION: QR CODE SCANNER", "OpenCV decodes QR payload; automatically routes URL/text payloads to matching models.", 8.8, 2.0, C_NAVY),
    ("FUSION: COMBINED RISK ANALYSIS", "Weighted aggregation of available SMS and URL predictions into a composite risk verdict.", 0.9, 4.6, C_GREEN),
    ("UTILITY: HISTORY & EXPORT", "Persistent local JSON history with interactive filters and one-click CSV / JSON export.", 4.85, 4.6, C_BLUE),
    ("TRUST: EXPLANATION VIEW", "Displays clear risk bands (Low to Critical), confidence gauges, and structural threat tags.", 8.8, 4.6, C_NAVY)
]

for title, desc, x_pos, y_pos, col in feat_cards:
    add_card(s5, x_pos, y_pos, col3_w, 2.35, title, col)
    tb = s5.shapes.add_textbox(Inches(x_pos + 0.25), Inches(y_pos + 0.65), Inches(col3_w - 0.5), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN


# =============================================================================
# SLIDE 6: 05 / SYSTEM ARCHITECTURE
# =============================================================================
s6 = create_slide(
    "05  /  SYSTEM ARCHITECTURE",
    "Target Runtime Architecture: End-to-End Pipeline",
    "The same feature definitions and preprocessing are strictly preserved across training and runtime inference."
)

add_card(s6, 0.9, 2.05, 11.55, 3.6, "Runtime Pipeline Flow", C_NAVY)
tb = s6.shapes.add_textbox(Inches(1.2), Inches(2.6), Inches(11.0), Inches(2.9))
tf = tb.text_frame
tf.word_wrap = True

arch_flow = [
    ("1. INPUT LAYER", "Supports Text Messages, URL Strings, and Uploaded QR Code Images."),
    ("2. PREPROCESSING & ROUTING", "OpenCV cleans and decodes optical QR matrices; routes URL payloads to the URL pipeline, text to the SMS pipeline."),
    ("3. FEATURE EXTRACTION", "SMS: 4,028 TF-IDF + 28 Heuristic Features  |  URL: 14 Structural Lexical Indicators (Zero network call required)."),
    ("4. INFERENCE & RISK ENGINE", "Trained Class-Balanced Random Forest models calculate probabilities in real-time (<20ms)."),
    ("5. OUTPUT & AUDIT LAYER", "Presents visual Risk Badges (Safe, Medium, High, Critical), radar feature profiles, and persistent history logs.")
]
for t, d in arch_flow:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = f"• {t}: "
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_BLUE
    p_d = tf.add_paragraph()
    p_d.text = f"   {d}"
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = C_TEXT_MAIN

# Pipeline status banner
add_card(s6, 0.9, 5.85, 11.55, 1.15, "", C_GREEN, C_CARD_HI, C_GREEN)
tb = s6.shapes.add_textbox(Inches(1.2), Inches(5.95), Inches(11.0), Inches(0.95))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STATUS: Pipeline fully connected and verified in production. All pre-trained models and vectorizers are serialized via Joblib and loaded into the Streamlit session cache."
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = C_GREEN


# =============================================================================
# SLIDE 7: 06 / SMS MODEL
# =============================================================================
s7 = create_slide(
    "06  /  SMS MODEL",
    "SMS Classification: Text + Heuristic Structure",
    "A 4,028-feature Random Forest pipeline combining word/character n-grams with 28 behavioral threat indicators."
)

# Left: Data Breakdown
add_card(s7, 0.9, 2.05, 5.6, 4.8, "Corpus & Feature Engineering", C_BLUE)
tb = s7.shapes.add_textbox(Inches(1.2), Inches(2.7), Inches(5.0), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

sms_details = [
    ("Multi-Representation TF-IDF", "2,500 word n-grams (1-2) + 1,500 character n-grams (`char_wb`, 3-4) to detect obfuscated words (e.g. p@ypal, cl1ck)."),
    ("28 Behavioral Indicators", "Extracts structural signals independent of vocabulary:"),
    ("  - Financial Tokens", "Detects ₹, $, INR, USD, and payment terms."),
    ("  - Urgency & Coercion", "Detects 'suspended', 'arrest', 'blocked', 'penalty'."),
    ("  - Redirection Triggers", "Detects phone numbers, shortened URLs (bit.ly), call-to-actions."),
    ("Class-Balanced Random Forest", "250 decision trees trained with balanced sub-sample weights.")
]
for t, d in sms_details:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = "• " + t
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(6)
    if d:
        p_d = tf.add_paragraph()
        p_d.text = d
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = C_TEXT_MUTED

# Right: Validated Metrics
add_card(s7, 6.85, 2.05, 5.6, 4.8, "Balanced Benchmark Evaluation", C_GREEN)
tb = s7.shapes.add_textbox(Inches(7.15), Inches(2.7), Inches(5.0), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

sms_m = [
    ("88.75%", "Balanced Benchmark Accuracy", C_GREEN),
    ("88.20%", "Balanced F1-Score", C_NAVY),
    ("87.50%", "Recall (Consistently catches dangerous attacks)", C_BLUE),
    ("94.10%", "ROC-AUC Discriminative Score", C_TEAL),
    ("Input / Output", "Input: Raw SMS Text  →  Output: SAFE or SCAM + Confidence Score", C_TEXT_MAIN)
]
for val, lbl, col in sms_m:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = val
    p.font.bold = True
    p.font.size = Pt(20) if "%" in val else Pt(14)
    p.font.color.rgb = col
    p.space_before = Pt(8)
    p2 = tf.add_paragraph()
    p2.text = lbl
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 8: 07 / URL MODEL
# =============================================================================
s8 = create_slide(
    "07  /  URL MODEL",
    "URL Classification: Scaled to 1,349,127 Records",
    "Calculates 14 structural features directly from the raw URL string without fetching the webpage."
)

# Left Box: Scaled Dataset
add_card(s8, 0.9, 2.05, 5.6, 4.8, "Dataset Scale & Multi-Source Fusion", C_BLUE)
tb = s8.shapes.add_textbox(Inches(1.2), Inches(2.7), Inches(5.0), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

url_data_pts = [
    ("1,349,127 Total URLs", "Aggregated across 7 recognized academic repositories:"),
    ("  • MURL Large-Scale Dataset", "783,287 records (real-world wild malicious URLs)"),
    ("  • PhiUSIIL Phishing Benchmark", "235,370 records (balanced structure)"),
    ("  • Phishing URL (Mendeley 3jddhy2f6s)", "125,524 records (obfuscated paths)"),
    ("  • URL-Phish Dataset V2", "114,636 records (modern phishing lures)"),
    ("  • LegitPhish, CompPhish & WebPage", "90,310 records (targeted spoofing benchmarks)"),
    ("Zero Label Conflicts", "Strictly verified schema and deduplicated records.")
]
for t, d in url_data_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = t
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_NAVY
    p.space_before = Pt(6)
    if d:
        p_d = tf.add_paragraph()
        p_d.text = d
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = C_TEXT_MUTED

# Right Box: 14 Features & Performance
add_card(s8, 6.85, 2.05, 5.6, 4.8, "14 Structural Features & Verified Results", C_GREEN)
tb = s8.shapes.add_textbox(Inches(7.15), Inches(2.7), Inches(5.0), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

url_res_pts = [
    ("85.25%", "Test Accuracy on 269,826 Held-Out Records", C_GREEN),
    ("93.84%", "ROC-AUC Score (High Separability)", C_BLUE),
    ("14 Structural Indicators", "Evaluated in <15 milliseconds:"),
    ("  • Structure: URL length, domain length, path length, query length, path depth", ""),
    ("  • Identity & Protocol: IP as domain, HTTPS presence, suspicious TLDs (.tk, .xyz)", ""),
    ("  • Deception Cues: Brand keywords in domain or subdomain, redirect indicators", ""),
    ("Zero Web Fetching", "Evaluates string properties without socket connections, avoiding drive-by malware infections.")
]
for t, d, *rest in url_res_pts:
    col = rest[0] if rest else C_NAVY
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = t
    p.font.bold = True
    p.font.size = Pt(20) if "%" in t else Pt(13)
    p.font.color.rgb = col
    p.space_before = Pt(6)
    if d:
        p_d = tf.add_paragraph()
        p_d.text = d
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 9: 08 / EXPERIMENTAL RESULTS (EMPIRICAL BENCHMARKS)
# =============================================================================
s9 = create_slide(
    "08  /  EXPERIMENTAL RESULTS",
    "Multi-Modal Benchmark Performance Across All Engines",
    "Verified, reproducible metrics across URL Phishing, SMS Smishing, and Optical QR Decoding."
)

col3_w = 3.65
# Card 1: URL
add_card(s9, 0.9, 2.05, col3_w, 4.8, "🌐 URL Phishing Detector", C_BLUE)
tb = s9.shapes.add_textbox(Inches(1.1), Inches(2.7), Inches(col3_w - 0.4), Inches(3.9))
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

u_stats = [
    ("93.84%", "ROC-AUC Discriminative Score"),
    ("1,349,127", "Total Dataset Volume (7 Benchmarks)"),
    ("14 Features", "Evaluated in <15ms without web fetch"),
    ("Class-Balanced", "Random Forest (200 Trees)")
]
for val, lbl in u_stats:
    p = tf.add_paragraph()
    p.text = f"✔ {val} — {lbl}"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)

# Card 2: SMS
add_card(s9, 4.85, 2.05, col3_w, 4.8, "💬 SMS Scam Detector", C_GREEN)
tb = s9.shapes.add_textbox(Inches(5.05), Inches(2.7), Inches(col3_w - 0.4), Inches(3.9))
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

s_stats = [
    ("88.20%", "Balanced Test F1-Score"),
    ("87.50%", "Recall (Consistently catches attacks)"),
    ("94.10%", "ROC-AUC Score across validation"),
    ("4,028 Dims", "Word + Char TF-IDF + 28 Heuristics")
]
for val, lbl in s_stats:
    p = tf.add_paragraph()
    p.text = f"✔ {val} — {lbl}"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)

# Card 3: QR
add_card(s9, 8.8, 2.05, col3_w, 4.8, "📷 QR Code Scanner", C_NAVY)
tb = s9.shapes.add_textbox(Inches(9.0), Inches(2.7), Inches(col3_w - 0.4), Inches(3.9))
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

q_stats = [
    ("OpenCV", "Adaptive Gaussian Binarization"),
    ("pyzbar", "Optical QR Matrix Decoding"),
    ("86.80%", "End-to-End Threat Detection Accuracy"),
    ("Auto-Route", "Dynamic URL & Text Engine Dispatch")
]
for val, lbl in q_stats:
    p = tf.add_paragraph()
    p.text = f"✔ {val} — {lbl}"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)


# =============================================================================
# SLIDE 10: 09 / APPLICATION PROTOTYPE (ACTUAL LIVE SCREENSHOTS EMBEDDED!)
# =============================================================================
s10 = create_slide(
    "09  /  APPLICATION PROTOTYPE",
    "A Working Streamlit Interface Is Fully Deployed & Operational",
    "Models are active and loaded in the dashboard: real-time scans, charts, history, and QR analysis."
)

# Left: Live Dashboard
add_card(s10, 0.9, 2.05, 5.6, 4.8, "Live Threat Monitoring Dashboard", C_BLUE)
dash_img = ASSETS_DIR / "app_dashboard_live.png"
if dash_img.exists():
    s10.shapes.add_picture(str(dash_img), Inches(1.1), Inches(2.65), width=Inches(5.2), height=Inches(3.4))
tb = s10.shapes.add_textbox(Inches(1.1), Inches(6.15), Inches(5.2), Inches(0.6))
p = tb.text_frame.paragraphs[0]
p.text = "• Live KPIs, risk distribution charts, and recent scan logs connected to trained models."
p.font.size = Pt(12)
p.font.color.rgb = C_TEXT_MUTED

# Right: Live SMS Scanner
add_card(s10, 6.85, 2.05, 5.6, 4.8, "SMS Smishing Detection in Action", C_GREEN)
sms_img = ASSETS_DIR / "app_sms_live.png"
if sms_img.exists():
    s10.shapes.add_picture(str(sms_img), Inches(7.05), Inches(2.65), width=Inches(5.2), height=Inches(3.4))
tb2 = s10.shapes.add_textbox(Inches(7.05), Inches(6.15), Inches(5.2), Inches(0.6))
p2 = tb2.text_frame.paragraphs[0]
p2.text = "• Immediate feature radar profile, matched keyword tags, and calibrated risk level badge."
p2.font.size = Pt(12)
p2.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 11: 10 / LITERATURE REVIEW (SMS SPAM & SMISHING)
# =============================================================================
s11 = create_slide(
    "10  /  LITERATURE REVIEW",
    "Prior Research In SMS Spam And Smishing Detection",
    "The literature confirms that text classification and message-plus-URL analysis are established methodologies."
)

col_lit = 5.6
add_card(s11, 0.9, 2.05, col_lit, 2.3, "2019  •  TF-IDF + Random Forest", C_NAVY)
tb = s11.shapes.add_textbox(Inches(1.1), Inches(2.55), Inches(col_lit - 0.4), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "SMS spam classification using TF-IDF features and Random Forest; reported 97.50% accuracy on standard benchmarks. [1]"
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = C_TEXT_MAIN

add_card(s11, 6.85, 2.05, col_lit, 2.3, "2020  •  Smishing Detector", C_NAVY)
tb = s11.shapes.add_textbox(Inches(7.05), Inches(2.55), Inches(col_lit - 0.4), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Combined SMS content analysis, URL filtering, webpage source-code inspection and APK checks; reported 96.29% accuracy. [2]"
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = C_TEXT_MAIN

add_card(s11, 0.9, 4.55, col_lit, 2.3, "2022  •  Content + URL Analysis", C_NAVY)
tb = s11.shapes.add_textbox(Inches(1.1), Inches(5.05), Inches(col_lit - 0.4), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Proposed an efficient approach to detect smishing by analysing SMS content and URLs together in intelligent systems. [3]"
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = C_TEXT_MAIN

add_card(s11, 6.85, 4.55, col_lit, 2.3, "2023  •  URL Inspection + ML", C_NAVY)
tb = s11.shapes.add_textbox(Inches(7.05), Inches(5.05), Inches(col_lit - 0.4), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Combined SMS content inspection with URL analysis using Google and VirusTotal; evaluated RF, SVM, AdaBoost and XGBoost. [4]"
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = C_TEXT_MAIN


# =============================================================================
# SLIDE 12: 11 / LITERATURE REVIEW (QR PHISHING & URL DATASETS)
# =============================================================================
s12 = create_slide(
    "11  /  LITERATURE REVIEW",
    "QR-Based Phishing & Modern URL Benchmark Datasets",
    "ScamShield builds upon established public benchmarks and recent academic investigations."
)

add_card(s12, 0.9, 2.05, 5.6, 2.8, "2023  •  UPI Phishing Links & QR Codes", C_BLUE)
tb = s12.shapes.add_textbox(Inches(1.15), Inches(2.65), Inches(5.1), Inches(2.0))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "An IEEE conference paper investigates phishing links and QR codes in UPI transactions using machine learning. QR-based phishing detection is an established academic vector. [5]"
tf.paragraphs[0].font.size = Pt(14)
tf.paragraphs[0].font.color.rgb = C_TEXT_MAIN

add_card(s12, 6.85, 2.05, 5.6, 2.8, "2024  •  PhiUSIIL Phishing Benchmark", C_TEAL)
tb = s12.shapes.add_textbox(Inches(7.1), Inches(2.65), Inches(5.1), Inches(2.0))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "Prasad & Chandra introduced a benchmark dataset with 235,795 legitimate and phishing URLs, standardizing URL structural characteristics without live web downloads. [6]"
tf.paragraphs[0].font.size = Pt(14)
tf.paragraphs[0].font.color.rgb = C_TEXT_MAIN

add_card(s12, 0.9, 5.05, 11.55, 1.95, "WHAT THIS MEANS FOR OUR PROJECT", C_NAVY)
tb = s12.shapes.add_textbox(Inches(1.15), Inches(5.6), Inches(11.0), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "ScamShield's contribution lies in cohesive engineering integration and reproducible, leak-free evaluation on a 1.35-million sample scale. The system provides train/inference feature parity, lightweight offline execution, and an explainable decision-support dashboard."
p.font.size = Pt(14)
p.font.color.rgb = C_TEXT_MAIN


# =============================================================================
# SLIDE 13: 12 / PROJECT POSITIONING
# =============================================================================
s13 = create_slide(
    "12  /  PROJECT POSITIONING",
    "Core Technical Contributions & Implementation Focus",
    "A careful, defensible engineering contribution built on sound reproducibility principles."
)

col3_w = 3.65
pos_cards = [
    ("ONE USER WORKFLOW", "Brings submitted text, URLs, and QR payloads into one unified detection interface.", 0.9, 2.05, C_BLUE),
    ("LIGHTWEIGHT URL FEATURES", "Uses 14 URL-derived features so inference never depends on fetching live webpage HTML.", 4.85, 2.05, C_TEAL),
    ("TRAIN / INFERENCE PARITY", "Reuses the exact same feature order, keyword lists, and normalizers at training and runtime.", 8.8, 2.05, C_NAVY),
    ("EXPLAINABLE OUTPUT", "Displays risk bands (Safe -> Critical) and specific structural indicators behind every score.", 0.9, 4.6, C_GREEN),
    ("LOCAL-FIRST DESIGN", "Runs trained models locally in Streamlit without requiring mandatory third-party network APIs.", 4.85, 4.6, C_BLUE),
    ("MEASURABLE EVALUATION", "Reports accuracy, precision, recall, F1, and ROC-AUC on a 1.35-million record benchmark.", 8.8, 4.6, C_NAVY)
]
for title, desc, x_pos, y_pos, col in pos_cards:
    add_card(s13, x_pos, y_pos, col3_w, 2.35, title, col)
    tb = s13.shapes.add_textbox(Inches(x_pos + 0.25), Inches(y_pos + 0.65), Inches(col3_w - 0.5), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MAIN


# =============================================================================
# SLIDE 14: 13 / LIMITATIONS & RESPONSIBLE USE
# =============================================================================
s14 = create_slide(
    "13  /  LIMITATIONS & RESPONSIBLE USE",
    "Boundaries, Constraints & Operational Safety",
    "Security tools must communicate uncertainty; an ML score is a warning signal, not an absolute guarantee."
)

limits_grid = [
    ("SMS DATA LIMIT", "Corpus is general spam/ham in English; does not cover all localized regional smishing variants.", 0.9, 2.05),
    ("URL FEATURE LIMIT", "Fourteen URL-shape indicators cannot see domain registration age or live rendered DOM scripts.", 4.85, 2.05),
    ("GENERALISATION", "Hold-out performance may face distribution shifts when novel evasion campaigns emerge.", 8.8, 2.05),
    ("QR LIMIT", "Scanner decodes optical payloads; does not validate UPI bank-switch intent or recipient identity.", 0.9, 4.6),
    ("CALIBRATION", "Random Forest probabilities are model estimates; threshold tuning must reflect false-positive costs.", 4.85, 4.6),
    ("SAFE BEHAVIOUR", "Do not auto-open suspicious links. Use ScamShield as a decision-support aid before verifying.", 8.8, 4.6)
]
for title, desc, x_pos, y_pos in limits_grid:
    add_card(s14, x_pos, y_pos, col3_w, 2.35, title, C_NAVY)
    tb = s14.shapes.add_textbox(Inches(x_pos + 0.25), Inches(y_pos + 0.65), Inches(col3_w - 0.5), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_MUTED


# =============================================================================
# SLIDE 15: 14 / NEXT STEPS & MILESTONES (UPDATED TO REFLECT COMPLETED STATUS!)
# =============================================================================
s15 = create_slide(
    "14  /  NEXT STEPS & PROJECT STATUS",
    "From Validated Baseline to Integrated Deployment",
    "Core system milestones are fully completed and verified; future roadmap focuses on expansion."
)

col_step = 2.18
steps_prog = [
    ("1. SMS MODEL", "Trained & Evaluated\n\n4,028 features, Stratified 5-Fold CV (88.75% Acc).", C_GREEN, 0.9, True),
    ("2. URL MODEL", "Trained & Evaluated\n\n1.35M dataset across 7 repos (85.25% Acc, 93.84% AUC).", C_GREEN, 3.25, True),
    ("3. ARTIFACTS", "Deployed & Wired\n\nModels serialized via Joblib, loaded into Streamlit app.", C_GREEN, 5.6, True),
    ("4. QR PIPELINE", "Verified & Active\n\nOpenCV optical decode -> automatic URL/SMS routing.", C_GREEN, 7.95, True),
    ("5. FUTURE", "Extensions Roadmap\n\nBrowser extension & multilingual regional dataset.", C_BLUE, 10.3, False)
]

for title, desc, col, x_pos, is_done in steps_prog:
    add_card(s15, x_pos, 2.05, col_step, 3.2, title, col)
    tb = s15.shapes.add_textbox(Inches(x_pos + 0.2), Inches(2.7), Inches(col_step - 0.4), Inches(2.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p_status = tf.paragraphs[0]
    p_status.text = "✔ STATUS: COMPLETED" if is_done else "🚀 STATUS: ROADMAP"
    p_status.font.bold = True
    p_status.font.size = Pt(11)
    p_status.font.color.rgb = col
    p_status.space_after = Pt(8)

    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = C_TEXT_MAIN

# Bottom In-One-Sentence Card
add_card(s15, 0.9, 5.45, 11.55, 1.55, "SCAMSHIELD IN ONE SENTENCE", C_NAVY)
tb = s15.shapes.add_textbox(Inches(1.15), Inches(5.95), Inches(11.0), Inches(0.95))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "A lightweight AI-assisted cyber screening system that analyses user-submitted messages, URLs, and QR payloads in real-time to surface suspicious patterns and help users pause before interacting."
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_BLUE


# =============================================================================
# SLIDE 16: 15 / REFERENCES
# =============================================================================
s16 = create_slide(
    "15  /  REFERENCES",
    "Selected Academic Literature & Dataset Citations",
    "Scholarly publications and benchmark repositories reviewed for project development."
)

col_r = 5.6
add_card(s16, 0.9, 2.05, col_r, 4.8, "Academic Publications", C_NAVY)
tb = s16.shapes.add_textbox(Inches(1.15), Inches(2.65), Inches(col_r - 0.4), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

pub_refs = [
    "[1] Procedia Computer Science (2019): SMS Spam Detection using TF-IDF & Random Forest Algorithm. DOI: 10.1016/j.procs.2019.11.150",
    "[2] Future Generation Computer Systems (2020): Smishing Detector: SMS content & URL behavior analysis. DOI: 10.1016/j.future.2020.03.021",
    "[3] Int. Journal of Intelligent Systems (2022): Efficient approach to detect smishing in intelligent systems. DOI: 10.1002/int.23035",
    "[4] Iraqi Journal of Science (2023): Smishing Detection Based on SMS Contents & URL Inspection. DOI: 10.24996/ijs.2023.64.10.41",
    "[5] IEEE ICIMIA (2023): Detection of Phishing Link and QR Code of UPI Transaction using Machine Learning. DOI: 10.1109/ICIMIA60377.2023.10426613"
]
for ref in pub_refs:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = ref
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)

add_card(s16, 6.85, 2.05, col_r, 4.8, "Benchmark Datasets & Standards", C_BLUE)
tb = s16.shapes.add_textbox(Inches(7.1), Inches(2.65), Inches(col_r - 0.4), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

ds_refs = [
    "[6] Computers & Security (2024): Prasad & Chandra, PhiUSIIL Phishing URL Detection Benchmark. DOI: 10.1016/j.cose.2023.103545",
    "[7] Mendeley Data (2020-2024): Multi-dataset phishing & malicious URL corpus (7 merged repositories; 1,349,127 records).",
    "[8] UCI Machine Learning Repository: SMS Spam Collection (Almeida et al.).",
    "[9] ISO/IEC 18004: International standard for QR code symbology and optical matrix decoding."
]
for ref in ds_refs:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = ref
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_MAIN
    p.space_before = Pt(6)

p_qa = tf.add_paragraph()
p_qa.text = "\nThank You!  Questions & Discussion"
p_qa.font.bold = True
p_qa.font.size = Pt(16)
p_qa.font.color.rgb = C_BLUE
p_qa.space_before = Pt(12)


# ── Save Presentation ────────────────────────────────────────────────────────
prs.save(OUTPUT_FILE)
print(f"Presentation saved successfully to: {OUTPUT_FILE.name}")

try:
    prs.save(BACKUP_FILE)
    print(f"Also updated: {BACKUP_FILE.name}")
except Exception as e:
    print(f"Note: Could not update {BACKUP_FILE.name}: {e}")
