# F.R.I.D.A.Y — Local Iron-Man AI Assistant

**100% local · zero cost · full PC control · voice · vision · sandboxed security tools**

A realistic desktop AI assistant inspired by MCU F.R.I.D.A.Y / J.A.R.V.I.S.
Runs a small open-weight LLM through Ollama, sees your screen, hears you, speaks back,
controls mouse/keyboard/windows/files, browses the web, and includes a strictly
sandboxed security-testing module for your own lab / CTF / owned hardware.

## Features

| Domain | Capability |
|--------|------------|
| **Brain** | Qwen2.5-7B (or 3B fallback) via Ollama, tool-calling agent loop |
| **Voice** | faster-whisper STT + Piper TTS (`en_GB-alba-medium` British female) |
| **Vision** | Screenshot + Tesseract OCR, webcam capture |
| **PC Control** | Mouse, keyboard, windows, clipboard, files (home-scoped), processes |
| **Web** | Playwright browsing, page reading, form fill |
| **Memory** | Local SQLite + embeddings |
| **Security** | Docker sandbox by default + explicit typed Go-Live with TTL + audit log |
| **Safety** | Voice can never trigger Go-Live. No privilege escalation. Append-only audit. |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/jd0039970-beep/friday-assistant.git
cd friday-assistant

# 2. Install (Ollama + models + Python deps + optional Docker sandbox)
bash scripts/install.sh          # Linux / macOS
# or
powershell -File scripts/install.ps1

# 3. Start backend
cd backend
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m app.main

# 4. Talk to her
curl -X POST http://127.0.0.1:8787/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Friday, status report."}'
```

Optional: install Piper voice for speech output:
```bash
pip install piper-tts
python -m piper.download_voices en_GB-alba-medium
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) and [SAFETY.md](SAFETY.md).

## Roadmap

See [MILESTONES.md](MILESTONES.md). Current focus: full voice pipeline + Tauri desktop shell.

## License

MIT — free for any use. The security module deliberately does **not** contain
exploit code; it only orchestrates tools you install yourself inside a sandbox.
