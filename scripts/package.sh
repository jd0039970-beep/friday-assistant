#!/usr/bin/env bash
# Best-effort packaging helper
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "F.R.I.D.A.Y package helper"
echo "1. Backend is Python — use the install scripts for deps."
echo "2. Desktop shell: cd frontend/tauri && npm install && npm run tauri build"
echo "3. Optional: PyInstaller for a single backend binary (advanced)."
echo "Done. Prefer 'python -m app.main' + HUD/Tauri for daily use."
