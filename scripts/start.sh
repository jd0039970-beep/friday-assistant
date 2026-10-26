#!/usr/bin/env bash
# One-command start: backend + open HUD
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [[ -f .venv/Scripts/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
else
  echo "No venv found. Run scripts/install.sh first."
  exit 1
fi

echo "Starting F.R.I.D.A.Y backend..."
python -m app.main &
PID=$!
echo "Backend PID $PID"
sleep 2

HUD="http://127.0.0.1:8787/hud/"
if command -v xdg-open &>/dev/null; then
  xdg-open "$HUD" &>
/dev/null || true
elif command -v open &>/dev/null; then
  open "$HUD" || true
elif command -v start &>/dev/null; then
  start "$HUD" || true
else
  echo "Open manually: $HUD"
fi

echo "HUD → $HUD"
echo "Tab = talk · Esc = SHUT DOWN"
echo "Ctrl+C here does not kill backend; use Esc in the HUD or: kill $PID"
wait $PID 2>/dev/null || true
