# F.R.I.D.A.Y — Local Iron-Man AI

**Holographic HUD · Tab push-to-talk · Esc silence · full lab control · self-skills**

## Hotkeys
| Key | Action |
|-----|--------|
| **Tab** (hold) | Push-to-talk |
| **Esc** | Silence / interrupt Friday |
| **Enter** | Send typed command |

## Quick start
```bash
git clone https://github.com/jd0039970-beep/friday-assistant.git
cd friday-assistant
bash scripts/install.sh
cd backend && source .venv/bin/activate
python -m app.main
# open http://127.0.0.1:8787/hud/
```

## Workshop (your encrypted drives / lab boxes)
```
enable workshop mode
add trusted target /dev/sdb
work on /dev/sdb          # she identifies, strings, binwalks, etc.
```

## Forensics packs
Ask: `list forensics packs` — then e.g. `run full lab pass on /dev/sdb`

## Desktop shell (optional)
```bash
cd frontend/tauri && npm install && npm run tauri dev
```

## Stack
Qwen2.5-7B · Piper en_GB-alba · Playwright · Docker sandbox · Tauri shell

MIT. Local only.
