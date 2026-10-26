# F.R.I.D.A.Y — Local AI Desktop Assistant

A 100%-local, zero-cost, Iron-Man-style AI assistant. Runs a small open-weight LLM
through Ollama, controls your PC, sees your screen, talks to you, and includes a
strictly sandboxed security-testing module for your own lab/CTF/owned-hardware work.

## Quick start

```bash
# 1. Install Ollama + pull the model + python deps
bash scripts/install.sh          # Linux/macOS
# or
powershell -File scripts/install.ps1   # Windows

# 2. Start the backend
cd backend
python -m app.main

# 3. (later) run the Tauri desktop shell
cd frontend && npm install && npm run tauri dev
```

See `ARCHITECTURE.md` for the system design, `SAFETY.md` for how the sandbox/live-mode
split works, and `MILESTONES.md` for the build plan.

## What's actually implemented in this starter drop

- Ollama-backed agent loop with a clean tool-calling protocol (`backend/app/core`)
- Tool registry + first real tools: filesystem, screenshot, clipboard, mouse/keyboard,
  notifications, process list (`backend/app/tools`)
- SQLite + embeddings long-term memory (`backend/app/memory`)
- Docker-isolated sandbox executor with an explicit, logged "Go Live" gate
  (`backend/app/sandbox`)
- Voice pipeline wiring for faster-whisper (STT) and Piper (TTS)
  (`backend/app/voice`)
- FastAPI app tying it together with a `/chat` and `/voice` endpoint (`backend/app/main.py`)

What's deliberately **not** included: an actual exploit/crack engine. The security
module is an *orchestrator* around tools you install yourself (nmap, hashcat, etc.) —
see `SAFETY.md` for why and how that boundary is enforced in code.
