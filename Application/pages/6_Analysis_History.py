"""
ScamShield — Page 6: Analysis History
Searchable, filterable log of all past scans with export functionality.
"""
import streamlit as st
import pandas as pd
from config import PAGE_CONFIG, COLORS
from ui.theme import inject_css
from ui.sidebar import render_sidebar
from ui.cards import page_header, section_divider
from ui.charts import risk_distribution_pie, scan_history_bar, timeline_chart
from core.history_manager import get_all, clear_history, get_stats

st.set_page_config(**PAGE_CONFIG)
inject_css()
render_sidebar()

page_header("📁", "Analysis History",
            "Browse, filter and export all past scan records")

records = get_all()
stats   = get_stats()

# ── Stats strip ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Records",  stats.get("total", 0))
with c2: st.metric("Threats",        stats.get("scam",  0))
with c3: st.metric("Safe",           stats.get("safe",  0))
with c4:
    by_type = stats.get("by_type", {})
    most    = max(by_type, key=by_type.get) if by_type else "—"
    st.metric("Most Used Scanner",   most)

section_divider("HISTORY CHARTS")

if records:
    hc1, hc2, hc3 = st.columns(3)
    with hc1: st.plotly_chart(scan_history_bar(records),       use_container_width=True)
    with hc2: st.plotly_chart(risk_distribution_pie(records),  use_container_width=True)
    with hc3: st.plotly_chart(timeline_chart(records),         use_container_width=True)
else:
    st.markdown(f"""
    <div style="text-align:center;padding:3rem;color:{COLORS['text_muted']};">
        <div style="font-size:2.5rem;">📭</div>
        <p>No history yet. Run some scans first.</p>
    </div>
    """, unsafe_allow_html=True)

section_divider("FILTER & SEARCH")

# ── Filters ───────────────────────────────────────────────────────────────
if records:
    df = pd.DataFrame(records)

    f1, f2, f3 = st.columns(3)
    with f1:
        types = ["All"] + sorted(df["scan_type"].unique().tolist())
        sel_type = st.selectbox("Scan Type", types, key="hist_type")
    with f2:
        levels = ["All"] + sorted(df["risk_level"].dropna().unique().tolist())
        sel_level = st.selectbox("Risk Level", levels, key="hist_level")
    with f3:
        search = st.text_input("Search input preview", placeholder="keyword…", key="hist_search")

    filtered = df.copy()
    if sel_type  != "All":    filtered = filtered[filtered["scan_type"]  == sel_type]
    if sel_level != "All":    filtered = filtered[filtered["risk_level"] == sel_level]
    if search.strip():        filtered = filtered[filtered["input_preview"].str.contains(
                                              search.strip(), case=False, na=False)]

    st.caption(f"Showing {len(filtered)} / {len(df)} records")

    # ── Colour-code risk level column ─────────────────────────────────────
    display_cols = ["timestamp","scan_type","input_preview","risk_level","label","confidence","status"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    disp = filtered[display_cols].copy()
    disp["confidence"] = disp["confidence"].apply(
        lambda x: f"{x*100:.1f}%" if x is not None and str(x) != "nan" else "—"
    )
    disp.columns = [c.replace("_"," ").title() for c in disp.columns]

    st.dataframe(disp, use_container_width=True, hide_index=True)

    # ── Export ────────────────────────────────────────────────────────────
    section_divider("EXPORT")
    ex1, ex2, ex3 = st.columns([1, 1, 3])
    with ex1:
        st.download_button(
            "⬇️ Export CSV",
            filtered.to_csv(index=False),
            file_name="scamshield_history.csv",
            mime="text/csv",
        )
    with ex2:
        st.download_button(
            "⬇️ Export JSON",
            filtered.to_json(orient="records", indent=2),
            file_name="scamshield_history.json",
            mime="application/json",
        )
    with ex3:
        if st.button("🗑️ Clear All History", type="secondary"):
            clear_history()
            st.success("History cleared.")
            st.rerun()
