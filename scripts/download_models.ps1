$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$modelDir = Join-Path $root 'models\wav2lip'
New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Chạy scripts/setup.ps1 trước.' }
$models = @(
    @{ Name='wav2lip.pth'; Id='15MzTPHCbD4FGDh1bzKqgdgq2GZqgsNvD'; Sha='7AB9249147FD8D7884983567883222B7A86B6F94282354887825DFEE7D608999' },
    @{ Name='wav2lip_gan.pth'; Id='15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk'; Sha='180CFD49D31D47F195D5BFC62830FFE2C40724B7BBBCE6FAADC73AC6AB1A3B8E' }
)
foreach ($item in $models) {
    $path = Join-Path $modelDir $item.Name
    if ((Test-Path $path) -and (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $item.Sha) { continue }
    & $python -m gdown $item.Id -O $path
    if ($LASTEXITCODE -ne 0 -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $item.Sha) { throw "Model $($item.Name) tải lỗi hoặc sai SHA-256." }
}
$facePath = Join-Path $modelDir 's3fd.pth'
$faceSha = '619A31681264D3F7F7FC7A16A42CBBE8B23F31A256F75A366E5A1BCD59B33543'
if (-not ((Test-Path $facePath) -and (Get-FileHash -LiteralPath $facePath -Algorithm SHA256).Hash -eq $faceSha)) {
    Invoke-WebRequest -Uri 'https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth' -OutFile $facePath
    if ((Get-FileHash -LiteralPath $facePath -Algorithm SHA256).Hash -ne $faceSha) { throw 'Model S3FD sai SHA-256.' }
}
& $python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"
if ($LASTEXITCODE -ne 0) { throw 'Không tải được faster-whisper small.' }
Write-Host 'Đã chuẩn bị model local. Không đưa các checkpoint này vào Git hoặc bộ cài.'
