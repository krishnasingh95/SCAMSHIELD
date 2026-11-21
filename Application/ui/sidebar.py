"""
ScamShield — Sidebar renderer
"""
import os
import streamlit as st
from config import APP_NAME, APP_VERSION, APP_ICON, COLORS, MODEL_PATHS


def render_sidebar():
    with st.sidebar:
        # ── Logo / Brand ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:1rem 0 0.5rem;">
            <div style="font-size:2.8rem;margin-bottom:4px;">{APP_ICON}</div>
            <h2 style="color:{COLORS['accent_cyan']};margin:0;font-size:1.4rem;
                       font-weight:800;letter-spacing:0.05em;">{APP_NAME}</h2>
            <p style="color:{COLORS['text_muted']};font-size:0.72rem;margin:2px 0 0;">
                Digital Threat Detection
            </p>
        </div>
        <hr style="border-color:{COLORS['border']};margin:0.75rem 0;">
        """, unsafe_allow_html=True)

        # ── Navigation label ──────────────────────────────────────────────────
        st.markdown(f"""
        <p style="color:{COLORS['text_muted']};font-size:0.7rem;font-weight:600;
                  letter-spacing:0.1em;text-transform:uppercase;margin:0.25rem 0 0.5rem 0.5rem;">
            Navigation
        </p>
        """, unsafe_allow_html=True)

        # Streamlit handles page links automatically via pages/ folder.
        # We add extra status info below.

        st.markdown(f"<hr style='border-color:{COLORS['border']};margin:0.75rem 0;'>",
                    unsafe_allow_html=True)

        # ── Model Status ──────────────────────────────────────────────────────
        st.markdown(f"""
        <p style="color:{COLORS['text_muted']};font-size:0.7rem;font-weight:600;
                  letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.5rem 0.5rem;">
            Model Status
        </p>
        """, unsafe_allow_html=True)

        _model_status_indicator("SMS Scam RF",    MODEL_PATHS["sms"])
        _model_status_indicator("URL Phishing RF", MODEL_PATHS["url"])

        st.markdown(f"<hr style='border-color:{COLORS['border']};margin:0.75rem 0;'>",
                    unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:0.5rem 0;">
            <p style="color:{COLORS['text_muted']};font-size:0.7rem;margin:0;">
                v{APP_VERSION} &nbsp;·&nbsp; AIML College Project
            </p>
        </div>
        """, unsafe_allow_html=True)


def _model_status_indicator(name: str, path: str):
    exists  = os.path.exists(path)
    dot_col = COLORS["risk_safe"] if exists else COLORS["text_muted"]
    status  = "Loaded" if exists else "Not loaded"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;padding:3px 0 3px 0.5rem;">
        <div style="width:8px;height:8px;border-radius:50%;background:{dot_col};
                    box-shadow:0 0 6px {dot_col}99;flex-shrink:0;"></div>
        <span style="color:{COLORS['text_primary']};font-size:0.8rem;">{name}</span>
        <span style="color:{dot_col};font-size:0.7rem;margin-left:auto;padding-right:0.25rem;">{status}</span>
    </div>
    """, unsafe_allow_html=True)
