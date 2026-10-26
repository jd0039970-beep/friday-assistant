# Restore ~/.friday from a backup zip (after wipe + fresh install)
param(
  [string]$ZipPath = ""
)

$ErrorActionPreference = "Stop"
$HomeDir = Join-Path $env:USERPROFILE ".friday"

if (-not $ZipPath) {
  $candidate = Get-ChildItem (Join-Path $env:USERPROFILE "Desktop") -Filter "friday-backup-*.zip" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($candidate) { $ZipPath = $candidate.FullName }
}

if (-not $ZipPath -or -not (Test-Path $ZipPath)) {
  Write-Host "Usage: .\restore_friday.ps1 -ZipPath C:\path\to\friday-backup-XXXX.zip"
  Write-Host "Or put the zip on Desktop named friday-backup-*.zip"
  exit 1
}

New-Item -ItemType Directory -Force -Path $HomeDir | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $HomeDir -Force
Write-Host "Restored into $HomeDir from $ZipPath"
Write-Host "Workshop mode, trusted targets, skills, plans, memory should be back."
