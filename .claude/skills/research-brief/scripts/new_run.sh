#!/usr/bin/env bash
# new_run.sh "<client>" "<topic>"
# Creates ~/Desktop/consulting/<client-slug>/<topic-slug>-YYYYMMDD/{charts,sources,deck}
# Prints the absolute path of the run dir on stdout.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: new_run.sh <client> <topic>" >&2
  exit 2
fi

CLIENT="$1"
TOPIC="$2"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLUGIFY="$HERE/slugify.sh"

CLIENT_SLUG="$(bash "$SLUGIFY" "$CLIENT")"
TOPIC_SLUG="$(bash "$SLUGIFY" "$TOPIC")"
DATE="$(date +%Y%m%d)"

ROOT="$HOME/Desktop/consulting"
RUN="$ROOT/$CLIENT_SLUG/${TOPIC_SLUG}-${DATE}"

mkdir -p "$RUN"/{charts,sources,deck}

# Drop a tiny meta file so the run is self-describing.
cat > "$RUN/.run.json" <<EOF
{
  "client": $(printf '%s' "$CLIENT" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))'),
  "topic":  $(printf '%s' "$TOPIC"  | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))'),
  "client_slug": "$CLIENT_SLUG",
  "topic_slug":  "$TOPIC_SLUG",
  "created_at":  "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "$RUN"
