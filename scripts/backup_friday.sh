#!/usr/bin/env bash
set -euo pipefail
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="${HOME}/friday-backup-${STAMP}.tar.gz"
if [[ ! -d "${HOME}/.friday" ]]; then
  echo "Nothing to backup."
  exit 0
fi
tar -czf "$OUT" -C "$HOME" .friday
echo "Backup: $OUT"
echo "Copy off this machine before a wipe."
