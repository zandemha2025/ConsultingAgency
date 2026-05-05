"""Chart spec dataclasses + JSON loader.

Spec format (array of chart objects):

  {
    "id": "ev-tam",                       # required, used as filename
    "type": "bar",                        # bar | stacked_bar | line | area | scatter |
                                          # waterfall | matrix2x2 | marimekko | table
    "title": "EV TAM by segment, 2025E",
    "x":     ["Passenger","LCV","HCV","2-wheeler"],
    "y":     [420, 110, 65, 28],
    "series": [{"name":"AC","x":[...],"y":[...]}, ...],   # for line/area/stacked
    "x_label": "Segment",
    "y_label": "$B",
    "source":  "IEA Global EV Outlook 2025",
    "footnote": "FX at 2024 spot rates",
    "backend": "matplotlib",              # optional override; else CLI default
    "interactive_html": false,            # plotly only: also emit .html
    # Type-specific extras:
    "matrix": {                           # for matrix2x2
       "x_axis": "Market attractiveness",
       "y_axis": "Right-to-win",
       "items": [{"label":"Vertical A","x":0.7,"y":0.4}, ...]
    },
    "waterfall": {                        # for waterfall
       "labels":["Start","+New","+Up","-Churn","End"],
       "values":[100, 30, 10, -15, 125],
       "kinds":["abs","rel","rel","rel","abs"]
    }
  }
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ChartSpec:
    id: str
    type: str
    title: str
    source: str = ""
    footnote: str = ""
    x: list[Any] = field(default_factory=list)
    y: list[Any] = field(default_factory=list)
    series: list[dict] = field(default_factory=list)
    x_label: str = ""
    y_label: str = ""
    backend: str | None = None
    interactive_html: bool = False
    matrix: dict | None = None
    waterfall: dict | None = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "ChartSpec":
        if "id" not in d or "type" not in d or "title" not in d:
            raise ValueError(f"chart spec missing id/type/title: {d!r}")
        return cls(
            id=d["id"],
            type=d["type"],
            title=d["title"],
            source=d.get("source", ""),
            footnote=d.get("footnote", ""),
            x=list(d.get("x", [])),
            y=list(d.get("y", [])),
            series=list(d.get("series", [])),
            x_label=d.get("x_label", ""),
            y_label=d.get("y_label", ""),
            backend=d.get("backend"),
            interactive_html=bool(d.get("interactive_html", False)),
            matrix=d.get("matrix"),
            waterfall=d.get("waterfall"),
            raw=d,
        )


def load_specs(path: Path) -> list[ChartSpec]:
    path = Path(path)
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array of chart specs")
    return [ChartSpec.from_dict(d) for d in data]
