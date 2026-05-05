#!/usr/bin/env bash
# run_feynman.sh "<topic>" "<run_dir>"
# Invokes `feynman deepresearch "<topic>"` in an isolated working dir, then
# harvests every artifact Feynman wrote into <run_dir>/sources/feynman/.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: run_feynman.sh <topic> <run_dir>" >&2
  exit 2
fi

TOPIC="$1"
RUN_DIR="$2"
DEST="$RUN_DIR/sources/feynman"
mkdir -p "$DEST"

if ! command -v feynman >/dev/null 2>&1; then
  echo "[run_feynman] ERROR: feynman not on PATH. Run bootstrap.sh first." >&2
  exit 1
fi

# Use a sandboxed scratch dir so Feynman's outputs/ doesn't collide with the user's cwd.
WORK="$(mktemp -d -t feynman-run-XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

echo "[run_feynman] working dir: $WORK"
echo "[run_feynman] topic: $TOPIC"

cd "$WORK"

# Feynman's deepresearch slash-command is the canonical multi-agent flow.
# We invoke non-interactively by piping the command through stdin and exiting.
# Both shapes are documented; try the explicit subcommand first, fall back to the slash form.
if feynman --help 2>&1 | grep -q 'deepresearch'; then
  feynman deepresearch "$TOPIC" 2>&1 | tee "$DEST/feynman.log"
else
  printf '/deepresearch %s\n/exit\n' "$TOPIC" | feynman 2>&1 | tee "$DEST/feynman.log"
fi

# Harvest. Feynman writes into ./outputs/ (briefs + .provenance.md sidecars),
# ./papers/ (drafts), ./notes/, ./metadata/. Copy whatever exists.
for sub in outputs papers notes metadata; do
  if [[ -d "$WORK/$sub" ]] && [[ -n "$(ls -A "$WORK/$sub" 2>/dev/null)" ]]; then
    mkdir -p "$DEST/$sub"
    cp -R "$WORK/$sub/." "$DEST/$sub/"
    echo "[run_feynman] harvested $sub/ -> $DEST/$sub/"
  fi
done

# Sanity: did we actually get any provenance?
if ! find "$DEST" -name '*.provenance.md' -print -quit | grep -q .; then
  echo "[run_feynman] WARN: no .provenance.md sidecar produced. Citations will be sparse." >&2
fi

echo "[run_feynman] done -> $DEST"
