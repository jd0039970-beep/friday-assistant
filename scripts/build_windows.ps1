# Build a one-folder Windows distribution + simple updater stub
# Prerequisites: Python 3.11+, pip, and (optional) Inno Setup for a real Setup.exe

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location "$Root\backend"

Write-Host "== F.R.I.D.A.Y Windows build =="

if (-not (Test-Path .venv)) {
  python -m venv .venv
}
.\ .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

Write-Host "-- PyInstaller bundle"
pyinstaller --noconfirm --clean `
  --name Friday `
  --add-data "../config;config" `
  --add-data "../frontend/hud;frontend/hud" `
  --hidden-import uvicorn.logging `
  --hidden-import uvicorn.loops `
  --hidden-import uvicorn.loops.auto `
  --hidden-import uvicorn.protocols `
  --hidden-import uvicorn.protocols.http `
  --hidden-import uvicorn.protocols.http.auto `
  --hidden-import uvicorn.protocols.websockets.auto `
  --collect-all faster_whisper `
  -m app.main

Write-Host "-- Copy updater + start helper"
$Dist = "$Root\backend\dist\Friday"
Copy-Item "$Root\scripts\update_friday.ps1" "$Dist\update_friday.ps1" -Force
Copy-Item "$Root\scripts\start_friday.bat" "$Dist\start_friday.bat" -Force

Write-Host ""
Write-Host "Build output: $Dist"
Write-Host "Run start_friday.bat inside that folder."
Write-Host "For a real Setup.exe, point Inno Setup at $Dist (see scripts/friday_setup.iss)."
