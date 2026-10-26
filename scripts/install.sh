#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "  F.R.I.D.A.Y local install (Linux / macOS)"
echo "=============================================="

# --- Ollama ---
if ! command -v ollama &>/dev/null; then
  echo "-- Installing Ollama"
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "-- Ollama already installed"
fi

echo "-- Pulling models (one-time download, then fully offline)"
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull nomic-embed-text

# --- Python ---
echo "-- Setting up Python virtual environment"
cd "$(dirname "$0")/../backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Playwright browsers (for web tools)
echo "-- Installing Playwright Chromium"
playwright install chromium || echo "   Playwright browser install skipped / failed"

# --- Docker sandbox (optional) ---
if command -v docker &>/dev/null; then
  echo "-- Building security sandbox Docker image"
  docker build -t friday-sandbox:latest -f ../scripts/Dockerfile.sandbox ../scripts || true
else
  echo "-- Docker not found. Security sandbox tools will be unavailable until Docker is installed."
fi

# --- Piper TTS (recommended) ---
echo "-- Piper TTS (British female voice)"
echo "   Run after activate:  pip install piper-tts && python -m piper.download_voices en_GB-alba-medium"

# --- Tesseract (OCR) ---
if ! command -v tesseract &>/dev/null; then
  echo "-- Tesseract OCR not found. Install it for screen reading:"
  echo "   Ubuntu/Debian: sudo apt install tesseract-ocr"
  echo "   macOS:         brew install tesseract"
fi

cat <<'EOF'

==============================================
  Install complete.
==============================================

Next steps:
  1. source backend/.venv/bin/activate
  2. cd backend && python -m app.main
  3. (optional) install Piper voice:
       pip install piper-tts
       python -m piper.download_voices en_GB-alba-medium
  4. Test:
       curl -X POST http://127.0.0.1:8787/chat \
         -H 'Content-Type: application/json' \
         -d '{"message": "Hello Friday, status report."}'

EOF
