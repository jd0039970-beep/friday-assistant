# F.R.I.D.A.Y — Local Iron-Man AI (v0.7)

Holographic HUD · Tab talk · Esc shutdown · boot checks · long-task planner · Windows installer

## One-click Windows build

```powershell
# On a Windows machine with Python 3.11+
.git\clone or download source
cd friday-assistant
powershell -File scripts\build_windows.ps1
# Output: backend\dist\Friday\
# Optional: compile scripts\friday_setup.iss with Inno Setup → Setup-Friday.exe
```

Updater: `update_friday.ps1` in the dist folder (GitHub Releases or git pull).

## Dev start
```bash
bash scripts/install.sh
bash scripts/start.sh
# HUD: http://127.0.0.1:8787/hud/
```

## Boot check
Runs automatically on startup. Also:
```
GET /bootcheck
GET /bootcheck?refresh=true
```

## Long tasks
```
create a plan to image the lab drive, extract strings, and binwalk it
```
Friday uses `create_plan` / `mark_step` / `plan_status` and persists under `~/.friday/plans/`.

## Hotkeys
| Key | Action |
|-----|--------|
| Tab (hold) | Push-to-talk → STT → agent |
| Esc | Full shutdown |
| Enter | Send text |

MIT. Local only.
