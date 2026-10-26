# One thing to run — everything installs

## Clean PC / first time (Windows)

1. Open **PowerShell as Administrator**
2. Paste:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/jd0039970-beep/friday-assistant/main/INSTALL_EVERYTHING.ps1 | iex
```

That single command installs (as available via winget):

- Git  
- Python 3.12  
- Ollama  
- Docker Desktop  
- Friday source code  
- Python packages  
- Qwen + embed models  
- Desktop shortcut  

3. If Docker/Ollama were newly installed → **reboot once**  
4. Double-click **F.R.I.D.A.Y** on the Desktop  
5. Open HUD if it doesn’t auto-open: http://127.0.0.1:8787/hud/

## Already cloned the repo?

```powershell
cd friday-assistant
powershell -ExecutionPolicy Bypass -File INSTALL_EVERYTHING.ps1
```

## After that

- **Tab** = talk  
- **Esc** = full shutdown  
- Personal data stays in `%USERPROFILE%\.friday`  
- Optional backup: `scripts\backup_friday.ps1`

## If winget cannot install something

Install manually, then re-run the same script (it skips what’s already there):

| Piece | Link |
|-------|------|
| Python | https://www.python.org/downloads/ (tick Add to PATH) |
| Git | https://git-scm.com |
| Ollama | https://ollama.com/download |
| Docker | https://www.docker.com/products/docker-desktop/ |
