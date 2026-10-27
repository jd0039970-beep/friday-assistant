# ============================================================
#  ONE COMMAND -> Friday.exe (native window, no browser)
#  Run in PowerShell:
#    cd C:\Users\frost\friday-assistant
#    powershell -ExecutionPolicy Bypass -File scripts\BUILD_EXE.ps1
# ============================================================
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
Set-Location $Backend

if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Write-Host "Run INSTALL_EVERYTHING.ps1 first."
  exit 1
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pywebview pyinstaller

Write-Host "Building Friday.exe (this takes a few minutes)..."

pyinstaller --noconfirm --clean --windowed --name Friday `
  --add-data "../config;config" `
  --add-data "../frontend/hud;frontend/hud" `
  --hidden-import uvicorn.logging `
  --hidden-import uvicorn.loops `
  --hidden-import uvicorn.loops.auto `
  --hidden-import uvicorn.protocols `
  --hidden-import uvicorn.protocols.http `
  --hidden-import uvicorn.protocols.http.auto `
  --hidden-import uvicorn.protocols.websockets.auto `
  --hidden-import uvicorn.lifespan `
  --hidden-import uvicorn.lifespan.on `
  --collect-all webview `
  -m app.desktop

$Dist = Join-Path $Backend "dist\Friday"
Write-Host ""
Write-Host "DONE."
Write-Host "Run:  $Dist\Friday.exe"
Write-Host "That is a real .exe with a native window. Not a browser."

# Desktop shortcut to the exe
try {
  $Wsh = New-Object -ComObject WScript.Shell
  $Sc = $Wsh.CreateShortcut((Join-Path $env:USERPROFILE "Desktop\F.R.I.D.A.Y.lnk"))
  $Sc.TargetPath = Join-Path $Dist "Friday.exe"
  $Sc.WorkingDirectory = $Dist
  $Sc.Description = "F.R.I.D.A.Y"
  $Sc.Save()
  Write-Host "Desktop shortcut updated -> Friday.exe"
} catch {}
