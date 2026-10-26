#!/usr/bin/env bash
set -euo pipefail

echo "== F.R.I.D.A.Y local install (Linux/macOS) =="

if ! command -v ollama &>/dev/null; then
  echo "-- Installing Ollama"
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "-- Pulling models (this downloads a few GB, offline after this)"
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull nomic-embed-text

echo "-- Setting up Python venv"
cd "$(dirname "$0")/../backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "-- Building sandbox Docker image (optional, needed for security module)"
if command -v docker &>/dev/null; then
  docker build -t friday-sandbox:latest -f ../scripts/Dockerfile.sandbox .
else
  echo "   Docker not found — skipping; the security sandbox tools won't work until it's installed."
fi

cat <<'EOF'

Done.

Next steps:
  1. source backend/.venv/bin/activate
  2. cd backend && python -m app.main
  3. (optional) install Piper for voice output: https://github.com/rhasspy/piper

EOF
