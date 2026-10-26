# Build milestones

## M0 — Core brain + safety (DONE)
- Ollama-backed agent loop with tool calling
- Tool registry + system/input tools
- Sandbox controller + Go-Live state machine + audit log
- SQLite memory
- FastAPI `/chat`

## M1 — Voice
- Global push-to-talk hotkey
- faster-whisper STT
- Piper TTS with British female voice (F.R.I.D.A.Y style)
- Optional wake word

## M2 — Vision
- Screenshot + OCR
- Webcam capture
- Basic visual understanding

## M3 — Desktop shell
- Tauri app + Iron-Man HUD
- System tray + live-mode overlay
- Settings panel

## M4 — Browsing & chaining
- Playwright web tools
- Multi-step agentic chains

## M5 — Security hardening
- Full nmap/hashcat/binwalk wrappers
- Audit log viewer in UI

## M6 — Polish
- Persona tuning
- Self-tool creation (sandboxed)
- One-click installer
