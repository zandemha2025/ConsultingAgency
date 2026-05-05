#!/usr/bin/env bash
# render_brief.sh <run_dir>
# Reads <run_dir>/brief.md and produces:
#   <run_dir>/brief.pdf  (via weasyprint)
#   <run_dir>/brief.docx (via pandoc)
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: render_brief.sh <run_dir>" >&2
  exit 2
fi

RUN_DIR="$1"
SRC="$RUN_DIR/brief.md"
[[ -f "$SRC" ]] || { echo "[render_brief] missing $SRC" >&2; exit 1; }

# --- PDF via weasyprint ---------------------------------------------------
python3 - <<PY
from pathlib import Path
import markdown, weasyprint
src = Path("$SRC").read_text()
html_body = markdown.markdown(src, extensions=["tables", "fenced_code", "toc", "footnotes"])
css = """
@page { size: Letter; margin: 0.75in 0.85in; }
body  { font-family: 'Helvetica','Arial',sans-serif; color:#0B2A4A; font-size:10.5pt; line-height:1.45; }
h1    { color:#0B2A4A; font-size:20pt; border-bottom:2px solid #0B2A4A; padding-bottom:4px; }
h2    { color:#0B2A4A; font-size:14pt; margin-top:18pt; }
h3    { color:#1F77B4; font-size:12pt; }
img   { max-width:100%; }
table { border-collapse:collapse; width:100%; font-size:9.5pt; }
th,td { border-bottom:1px solid #E5E7EB; padding:4px 6px; text-align:left; }
th    { background:#F3F4F6; }
blockquote { color:#6B7280; border-left:3px solid #1F77B4; padding-left:10px; }
code  { background:#F3F4F6; padding:1px 4px; border-radius:3px; font-size:9.5pt; }
hr    { border:none; border-top:1px solid #E5E7EB; }
.footnote { font-size:8.5pt; color:#6B7280; }
"""
html = f"<html><head><style>{css}</style></head><body>{html_body}</body></html>"
weasyprint.HTML(string=html, base_url="$RUN_DIR").write_pdf("$RUN_DIR/brief.pdf")
print("[render_brief] wrote $RUN_DIR/brief.pdf")
PY

# --- DOCX via pandoc ------------------------------------------------------
if command -v pandoc >/dev/null 2>&1; then
  pandoc "$SRC" \
    --from gfm+footnotes \
    --to docx \
    --resource-path="$RUN_DIR" \
    -o "$RUN_DIR/brief.docx"
  echo "[render_brief] wrote $RUN_DIR/brief.docx"
else
  echo "[render_brief] WARN: pandoc not installed; skipping .docx" >&2
fi
