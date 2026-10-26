# ============================================================
#  F.R.I.D.A.Y — ONE SCRIPT INSTALL (Windows)
#  Installs: Git, Python, Ollama, Docker Desktop, models, app
#  Run in PowerShell AS ADMINISTRATOR for best results:
#    Set-ExecutionPolicy Bypass -Scope Process -Force
#    irm https://raw.githubusercontent.com/jd0039970-beep/friday-assistant/main/INSTALL_EVERYTHING.ps1 | iex
#  Or after clone:
#    powershell -ExecutionPolicy Bypass -File INSTALL_EVERYTHING.ps1
# ============================================================

$ErrorActionPreference = "Continue"
$RepoUrl = "https://github.com/jd0039970-beep/friday-assistant.git"
$InstallRoot = Join-Path $env:USERPROFILE "friday-assistant"

function Assert-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p = New-Object Security.Principal.WindowsPrincipal($id)
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Cmd($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

function Ensure-Winget {
  if (Test-Cmd "winget") { return $true }
  Write-Host "[!] winget not found. Install 'App Installer' from the Microsoft Store, then re-run."
  return $false
}

function Winget-Install($id, $name) {
  if (-not (Ensure-Winget)) { return $false }
  Write-Host "[--] Installing $name ($id) via winget..."
  winget install -e --id $id --accept-package-agreements --accept-source-agreements --silent
  return $LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq -1978335189  # already installed codes vary
}

Write-Host ""
Write-Host "=============================================="
Write-Host "  F.R.I.D.A.Y — FULL MACHINE BOOTSTRAP"
Write-Host "=============================================="
Write-Host "This installs everything Friday needs on a clean PC."
Write-Host ""

if (-not (Assert-Admin)) {
  Write-Host "[!] Not running as Administrator."
  Write-Host "    Right-click PowerShell -> Run as administrator, then re-run this script."
  Write-Host "    Continuing anyway (some installs may fail)..."
}

# Refresh PATH helper after installs
function Refresh-Path {
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
              [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ---- 1. Git ----
if (-not (Test-Cmd "git")) {
  Winget-Install "Git.Git" "Git" | Out-Null
  Refresh-Path
}
if (Test-Cmd "git") { Write-Host "[OK] Git" } else { Write-Host "[FAIL] Git — install manually from https://git-scm.com" }

# ---- 2. Python ----
if (-not (Test-Cmd "python")) {
  Winget-Install "Python.Python.3.12" "Python 3.12" | Out-Null
  Refresh-Path
}
if (Test-Cmd "python") { Write-Host "[OK] Python $(python --version 2>&1)" } else { Write-Host "[FAIL] Python — https://www.python.org/downloads/ (tick Add to PATH)" }

# ---- 3. Ollama ----
if (-not (Test-Cmd "ollama")) {
  Winget-Install "Ollama.Ollama" "Ollama" | Out-Null
  Refresh-Path
  # Fallback: direct installer hint
  if (-not (Test-Cmd "ollama")) {
    Write-Host "[--] Trying Ollama silent-ish download page instruction..."
    Write-Host "    If still missing: https://ollama.com/download — install, then re-run this script."
  }
}
if (Test-Cmd "ollama") { Write-Host "[OK] Ollama" } else { Write-Host "[FAIL] Ollama" }

# ---- 4. Docker Desktop ----
if (-not (Test-Cmd "docker")) {
  Winget-Install "Docker.DockerDesktop" "Docker Desktop" | Out-Null
  Refresh-Path
}
if (Test-Cmd "docker") {
  Write-Host "[OK] Docker"
} else {
  Write-Host "[!] Docker not on PATH yet. Install/start Docker Desktop, then reboot if needed."
  Write-Host "    Friday still runs; sandbox is limited until Docker works."
}

# ---- 5. Clone or update repo ----
if (Test-Path (Join-Path $InstallRoot ".git")) {
  Write-Host "[--] Updating existing repo at $InstallRoot"
  Push-Location $InstallRoot
  git pull
  Pop-Location
} elseif (Test-Path $InstallRoot) {
  Write-Host "[OK] Source folder exists (no git) $InstallRoot"
} else {
  if (Test-Cmd "git") {
    Write-Host "[--] Cloning Friday into $InstallRoot"
    git clone $RepoUrl $InstallRoot
  } else {
    Write-Host "[FAIL] Cannot clone — Git missing. Download ZIP from GitHub and extract to $InstallRoot"
    exit 1
  }
}

if (-not (Test-Path $InstallRoot)) {
  Write-Host "[FAIL] Repo not at $InstallRoot"
  exit 1
}

# ---- 6. Python venv + packages ----
$Backend = Join-Path $InstallRoot "backend"
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
  pip install fastapi "uvicorn[standard]" httpx pyyaml numpy pillow faster-whisper pydantic python-multipart
}
Write-Host "[OK] Python packages"

# ---- 7. ~/.friday dirs ----
$FridayHome = Join-Path $env:USERPROFILE ".friday"
@( "skills", "plans", "inbox" ) | ForEach-Object {
  New-Item -ItemType Directory -Force -Path (Join-Path $FridayHome $_) | Out-Null
}
Write-Host "[OK] $FridayHome"

# ---- 8. Models ----
Refresh-Path
if (Test-Cmd "ollama") {
  Write-Host "[--] Pulling LLM models (large download, be patient)..."
  ollama pull qwen2.5:7b-instruct-q4_K_M
  ollama pull nomic-embed-text
  Write-Host "[OK] Models"
} else {
  Write-Host "[!] Skip models — install Ollama and re-run this script"
}

# ---- 9. Desktop shortcut ----
try {
  $Wsh = New-Object -ComObject WScript.Shell
  $Sc = $Wsh.CreateShortcut((Join-Path $env:USERPROFILE "Desktop\F.R.I.D.A.Y.lnk"))
  $startPs1 = Join-Path $InstallRoot "scripts\start.ps1"
  $Sc.TargetPath = "powershell.exe"
  $Sc.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$startPs1`""
  $Sc.WorkingDirectory = $InstallRoot
  $Sc.Description = "Start F.R.I.D.A.Y"
  $Sc.Save()
  Write-Host "[OK] Desktop shortcut: F.R.I.D.A.Y"
} catch {
  Write-Host "[!] Shortcut failed: $_"
}

# ---- Done ----
Write-Host ""
Write-Host "=============================================="
Write-Host "  INSTALL FINISHED"
Write-Host "=============================================="
Write-Host "Folder:  $InstallRoot"
Write-Host "Start:   Desktop shortcut  OR"
Write-Host "         powershell -ExecutionPolicy Bypass -File `$InstallRoot\scripts\start.ps1"
Write-Host "HUD:     http://127.0.0.1:8787/hud/"
Write-Host "Keys:    Tab = talk   Esc = SHUT DOWN"
Write-Host ""
Write-Host "If Docker or Ollama was just installed, reboot once, then start Friday."
Write-Host "=============================================="
