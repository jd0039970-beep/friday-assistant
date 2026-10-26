# Wipe-proof F.R.I.D.A.Y

Friday itself is the **repo + install script**.  
Your brain/settings (workshop, trusted targets, skills, plans, memory, audit) live in:

```
Windows:  %USERPROFILE%\.friday\
Linux:    ~/.friday/
```

## Before you wipe the PC

```powershell
powershell -File scripts\backup_friday.ps1
```

That puts `friday-backup-YYYYMMDD-HHMMSS.zip` on your Desktop.  
**Copy the zip to USB or cloud.**

Also optional: keep a copy of the whole `friday-assistant` folder or rely on GitHub.

## After wipe — full restore

1. Install **Python**, **Git**, **Ollama** (and Docker if you want sandbox).
2. Get Friday again:

```powershell
git clone https://github.com/jd0039970-beep/friday-assistant.git
cd friday-assistant
powershell -File scripts\install.ps1
```

`install.ps1` reinstalls deps and pulls the LLM models again.

3. Put your backup zip on the Desktop (or pass path), then:

```powershell
powershell -File scripts\restore_friday.ps1
```

4. Start:

```powershell
powershell -File scripts\start.ps1
```

Everything personal is back; models are re-downloaded by install.

## What is / is not in the backup

| In backup (`~/.friday`) | Re-downloaded by install |
|-------------------------|--------------------------|
| Workshop mode + trusted targets | Ollama + Qwen model |
| Custom skills | Python packages |
| Long-task plans | Repo code (git clone) |
| Memory DB | |
| Audit log | |

## One-click .exe later

After `build_windows.ps1`, keep `update_friday.ps1` next to the app.  
Still run `backup_friday` before a wipe so personal state is not lost.
