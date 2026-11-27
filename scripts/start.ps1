$root = Split-Path -Parent $PSScriptRoot
& (Join-Path $root '.venv\Scripts\pythonw.exe') (Join-Path $root 'main.py')
