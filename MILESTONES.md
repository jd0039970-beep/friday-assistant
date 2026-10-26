# Build milestones

## M0 — Core brain + safety ✅
- Ollama-backed agent loop with tool calling
- Tool registry + system / input tools
- Sandbox controller + Go-Live state machine + audit log
- SQLite + embeddings memory
- FastAPI `/chat`

## M1 — Voice (in progress)
- [x] faster-whisper STT wrapper
- [x] Piper TTS wrapper (`en_GB-alba-medium` British female)
- [x] Voice pipeline (record → STT → TTS → play)
- [ ] Global push-to-talk hotkey (desktop shell)
- [ ] Optional openWakeWord "Hey Friday"

## M2 — Vision ✅ (basic)
- [x] Screenshot + Tesseract OCR (`what_is_on_screen`)
- [x] Webcam capture
- [ ] Proactive screen diffing (opt-in)

## M3 — Web & agentic tools ✅ (basic)
- [x] Playwright browse_url + search_web
- [ ] Form fill / click helpers
- [ ] Multi-step chain examples

## M4 — Desktop shell (next)
- Tauri app + Iron-Man HUD (from the HTML mock)
- System tray + global hotkeys
- Always-on-top live-mode red ring
- Settings panel

## M5 — Security hardening
- More allow-listed tools (hashcat, binwalk, john)
- Audit log viewer in UI
- Ownership attestation flow polish

## M6 — Polish
- Persona few-shot tuning
- Self-tool creation (sandboxed draft → user approve)
- One-click installer / packaging
- Optional Kokoro-82M higher-quality TTS path
