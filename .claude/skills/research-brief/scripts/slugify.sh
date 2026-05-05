#!/usr/bin/env bash
# slugify.sh "Some Free-Form Title!" -> some-free-form-title
# Lowercases, strips accents, replaces non-alphanumeric runs with -, trims dashes.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: slugify.sh <string>" >&2
  exit 2
fi

python3 - "$1" <<'PY'
import re, sys, unicodedata
s = sys.argv[1]
s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
s = s.lower()
s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
s = re.sub(r"-{2,}", "-", s)
print(s or "untitled")
PY
