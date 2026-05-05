#!/usr/bin/env bash
# Idempotent bootstrap for the research-brief skill.
# - Auto-installs Feynman if missing (HARD dependency, no prompt).
# - Ensures marp-cli is reachable via npx.
# - Installs Python deps (matplotlib, plotly, kaleido, pandas, python-pptx, weasyprint, markdown).
# - Ensures pandoc exists (needed for .docx).
set -euo pipefail

log() { printf '[bootstrap] %s\n' "$*" >&2; }

# 1. Feynman --------------------------------------------------------------
if ! command -v feynman >/dev/null 2>&1; then
  log "feynman not found; installing via official installer..."
  if ! command -v curl >/dev/null 2>&1; then
    log "ERROR: curl is required to install feynman. Install curl and retry."
    exit 1
  fi
  if ! curl -fsSL https://feynman.is/install | bash; then
    log "ERROR: feynman install failed. See output above."
    exit 1
  fi
  # The installer typically drops binaries into ~/.feynman/bin or /usr/local/bin.
  for candidate in "$HOME/.feynman/bin" "$HOME/.local/bin" "/usr/local/bin"; do
    if [[ -x "$candidate/feynman" ]]; then
      export PATH="$candidate:$PATH"
      break
    fi
  done
  if ! command -v feynman >/dev/null 2>&1; then
    log "ERROR: feynman installed but not on PATH. Add ~/.feynman/bin to PATH and retry."
    exit 1
  fi
  log "feynman installed: $(command -v feynman)"
else
  log "feynman: $(command -v feynman)"
fi

# 2. marp-cli (via npx, cached) ------------------------------------------
if ! command -v npx >/dev/null 2>&1; then
  log "WARN: npx not found; deck rendering will fail. Install Node.js >= 20."
else
  npx -y -q @marp-team/marp-cli --version >/dev/null 2>&1 || \
    log "WARN: marp-cli probe failed (network?). Will retry at deck render time."
fi

# 3. Python deps ---------------------------------------------------------
PY_DEPS=(matplotlib plotly kaleido pandas python-pptx weasyprint markdown)
MISSING_PY=()
for pkg in "${PY_DEPS[@]}"; do
  modname="${pkg//-/_}"
  # python-pptx imports as 'pptx'; weasyprint imports as 'weasyprint'; markdown as 'markdown'
  case "$pkg" in
    python-pptx) modname="pptx" ;;
  esac
  if ! python3 -c "import $modname" >/dev/null 2>&1; then
    MISSING_PY+=("$pkg")
  fi
done
if (( ${#MISSING_PY[@]} > 0 )); then
  log "installing python deps: ${MISSING_PY[*]}"
  python3 -m pip install --quiet --user "${MISSING_PY[@]}" || {
    log "ERROR: pip install failed for: ${MISSING_PY[*]}"
    exit 1
  }
fi

# 4. pandoc --------------------------------------------------------------
if ! command -v pandoc >/dev/null 2>&1; then
  log "pandoc not found; attempting install..."
  if command -v apt-get >/dev/null 2>&1; then
    if [[ $EUID -eq 0 ]]; then
      apt-get update -qq && apt-get install -y -qq pandoc || log "WARN: apt install pandoc failed."
    else
      sudo -n apt-get install -y -qq pandoc 2>/dev/null || \
        log "WARN: pandoc missing and no passwordless sudo; .docx render will fail. Run: sudo apt-get install -y pandoc"
    fi
  elif command -v brew >/dev/null 2>&1; then
    brew install pandoc >/dev/null 2>&1 || log "WARN: brew install pandoc failed."
  else
    log "WARN: no apt/brew available; install pandoc manually for .docx output."
  fi
fi

log "bootstrap OK."
