"""Custom chart engine: JSON spec -> PNG (and optional interactive HTML).

Public API:
    render_all(spec_path, out_dir, default_backend="matplotlib") -> list[Path]
    render_one(chart_spec, out_dir, backend) -> Path

Backends are pluggable - adding a new one is a single file under this package
exposing `render(spec: ChartSpec, out_path: Path) -> Path`.
"""
from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from typing import Iterable

from .spec import ChartSpec, load_specs

_BACKENDS = {
    "matplotlib": "scripts.chart_engine.backend_matplotlib",
    "plotly":     "scripts.chart_engine.backend_plotly",
}


def _load_backend(name: str):
    if name not in _BACKENDS:
        raise ValueError(f"unknown chart backend: {name!r}; choose from {sorted(_BACKENDS)}")
    # Try the package-qualified import first, then a relative one (when the package
    # is invoked directly without scripts/ on sys.path).
    try:
        return import_module(_BACKENDS[name])
    except ModuleNotFoundError:
        return import_module(f".backend_{name}", package=__name__)


def render_one(spec: ChartSpec, out_dir: Path, backend: str = "matplotlib") -> Path:
    """Render a single chart spec, returning the path of the produced PNG."""
    out_dir.mkdir(parents=True, exist_ok=True)
    backend_name = spec.backend or backend
    mod = _load_backend(backend_name)
    out_path = out_dir / f"{spec.id}.png"
    return mod.render(spec, out_path)


def render_all(
    spec_path: Path,
    out_dir: Path,
    default_backend: str = "matplotlib",
) -> list[Path]:
    """Render every chart in `spec_path` (a JSON array of specs)."""
    specs = load_specs(spec_path)
    out_dir = Path(out_dir)
    paths: list[Path] = []
    for s in specs:
        try:
            paths.append(render_one(s, out_dir, backend=default_backend))
        except Exception as exc:  # one bad chart shouldn't kill the rest
            print(f"[chart_engine] FAIL {s.id}: {exc}")
    return paths


__all__ = ["ChartSpec", "render_all", "render_one", "load_specs"]
