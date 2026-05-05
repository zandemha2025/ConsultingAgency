#!/usr/bin/env bash
# render_deck.sh <run_dir>
# Reads <run_dir>/deck.md and produces:
#   <run_dir>/deck/deck.html
#   <run_dir>/deck/deck.pdf
#   <run_dir>/deck/deck.pptx
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: render_deck.sh <run_dir>" >&2
  exit 2
fi

RUN_DIR="$1"
SRC="$RUN_DIR/deck.md"
[[ -f "$SRC" ]] || { echo "[render_deck] missing $SRC" >&2; exit 1; }

OUT="$RUN_DIR/deck"
mkdir -p "$OUT"

if ! command -v npx >/dev/null 2>&1; then
  echo "[render_deck] ERROR: npx not on PATH (need Node.js >= 20)." >&2
  exit 1
fi

# Marp CLI handles HTML, PDF, and PPTX from the same source.
# --allow-local-files lets it embed the chart PNGs referenced from the deck.
COMMON=(--allow-local-files --html)

npx -y @marp-team/marp-cli "${COMMON[@]}" --html-output "$OUT/deck.html" "$SRC" \
  || { echo "[render_deck] HTML render failed"; exit 1; }
echo "[render_deck] wrote $OUT/deck.html"

npx -y @marp-team/marp-cli "${COMMON[@]}" --pdf  --output "$OUT/deck.pdf"  "$SRC" \
  || echo "[render_deck] WARN: PDF render failed (Chromium may be missing)."
[[ -f "$OUT/deck.pdf" ]] && echo "[render_deck] wrote $OUT/deck.pdf"

npx -y @marp-team/marp-cli "${COMMON[@]}" --pptx --output "$OUT/deck.pptx" "$SRC" \
  || echo "[render_deck] WARN: PPTX render failed."
[[ -f "$OUT/deck.pptx" ]] && echo "[render_deck] wrote $OUT/deck.pptx"
