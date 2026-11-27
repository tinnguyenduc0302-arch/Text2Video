$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --windowed --onedir --name VoicetoVideo --icon assets\icons\voicetovideo.ico --add-data 'assets\icons\voicetovideo.ico;assets\icons' --collect-all lipsync --collect-all face_alignment --collect-all faster_whisper main.py
