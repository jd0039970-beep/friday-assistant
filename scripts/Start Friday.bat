@echo off
title F.R.I.D.A.Y
cd /d "%~dp0\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
