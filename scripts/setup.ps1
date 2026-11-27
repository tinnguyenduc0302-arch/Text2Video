$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Test-Path .venv\Scripts\python.exe)) { python -m venv .venv }
$python = Join-Path $root '.venv\Scripts\python.exe'
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt
& $python -m pip install --no-deps lipsync==0.1.0
& $python -c 'import PySide6, torch, av, lipsync; print("Đã import GUI và engine AI")'
Write-Warning 'lipsync 0.1.0 yêu cầu PyAV <15, nhưng bản đó không có wheel Python 3.12 trên máy này. Bản PyAV mới đã import được nhưng engine cần checkpoint để thử thực tế.'
Write-Host 'Cài thư viện xong. Cần FFmpeg và FFprobe trên PATH, hai checkpoint trong models\wav2lip.'
