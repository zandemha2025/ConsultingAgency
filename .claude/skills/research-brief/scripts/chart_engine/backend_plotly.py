"""Plotly backend - emits PNG via kaleido and (optionally) interactive HTML.

Same `render(spec, out_path)` contract as the matplotlib backend.
"""
from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go

from .spec import ChartSpec

PRIMARY = "#0B2A4A"
PALETTE = ["#0B2A4A", "#1F77B4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#6B7280"]


def _layout(spec: ChartSpec) -> dict:
    annotations = []
    foot_bits = []
    if spec.source:
        foot_bits.append(f"Source: {spec.source}")
    if spec.footnote:
        foot_bits.append(f"Note: {spec.footnote}")
    if foot_bits:
        annotations.append(dict(
            x=0, y=-0.18, xref="paper", yref="paper", showarrow=False,
            text="  |  ".join(foot_bits), font=dict(size=10, color="#6B7280"),
            xanchor="left",
        ))
    return dict(
        title=dict(text=f"<b>{spec.title}</b>", x=0.02, xanchor="left",
                   font=dict(color=PRIMARY, size=16)),
        xaxis=dict(title=spec.x_label, color=PRIMARY, showgrid=False),
        yaxis=dict(title=spec.y_label, color=PRIMARY, gridcolor="#E5E7EB"),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=60, r=30, t=60, b=80),
        annotations=annotations,
        font=dict(color=PRIMARY),
    )


def _bar(spec: ChartSpec) -> go.Figure:
    return go.Figure(go.Bar(x=spec.x, y=spec.y, marker_color=PRIMARY,
                             text=spec.y, textposition="outside"))


def _stacked_bar(spec: ChartSpec) -> go.Figure:
    fig = go.Figure()
    for i, s in enumerate(spec.series):
        fig.add_bar(x=spec.x, y=s["y"], name=s["name"],
                     marker_color=PALETTE[i % len(PALETTE)])
    fig.update_layout(barmode="stack")
    return fig


def _line(spec: ChartSpec) -> go.Figure:
    fig = go.Figure()
    series = spec.series or [{"name": "", "x": spec.x, "y": spec.y}]
    for i, s in enumerate(series):
        fig.add_scatter(x=s["x"], y=s["y"], mode="lines+markers",
                         name=s.get("name", ""),
                         line=dict(color=PALETTE[i % len(PALETTE)], width=3))
    return fig


def _area(spec: ChartSpec) -> go.Figure:
    fig = go.Figure()
    series = spec.series or [{"name": "", "x": spec.x, "y": spec.y}]
    for i, s in enumerate(series):
        fig.add_scatter(x=s["x"], y=s["y"], fill="tozeroy", mode="lines",
                         name=s.get("name", ""),
                         line=dict(color=PALETTE[i % len(PALETTE)], width=2))
    return fig


def _scatter(spec: ChartSpec) -> go.Figure:
    return go.Figure(go.Scatter(x=spec.x, y=spec.y, mode="markers",
                                 marker=dict(color=PRIMARY, size=10)))


def _waterfall(spec: ChartSpec) -> go.Figure:
    w = spec.waterfall or {}
    measure = ["absolute" if k == "abs" else "relative" for k in w.get("kinds", [])]
    return go.Figure(go.Waterfall(
        x=w.get("labels", spec.x),
        y=w.get("values", spec.y),
        measure=measure,
        increasing=dict(marker=dict(color="#10B981")),
        decreasing=dict(marker=dict(color="#EF4444")),
        totals=dict(marker=dict(color=PRIMARY)),
    ))


def _matrix2x2(spec: ChartSpec) -> go.Figure:
    m = spec.matrix or {}
    items = m.get("items", [])
    fig = go.Figure()
    fig.add_scatter(
        x=[it["x"] for it in items], y=[it["y"] for it in items],
        mode="markers+text",
        text=[it["label"] for it in items], textposition="top center",
        marker=dict(size=18, color=PRIMARY),
    )
    fig.update_layout(
        shapes=[
            dict(type="line", x0=0.5, y0=0, x1=0.5, y1=1,
                 line=dict(color="#9CA3AF", width=1)),
            dict(type="line", x0=0, y0=0.5, x1=1, y1=0.5,
                 line=dict(color="#9CA3AF", width=1)),
        ],
        xaxis=dict(range=[0, 1], title=m.get("x_axis", spec.x_label),
                    showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 1], title=m.get("y_axis", spec.y_label),
                    showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


def _marimekko(spec: ChartSpec) -> go.Figure:
    # Approximation: stacked bar with width proportional to series weight.
    fig = go.Figure()
    series = spec.series
    total_w = sum(s.get("weight", 1) for s in series) or 1
    widths = [s.get("weight", 1) / total_w for s in series]
    names = [s["name"] for s in series]
    seg_names = sorted({seg["name"] for s in series for seg in s.get("segments", [])})
    for j, seg_name in enumerate(seg_names):
        ys = []
        for s in series:
            tot = sum(seg["value"] for seg in s.get("segments", [])) or 1
            v = next((seg["value"] for seg in s.get("segments", []) if seg["name"] == seg_name), 0)
            ys.append(v / tot)
        fig.add_bar(x=names, y=ys, name=seg_name, width=widths,
                     marker_color=PALETTE[j % len(PALETTE)])
    fig.update_layout(barmode="stack")
    return fig


def _table(spec: ChartSpec) -> go.Figure:
    headers = spec.raw.get("headers", [])
    rows = spec.raw.get("rows", [])
    cols = list(map(list, zip(*rows))) if rows else [[] for _ in headers]
    return go.Figure(go.Table(
        header=dict(values=headers, fill_color=PRIMARY,
                     font=dict(color="white", size=12), align="left"),
        cells=dict(values=cols, align="left",
                    fill_color="white", font=dict(color=PRIMARY, size=11)),
    ))


_DISPATCH = {
    "bar":         _bar,
    "stacked_bar": _stacked_bar,
    "line":        _line,
    "area":        _area,
    "scatter":     _scatter,
    "waterfall":   _waterfall,
    "matrix2x2":   _matrix2x2,
    "marimekko":   _marimekko,
    "table":       _table,
}


def render(spec: ChartSpec, out_path: Path) -> Path:
    fn = _DISPATCH.get(spec.type)
    if fn is None:
        raise ValueError(f"plotly backend has no renderer for type={spec.type!r}")
    fig = fn(spec)
    fig.update_layout(**_layout(spec))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(out_path, width=1280, height=720, scale=2)
    if spec.interactive_html:
        fig.write_html(out_path.with_suffix(".html"), include_plotlyjs="cdn", full_html=True)
    return out_path
