# F.R.I.D.A.Y Desktop Shell (Tauri)

## Hotkeys
- **Tab** — push-to-talk (hold to speak, release to send)
- **Esc** — interrupt / silence Friday immediately

## Dev
```bash
# prerequisites: Rust, Node, system deps for Tauri
cd frontend/tauri
npm install
npm run tauri dev
```

The webview loads the holographic HUD from the backend (`http://127.0.0.1:8787/hud/`).
Global hotkeys are registered in the Rust side.
