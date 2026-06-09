#!/usr/bin/env bash
# Agent Sanad — one-command local launch (macOS/Linux/Git-Bash).
# Starts the API + UI on http://127.0.0.1:8000 in offline mock mode.
set -euo pipefail
cd "$(dirname "$0")"

if command -v lsof >/dev/null 2>&1 && lsof -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8000 is already in use — that server may be an OLDER build." >&2
  echo "Stop it first (lsof -iTCP:8000) and re-run." >&2
  exit 1
fi

export PYTHONPATH=.
export LOCAL_MOCK_MODE=true
export SANAD_LIVE_EXTRACTION=1   # live synthetic GOLDEN certificate parse (cached fallback)

echo "Agent Sanad starting on http://127.0.0.1:8000  (offline mock mode)"
exec python -B -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
