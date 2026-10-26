#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-}"
if [[ -z "$ZIP" ]]; then
  ZIP=$(ls -t "$HOME"/friday-backup-*.tar.gz 2>/dev/null | head -1 || true)
fi
if [[ -z "$ZIP" || ! -f "$ZIP" ]]; then
  echo "Usage: $0 /path/to/friday-backup-XXXX.tar.gz"
  exit 1
fi
tar -xzf "$ZIP" -C "$HOME"
echo "Restored ~/.friday from $ZIP"
