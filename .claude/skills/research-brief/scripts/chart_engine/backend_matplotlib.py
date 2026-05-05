"""Matplotlib backend - PNG output only. Chart styling is deliberately MBB-clean:
no gridlines clutter, light gray accents, dark navy primary, source line at bottom."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from .spec import ChartSpec  # noqa: E402

PRIMARY = "#0B2A4A"      # deep navy
ACCENT  = "#1F77B4"
MUTED   = "#9CA3AF"
GRID    = "#E5E7EB"
PALETTE = ["#0B2A4A", "#1F77B4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#6B7280"]

DPI = 180
FIGSIZE = (8.0, 4.5)


def _new_axes(spec: ChartSpec):
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_title(spec.title, loc="left", fontsize=13, fontweight="bold", color=PRIMARY, pad=12)
    if spec.x_label:
        ax.set_xlabel(spec.x_label, color=PRIMARY)
    if spec.y_label:
        ax.set_ylabel(spec.y_label, color=PRIMARY)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=PRIMARY)
    return fig, ax


def _footer(fig, spec: ChartSpec):
    bits = []
    if spec.source:
        bits.append(f"Source: {spec.source}")
    if spec.footnote:
        bits.append(f"Note: {spec.footnote}")
    if bits:
        fig.text(0.02, 0.01, "  |  ".join(bits), fontsize=8, color=MUTED)


def _save(fig, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path


def _bar(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    ax.bar(spec.x, spec.y, color=PRIMARY, edgecolor="white")
    for i, v in enumerate(spec.y):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9, color=PRIMARY)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    _footer(fig, spec)
    return _save(fig, out_path)


def _stacked_bar(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    bottom = [0.0] * len(spec.x)
    for i, s in enumerate(spec.series):
        ax.bar(spec.x, s["y"], bottom=bottom, label=s["name"],
               color=PALETTE[i % len(PALETTE)], edgecolor="white")
        bottom = [b + v for b, v in zip(bottom, s["y"])]
    ax.legend(frameon=False, loc="upper left")
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    _footer(fig, spec)
    return _save(fig, out_path)


def _line(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    series = spec.series or [{"name": "", "x": spec.x, "y": spec.y}]
    for i, s in enumerate(series):
        ax.plot(s["x"], s["y"], label=s.get("name", ""),
                color=PALETTE[i % len(PALETTE)], linewidth=2.2, marker="o", markersize=4)
    if any(s.get("name") for s in series):
        ax.legend(frameon=False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    _footer(fig, spec)
    return _save(fig, out_path)


def _area(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    series = spec.series or [{"name": "", "x": spec.x, "y": spec.y}]
    for i, s in enumerate(series):
        ax.fill_between(s["x"], s["y"], alpha=0.55, color=PALETTE[i % len(PALETTE)],
                         label=s.get("name", ""))
    if any(s.get("name") for s in series):
        ax.legend(frameon=False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    _footer(fig, spec)
    return _save(fig, out_path)


def _scatter(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    ax.scatter(spec.x, spec.y, color=PRIMARY, s=60, alpha=0.8, edgecolor="white")
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    _footer(fig, spec)
    return _save(fig, out_path)


def _waterfall(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    w = spec.waterfall or {}
    labels = w.get("labels", spec.x)
    values = w.get("values", spec.y)
    kinds = w.get("kinds", ["rel"] * len(values))

    cum = 0.0
    for i, (lbl, val, kind) in enumerate(zip(labels, values, kinds)):
        if kind == "abs":
            ax.bar(i, val, color=PRIMARY, edgecolor="white")
            cum = val
            top = val
        else:
            color = "#10B981" if val >= 0 else "#EF4444"
            ax.bar(i, val, bottom=cum, color=color, edgecolor="white")
            cum += val
            top = cum
        ax.text(i, top, f"{top:,.0f}" if kind == "abs" else f"{val:+,.0f}",
                 ha="center", va="bottom", fontsize=9, color=PRIMARY)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    _footer(fig, spec)
    return _save(fig, out_path)


def _matrix2x2(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    m = spec.matrix or {}
    items = m.get("items", [])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axhline(0.5, color=MUTED, linewidth=0.8)
    ax.axvline(0.5, color=MUTED, linewidth=0.8)
    # Quadrant tints
    ax.add_patch(Rectangle((0.5, 0.5), 0.5, 0.5, color="#10B981", alpha=0.08))
    ax.add_patch(Rectangle((0,   0.5), 0.5, 0.5, color="#F59E0B", alpha=0.08))
    ax.add_patch(Rectangle((0.5, 0  ), 0.5, 0.5, color="#F59E0B", alpha=0.08))
    ax.add_patch(Rectangle((0,   0  ), 0.5, 0.5, color="#EF4444", alpha=0.08))
    for it in items:
        ax.scatter(it["x"], it["y"], s=120, color=PRIMARY, edgecolor="white", zorder=3)
        ax.annotate(it["label"], (it["x"], it["y"]), xytext=(6, 6),
                     textcoords="offset points", fontsize=9, color=PRIMARY)
    ax.set_xlabel(m.get("x_axis", spec.x_label), color=PRIMARY)
    ax.set_ylabel(m.get("y_axis", spec.y_label), color=PRIMARY)
    ax.set_xticks([]); ax.set_yticks([])
    _footer(fig, spec)
    return _save(fig, out_path)


def _marimekko(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    # Expect spec.series = [{name, weight, segments:[{name,value}]}, ...]
    series = spec.series
    total_w = sum(s.get("weight", 1) for s in series) or 1
    x0 = 0.0
    for i, s in enumerate(series):
        w = s.get("weight", 1) / total_w
        segs = s.get("segments", [])
        seg_total = sum(seg["value"] for seg in segs) or 1
        y0 = 0.0
        for j, seg in enumerate(segs):
            h = seg["value"] / seg_total
            ax.add_patch(Rectangle((x0, y0), w, h,
                                    color=PALETTE[j % len(PALETTE)], edgecolor="white"))
            ax.text(x0 + w / 2, y0 + h / 2, seg["name"],
                     ha="center", va="center", fontsize=8, color="white")
            y0 += h
        ax.text(x0 + w / 2, -0.04, s["name"], ha="center", va="top",
                 fontsize=9, color=PRIMARY)
        x0 += w
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    _footer(fig, spec)
    return _save(fig, out_path)


def _table(spec: ChartSpec, out_path: Path) -> Path:
    fig, ax = _new_axes(spec)
    ax.axis("off")
    headers = spec.raw.get("headers") or [""] + [s.get("name", "") for s in spec.series]
    rows = spec.raw.get("rows", [])
    table = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.4)
    _footer(fig, spec)
    return _save(fig, out_path)


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
        raise ValueError(f"matplotlib backend has no renderer for type={spec.type!r}")
    return fn(spec, out_path)
