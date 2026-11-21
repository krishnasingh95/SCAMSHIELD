"""
ScamShield — Main Entry Point
AI-Powered Intelligent Digital Threat Detection and Risk Assessment System

Run with:  streamlit run app.py
"""
import streamlit as st

# ── Landing / redirect to Dashboard ───────────────────────────────────────
# In Streamlit's multipage architecture, each page in pages/ defines its own
# page config, CSS theme, and sidebar navigation cleanly without duplicate call conflicts.
st.switch_page("pages/1_Dashboard.py")
