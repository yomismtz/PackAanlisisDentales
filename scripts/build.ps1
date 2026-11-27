$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path '.venv\Scripts\pyinstaller.exe')) { throw 'Primero ejecuta scripts\setup.ps1' }
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --name PackAnalisisDentales --collect-all PySide6 --collect-all cv2 --add-data "clients/web/public/avis-logo.svg;clients/web/public" --add-data "clients/web/public/birds;clients/web/public/birds" run.py
Write-Host 'Ejecutable generado en dist\PackAnalisisDentales\PackAnalisisDentales.exe'
