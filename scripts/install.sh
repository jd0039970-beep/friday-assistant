#!/usr/bin/env bash
# F.R.I.D.A.Y self-healing Linux/macOS install
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "========================================"
echo " F.R.I.D.A.Y self-healing install"
echo "========================================"

command -v python3 >/dev/null || { echo "Install Python 3.11+"; exit 1; }
echo "[OK] $(python3 --version)"

cd "$ROOT/backend"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
else
  pip install fastapi "uvicorn[standard]" httpx pyyaml numpy pillow faster-whisper pydantic python-multipart
fi
echo "[OK] Python packages"

mkdir -p "$HOME/.friday"/{skills,plans,inbox}
echo "[OK] ~/.friday"

if command -v ollama >/dev/null; then
  echo "[--] Pulling models..."
  ollama pull qwen2.5:7b-instruct-q4_K_M
  ollama pull nomic-embed-text
  echo "[OK] Models"
else
  echo "[!] Install Ollama from https://ollama.com/download then re-run to pull models"
fi

command -v docker >/dev/null && echo "[OK] Docker" || echo "[!] Docker optional for sandbox"

chmod +x "$ROOT/scripts/start.sh" "$ROOT/scripts/backup_friday.sh" "$ROOT/scripts/restore_friday.sh" 2>/dev/null || true

echo ""
echo "Install complete. Start with: bash scripts/start.sh"
echo "BEFORE wipe: bash scripts/backup_friday.sh"
echo "AFTER reinstall: bash scripts/restore_friday.sh"
