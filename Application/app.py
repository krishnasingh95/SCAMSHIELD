"""
ScamShield — Main Entry Point
AI-Powered Intelligent Digital Threat Detection and Risk Assessment System

Run with:  streamlit run app.py
"""
import os
import sys
import streamlit as st

# Ensure Application directory is in sys.path when running from repo root
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# ── Landing / redirect to Dashboard ───────────────────────────────────────
# In Streamlit's multipage architecture, each page in pages/ defines its own
# page config, CSS theme, and sidebar navigation cleanly without duplicate call conflicts.
st.switch_page("pages/1_Dashboard.py")
