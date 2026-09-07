#!/bin/sh
# Open the book in a browser, in the pdf.js viewer from pdfjs-wrapper/.
#
# A plain `open darzhaven-izpit-kn.pdf` works too and is one keystroke shorter.
# This exists because the wrapper gives what the built-in viewers do not: the
# book's own 35-chapter outline in a sidebar, so a 499-page PDF can be navigated
# by question number instead of by scrollbar.
#
# A server is required, not a convenience: pdf.js loads as an ES module and
# fetches the PDF, and both are blocked under file://.
#
#   scripts/preview.sh          # serve and open
#   scripts/preview.sh 9001     # ...on another port, if 8801 is taken
set -eu

PORT="${1:-8801}"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
URL="http://localhost:$PORT/pdfjs-wrapper/"

cd "$ROOT"

if [ ! -f darzhaven-izpit-kn.pdf ]; then
  echo "darzhaven-izpit-kn.pdf is missing; run scripts/build_topics.py first." >&2
  exit 1
fi

# Reuse a server already listening on the port instead of failing to bind.
if nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
  echo "reusing the server already on port $PORT"
else
  python3 "$ROOT/scripts/preview_server.py" "$PORT" >/dev/null 2>&1 &
  SERVER=$!
  trap 'kill $SERVER 2>/dev/null || true' EXIT INT TERM
  # Wait for the socket rather than sleeping a guessed interval.
  i=0
  while ! nc -z 127.0.0.1 "$PORT" 2>/dev/null; do
    i=$((i + 1))
    [ "$i" -gt 50 ] && { echo "server did not come up on port $PORT" >&2; exit 1; }
    sleep 0.1
  done
  echo "serving $ROOT on port $PORT (Ctrl-C to stop)"
fi

if command -v open >/dev/null 2>&1; then open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"
else echo "$URL"
fi

# Only hold the terminal when this script owns the server.
[ -n "${SERVER-}" ] && wait "$SERVER"
