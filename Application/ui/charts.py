"""
ScamShield — Chart builders (Plotly-based)
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import COLORS

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
    margin=dict(l=0, r=0, t=30, b=0),
)


def threat_gauge(score: float, title: str = "Threat Score") -> go.Figure:
    """Radial gauge showing overall threat level."""
    color = _score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 1),
        number={"suffix": "%", "font": {"size": 32, "color": color}},
        title={"text": title, "font": {"size": 14, "color": COLORS["text_muted"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["text_muted"],
                     "tickfont": {"color": COLORS["text_muted"]}},
            "bar":  {"color": color, "thickness": 0.25},
            "steps": [
                {"range": [0,  15], "color": COLORS["risk_safe"]    + "22"},
                {"range": [15, 40], "color": COLORS["risk_low"]     + "22"},
                {"range": [40, 65], "color": COLORS["risk_medium"]  + "22"},
                {"range": [65, 85], "color": COLORS["risk_high"]    + "22"},
                {"range": [85,100], "color": COLORS["risk_critical"]+ "22"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.85,
                "value": score * 100,
            },
            "bgcolor": COLORS["bg_tertiary"],
            "bordercolor": COLORS["border"],
        },
    ))
    fig.update_layout(**_PLOTLY_LAYOUT, height=260)
    return fig


def scan_history_bar(records: list) -> go.Figure:
    """Bar chart: scan count by type (last N records)."""
    if not records:
        return _empty_chart("No scan history yet")
    df  = pd.DataFrame(records)
    agg = df.groupby("scan_type").size().reset_index(name="count")
    fig = px.bar(
        agg, x="scan_type", y="count",
        color="scan_type",
        color_discrete_sequence=[COLORS["accent_blue"], COLORS["accent_cyan"], COLORS["accent_purple"]],
        labels={"scan_type": "Scan Type", "count": "Total Scans"},
        title="Scans by Type",
    )
    fig.update_layout(**_PLOTLY_LAYOUT, showlegend=False, height=280)
    fig.update_traces(marker_line_width=0)
    return fig


def risk_distribution_pie(records: list) -> go.Figure:
    """Donut chart: safe vs threat distribution."""
    if not records:
        return _empty_chart("No data")
    df     = pd.DataFrame(records)
    counts = df["risk_level"].value_counts().reset_index()
    counts.columns = ["risk_level", "count"]

    color_map = {
        "SAFE":     COLORS["risk_safe"],
        "LOW":      COLORS["risk_low"],
        "MEDIUM":   COLORS["risk_medium"],
        "HIGH":     COLORS["risk_high"],
        "CRITICAL": COLORS["risk_critical"],
        "UNKNOWN":  COLORS["text_muted"],
    }
    colors = [color_map.get(r, COLORS["text_muted"]) for r in counts["risk_level"]]

    fig = go.Figure(go.Pie(
        labels=counts["risk_level"],
        values=counts["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=COLORS["bg_primary"], width=2)),
        textfont=dict(color=COLORS["text_primary"]),
    ))
    fig.update_layout(**_PLOTLY_LAYOUT, title="Risk Distribution",
                      legend=dict(font=dict(color=COLORS["text_muted"])), height=280)
    return fig


def timeline_chart(records: list) -> go.Figure:
    """Line chart: scans over time."""
    if len(records) < 2:
        return _empty_chart("Not enough history for timeline")
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    daily = df.set_index("timestamp").resample("D").size().reset_index(name="count")
    fig = go.Figure(go.Scatter(
        x=daily["timestamp"], y=daily["count"],
        mode="lines+markers",
        line=dict(color=COLORS["accent_cyan"], width=2),
        marker=dict(color=COLORS["accent_blue"], size=6),
        fill="tozeroy",
        fillcolor=COLORS["accent_blue"] + "22",
    ))
    fig.update_layout(**_PLOTLY_LAYOUT, title="Scan Activity Over Time",
                      xaxis=dict(gridcolor=COLORS["border"]),
                      yaxis=dict(gridcolor=COLORS["border"]), height=260)
    return fig


def feature_radar(features: dict, title: str = "Feature Profile") -> go.Figure:
    """Radar chart for normalized feature values."""
    exclude = {k for k in features if k.startswith("_")}
    keys    = [k for k in features if k not in exclude]
    vals    = [float(features[k]) for k in keys]
    if not keys:
        return _empty_chart("No features to display")
    # Normalize 0–1 for display
    max_v = max(vals) if max(vals) > 0 else 1
    norm  = [v / max_v for v in vals]
    fig = go.Figure(go.Scatterpolar(
        r=norm + [norm[0]],
        theta=keys + [keys[0]],
        fill="toself",
        fillcolor=COLORS["accent_blue"] + "33",
        line=dict(color=COLORS["accent_cyan"]),
    ))
    fig.update_layout(
        **_PLOTLY_LAYOUT,
        polar=dict(
            bgcolor=COLORS["bg_tertiary"],
            radialaxis=dict(visible=True, color=COLORS["text_muted"],
                            gridcolor=COLORS["border"]),
            angularaxis=dict(color=COLORS["text_muted"],
                             gridcolor=COLORS["border"]),
        ),
        title=title, height=320,
    )
    return fig


def _score_color(score: float) -> str:
    if score >= 0.85: return COLORS["risk_critical"]
    if score >= 0.65: return COLORS["risk_high"]
    if score >= 0.40: return COLORS["risk_medium"]
    if score >= 0.15: return COLORS["risk_low"]
    return COLORS["risk_safe"]


def _empty_chart(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color=COLORS["text_muted"], size=14))
    fig.update_layout(**_PLOTLY_LAYOUT, height=200)
    return fig
