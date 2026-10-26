# Simple full updater: pulls latest release zip from GitHub and replaces files.
# Configure your repo; uses the public API (no token needed for public releases).

param(
  [string]$Owner = "jd0039970-beep",
  [string]$Repo = "friday-assistant",
  [string]$InstallDir = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
Write-Host "Checking GitHub releases for $Owner/$Repo ..."

try {
  $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases/latest" -Headers @{ "User-Agent" = "Friday-Updater" }
} catch {
  Write-Host "No releases yet or network error: $_"
  Write-Host "Falling back to git pull if this is a source checkout."
  if (Test-Path (Join-Path $InstallDir ".git")) {
    Set-Location $InstallDir
    git pull
    Write-Host "Source updated via git."
  }
  exit 0
}

$asset = $rel.assets | Where-Object { $_.name -match "windows|Friday|zip" } | Select-Object -First 1
if (-not $asset) {
  Write-Host "Latest release has no Windows asset. Tag: $($rel.tag_name)"
  Write-Host "Publish a zip named Friday-windows.zip on the release to enable auto-update."
  exit 0
}

$zip = Join-Path $env:TEMP $asset.name
Write-Host "Downloading $($asset.name) ..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zip

$staging = Join-Path $env:TEMP "friday-update-staging"
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $staging -Force

Write-Host "Stopping running Friday if any..."
Get-Process -Name "Friday" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "Applying update to $InstallDir"
Copy-Item -Path (Join-Path $staging "*") -Destination $InstallDir -Recurse -Force
Write-Host "Update complete: $($rel.tag_name)"
Write-Host "Start Friday again with start_friday.bat"
