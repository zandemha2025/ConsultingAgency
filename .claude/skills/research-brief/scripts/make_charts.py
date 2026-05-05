#!/usr/bin/env python3
"""make_charts.py - render chart_engine specs to PNG (and optional interactive HTML).

Usage:
    make_charts.py <spec.json> [--out <dir>] [--backend matplotlib|plotly]

Per-chart "backend" keys in the spec override the default chosen here.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the chart_engine package importable whether we're invoked via
# `python3 scripts/make_charts.py ...` or `python3 -m scripts.make_charts ...`.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from chart_engine import render_all  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Render chart specs to PNG/HTML.")
    p.add_argument("spec", type=Path, help="Path to chart spec JSON file.")
    p.add_argument("--out", type=Path, default=None,
                    help="Output directory (default: spec's parent dir).")
    p.add_argument("--backend", choices=["matplotlib", "plotly"], default="matplotlib",
                    help="Default backend when a chart spec doesn't pin one.")
    args = p.parse_args(argv)

    if not args.spec.exists():
        print(f"[make_charts] spec not found: {args.spec}", file=sys.stderr)
        return 2

    out_dir = args.out or args.spec.parent
    paths = render_all(args.spec, out_dir, default_backend=args.backend)
    for path in paths:
        print(path)
    if not paths:
        print("[make_charts] no charts rendered", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
