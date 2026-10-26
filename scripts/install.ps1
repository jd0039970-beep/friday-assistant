Write-Host "=============================================="
Write-Host "  F.R.I.D.A.Y local install (Windows)"
Write-Host "=============================================="

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "-- Installing Ollama via winget"
    winget install Ollama.Ollama
} else {
    Write-Host "-- Ollama already installed"
}

Write-Host "-- Pulling models"
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull nomic-embed-text

Write-Host "-- Setting up Python venv"
Set-Location "$PSScriptRoot\..\backend"
python -m venv .venv
.\ .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "-- Playwright Chromium"
playwright install chromium

Write-Host ""
Write-Host "Done."
Write-Host "Next:"
Write-Host "  .\backend\.venv\Scripts\Activate.ps1"
Write-Host "  cd backend; python -m app.main"
Write-Host "Optional Piper voice:"
Write-Host "  pip install piper-tts"
Write-Host "  python -m piper.download_voices en_GB-alba-medium"
