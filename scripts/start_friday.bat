@echo off
title F.R.I.D.A.Y
echo Starting F.R.I.D.A.Y...
if exist Friday.exe (
  start "" Friday.exe
) else (
  echo Friday.exe not found. Run from the PyInstaller dist folder or use scripts\start.ps1 for dev.
  pause
  exit /b 1
)
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8787/hud/
echo HUD opening. Tab=talk  Esc=SHUT DOWN
