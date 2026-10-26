# F.R.I.D.A.Y self-healing Windows install
# Run AFTER cloning/extracting the repo. Gets Python deps, Ollama, models, folders.
# Your personal state lives in %USERPROFILE%\.friday — use backup/restore around a wipe.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "========================================"
Write-Host " F.R.I.D.A.Y self-healing install"
Write-Host "========================================"

function Test-Cmd($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

# --- Python ---
if (-not (Test-Cmd "python")) {
  Write-Host "[!] Python not found. Install from https://www.python.org/downloads/ (tick Add to PATH), then re-run."
  exit 1
}
Write-Host "[OK] Python: $(python --version 2>&1)"

# --- venv + deps ---
$Backend = Join-Path $Root "backend"
Set-Location $Backend
if (-not (Test-Path ".venv")) {
  Write-Host "[--] Creating venv..."
  python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
  pip install -r requirements.txt
} else {
  pip install fastapi uvicorn[standard] httpx pyyaml numpy pillow faster-whisper openai-whisper pydantic python-multipart
}
Write-Host "[OK] Python packages"

# --- ~/.friday ---
$FridayHome = Join-Path $env:USERPROFILE ".friday"
New-Item -ItemType Directory -Force -Path $FridayHome | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $FridayHome "skills") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $FridayHome "plans") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $FridayHome "inbox") | Out-Null
Write-Host "[OK] $FridayHome"

# --- Ollama ---
if (-not (Test-Cmd "ollama")) {
  Write-Host "[!] Ollama not in PATH."
  Write-Host "    Download: https://ollama.com/download"
  Write-Host "    Install it, restart this terminal, then re-run this script to pull models."
} else {
  Write-Host "[OK] Ollama found"
  Write-Host "[--] Pulling models (this can take a while)..."
  ollama pull qwen2.5:7b-instruct-q4_K_M
  ollama pull nomic-embed-text
  Write-Host "[OK] Models"
}

# --- Docker (optional but recommended) ---
if (Test-Cmd "docker") {
  Write-Host "[OK] Docker found"
} else {
  Write-Host "[!] Docker not found — sandbox will be limited. Install Docker Desktop if you want full sandbox."
}

# --- Desktop shortcut ---
try {
  $Wsh = New-Object -ComObject WScript.Shell
  $Sc = $Wsh.CreateShortcut((Join-Path $env:USERPROFILE "Desktop\F.R.I.D.A.Y.lnk"))
  $Sc.TargetPath = "powershell.exe"
  $Sc.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$Root\scripts\start.ps1`""
  $Sc.WorkingDirectory = $Root
  $Sc.Description = "Start F.R.I.D.A.Y"
  $Sc.Save()
  Write-Host "[OK] Desktop shortcut"
} catch {
  Write-Host "[!] Could not create desktop shortcut: $_"
}

Write-Host ""
Write-Host "Install complete."
Write-Host "  Start:  powershell -File scripts\start.ps1"
Write-Host "  Or double-click Desktop\F.R.I.D.A.Y"
Write-Host "  HUD:    http://127.0.0.1:8787/hud/"
Write-Host ""
Write-Host "BEFORE a PC wipe, run:  powershell -File scripts\backup_friday.ps1"
Write-Host "AFTER reinstall, run:   powershell -File scripts\restore_friday.ps1"
