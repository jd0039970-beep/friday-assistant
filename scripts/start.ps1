# F.R.I.D.A.Y app launcher — double-click friendly
# Starts local backend (hidden) + opens a frameless app window (not a browser tab)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$Log = Join-Path $env:USERPROFILE ".friday\friday.log"

New-Item -ItemType Directory -Force -Path (Split-Path $Log) | Out-Null

if (-not (Test-Path $VenvPython)) {
  Write-Host "Friday not installed fully. Run INSTALL_EVERYTHING.ps1 first."
  pause
  exit 1
}

# Already running?
try {
  $r = Invoke-WebRequest -Uri "http://127.0.0.1:8787/health" -UseBasicParsing -TimeoutSec 2
  if ($r.StatusCode -eq 200) {
    Write-Host "Friday already running."
  }
} catch {
  Write-Host "Starting F.R.I.D.A.Y backend..."
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $VenvPython
  $psi.Arguments = "-m app.main"
  $psi.WorkingDirectory = $Backend
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $p = [System.Diagnostics.Process]::Start($psi)
  # Give server time to bind
  $ok = $false
  for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
      $r = Invoke-WebRequest -Uri "http://127.0.0.1:8787/health" -UseBasicParsing -TimeoutSec 1
      if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch {}
  }
  if (-not $ok) {
    Write-Host "Backend failed to start. Check $Log or run manually:"
    Write-Host "  cd $Backend"
    Write-Host "  .\.venv\Scripts\Activate.ps1"
    Write-Host "  python -m app.main"
    pause
    exit 1
  }
}

# Open as APP WINDOW (no browser tabs/chrome) — still 100% local
$Hud = "http://127.0.0.1:8787/hud/"
$launched = $false

$edge = @(
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($edge) {
  Start-Process $edge -ArgumentList "--app=$Hud", "--disable-extensions"
  $launched = $true
}

if (-not $launched) {
  $chrome = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
  ) | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($chrome) {
    Start-Process $chrome -ArgumentList "--app=$Hud"
    $launched = $true
  }
}

if (-not $launched) {
  # Fallback: default browser
  Start-Process $Hud
}

Write-Host "F.R.I.D.A.Y online (local only). Tab=talk  Esc=SHUT DOWN"
