Write-Host "Starting F.R.I.D.A.Y..."
Set-Location "$PSScriptRoot\..\backend"
if (Test-Path .venv\Scripts\Activate.ps1) {
  .\.venv\Scripts\Activate.ps1
} else {
  Write-Host "No venv. Run scripts/install.ps1 first."
  exit 1
}
$job = Start-Process python -ArgumentList "-m","app.main" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8787/hud/"
Write-Host "Backend PID $($job.Id)"
Write-Host "HUD open. Tab = talk, Esc = SHUT DOWN"
