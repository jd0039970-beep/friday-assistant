$Root = Split-Path -Parent $PSScriptRoot
Set-Location "$Root\backend"
if (-not (Test-Path .venv\Scripts\Activate.ps1)) {
  Write-Host "Run scripts\install.ps1 first."
  exit 1
}
& .\.venv\Scripts\Activate.ps1
Write-Host "Starting F.R.I.D.A.Y..."
Start-Process python -ArgumentList "-m","app.main" -WindowStyle Normal
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8787/hud/"
Write-Host "HUD opening. Tab=talk  Esc=SHUT DOWN"
