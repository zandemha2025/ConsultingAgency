#!/usr/bin/env bash
# Idempotent bootstrap for the research-brief skill.
# - Auto-installs Feynman if missing (HARD dependency, no prompt).
# - Ensures marp-cli is reachable via npx.
# - Installs Python deps (matplotlib, plotly, kaleido, pandas, python-pptx, weasyprint, markdown).
# - Ensures pandoc exists (needed for .docx).
set -euo pipefail

log() { printf '[bootstrap] %s\n' "$*" >&2; }

# 1. Feynman --------------------------------------------------------------
# Two install paths; we try them in order. (1) npm registry - works in any env
# with internet to npmjs.org and Node >= 20. (2) Official feynman.is curl|bash
# bundled installer - heavier but ships its own Node runtime.
install_feynman_npm() {
  command -v npm >/dev/null 2>&1 || return 1
  log "trying npm: npm install -g @companion-ai/feynman"
  if npm install -g --silent @companion-ai/feynman 2>&1 | tail -20 >&2; then
    return 0
  fi
  return 1
}

install_feynman_curl() {
  command -v curl >/dev/null 2>&1 || return 1
  log "trying curl: feynman.is/install"
  curl -fsSL https://feynman.is/install | bash
}

if ! command -v feynman >/dev/null 2>&1; then
  log "feynman not found; trying optional install (skill works without it)..."
  if install_feynman_npm 2>/dev/null || install_feynman_curl 2>/dev/null; then
    for candidate in "$HOME/.feynman/bin" "$HOME/.local/bin" "/usr/local/bin" \
                     "$(npm bin -g 2>/dev/null || echo /usr/lib/node_modules/.bin)"; do
      [[ -x "$candidate/feynman" ]] && { export PATH="$candidate:$PATH"; break; }
    done
  fi
  if command -v feynman >/dev/null 2>&1; then
    log "feynman installed: $(command -v feynman)"
  else
    log "feynman not available; native multi-agent flow will be used (this is fine)."
  fi
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

# 4. Chrome for marp-cli (PDF/PPTX rendering needs a real Chrome) -------
# Ubuntu's chromium-browser is a snap stub; use Puppeteer's bundled Chrome instead.
# Idempotent: skips if a working Chrome is already on disk.
if [[ ! -x "$HOME/.cache/puppeteer/chrome/"*"/chrome-linux64/chrome" ]] 2>/dev/null \
   && ! ls "$HOME/.cache/puppeteer/chrome/"*"/chrome-linux64/chrome" >/dev/null 2>&1; then
  if command -v npx >/dev/null 2>&1; then
    log "installing Puppeteer's Chrome (one-time, ~150MB)..."
    npx -y puppeteer browsers install chrome >/dev/null 2>&1 || \
      log "WARN: puppeteer chrome install failed; deck PDF/PPTX will fail. Try manually: npx puppeteer browsers install chrome"
  fi
fi

# Write a marp config that forces --no-sandbox (required when running as root in containers).
CHROME_BIN="$(ls "$HOME/.cache/puppeteer/chrome/"*"/chrome-linux64/chrome" 2>/dev/null | head -1 || true)"
if [[ -n "$CHROME_BIN" ]]; then
  cat > "$HOME/.marp.config.js" <<EOF
module.exports = {
  browser: 'chrome',
  browserPath: '$CHROME_BIN',
  browserArgs: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
};
EOF
  log "marp config written: $HOME/.marp.config.js (Chrome: $CHROME_BIN)"
fi

# 5. pandoc --------------------------------------------------------------
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
