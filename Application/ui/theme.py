"""
ScamShield — Theme & CSS Injection
Injects dark navy cybersecurity design system into Streamlit.
"""
import streamlit as st
from config import COLORS


def inject_css():
    st.markdown(f"""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Root & Background ── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS['bg_primary']} !important;
        color: {COLORS['text_primary']} !important;
        font-family: 'Inter', sans-serif !important;
    }}
    [data-testid="stHeader"] {{
        background-color: {COLORS['bg_primary']} !important;
        border-bottom: 1px solid {COLORS['border']} !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['bg_tertiary']} 0%, {COLORS['bg_secondary']} 100%) !important;
        border-right: 1px solid {COLORS['border']} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {COLORS['text_primary']} !important;
    }}
    [data-testid="stSidebarNav"] a {{
        border-radius: 8px !important;
        transition: background 0.2s !important;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background: {COLORS['bg_card']} !important;
    }}

    /* ── Main content area ── */
    .main .block-container {{
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 1400px !important;
    }}

    /* ── Metric widgets ── */
    [data-testid="stMetric"] {{
        background: {COLORS['bg_card']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {COLORS['accent_cyan']} !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {COLORS['text_muted']} !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}

    /* ── Text inputs ── */
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stTextArea"] textarea {{
        background: {COLORS['bg_tertiary']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px !important;
        color: {COLORS['text_primary']} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
    }}
    [data-testid="stTextInput"] > div > div > input:focus,
    [data-testid="stTextArea"] textarea:focus {{
        border-color: {COLORS['accent_blue']} !important;
        box-shadow: 0 0 0 2px {COLORS['border_glow']} !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['accent_blue']}, {COLORS['accent_purple']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: opacity 0.2s, transform 0.1s !important;
    }}
    .stButton > button:hover {{
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['bg_secondary']} !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: 8px !important;
        color: {COLORS['text_muted']} !important;
        font-weight: 500 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {COLORS['bg_card']} !important;
        color: {COLORS['accent_cyan']} !important;
    }}

    /* ── Dataframe / Table ── */
    [data-testid="stDataFrame"] {{
        border: 1px solid {COLORS['border']} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}

    /* ── Progress bar ── */
    [data-testid="stProgress"] > div > div {{
        background: {COLORS['bg_tertiary']} !important;
        border-radius: 99px !important;
    }}
    [data-testid="stProgress"] > div > div > div {{
        background: linear-gradient(90deg, {COLORS['accent_blue']}, {COLORS['accent_cyan']}) !important;
        border-radius: 99px !important;
    }}

    /* ── Alerts / Info boxes ── */
    [data-testid="stAlert"] {{
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }}

    /* ── Divider ── */
    hr {{
        border-color: {COLORS['border']} !important;
        margin: 1.25rem 0 !important;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS['bg_primary']}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS['border']}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {COLORS['accent_blue']}; }}

    /* ── Custom card class ── */
    .ss-card {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }}
    .ss-card:hover {{
        border-color: {COLORS['accent_blue']}66;
    }}
    .ss-card-title {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {COLORS['text_muted']};
        margin-bottom: 0.4rem;
    }}
    .ss-risk-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 14px;
        border-radius: 99px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
    }}
    .ss-model-notice {{
        background: {COLORS['bg_tertiary']};
        border: 1px dashed {COLORS['border']};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: {COLORS['text_muted']};
        font-size: 0.85rem;
        text-align: center;
    }}
    .ss-feature-table {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }}
    .ss-page-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
    }}
    .ss-page-icon {{
        font-size: 2rem;
    }}
    .ss-page-title {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin: 0;
    }}
    .ss-page-subtitle {{
        font-size: 0.85rem;
        color: {COLORS['text_muted']};
        margin: 0;
    }}
    </style>
    """, unsafe_allow_html=True)
