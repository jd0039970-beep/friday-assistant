# Backup personal Friday state (workshop, skills, plans, memory, audit)
# Copy the zip off the PC before a wipe.

$ErrorActionPreference = "Stop"
$HomeDir = Join-Path $env:USERPROFILE ".friday"
$OutDir = Join-Path $env:USERPROFILE "Desktop"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Zip = Join-Path $OutDir "friday-backup-$Stamp.zip"

if (-not (Test-Path $HomeDir)) {
  Write-Host "Nothing to backup — $HomeDir does not exist yet."
  exit 0
}

Compress-Archive -Path "$HomeDir\*" -DestinationPath $Zip -Force
Write-Host "Backup written: $Zip"
Write-Host "Copy this zip to a USB / cloud BEFORE wiping the PC."
