# Build TextReaderDemo.exe (plan.md Phase 5) from a native Windows Python.
# Usage:  powershell -ExecutionPolicy Bypass -File tools\build_demo.ps1
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

# 1. Portable Tesseract must be staged (never a system install — see
#    third_party/tesseract/README.md).
$tess = Join-Path $repo "third_party\tesseract"
if (-not (Test-Path (Join-Path $tess "tesseract.exe"))) {
    Write-Error "Missing $tess\tesseract.exe - see third_party\tesseract\README.md"
}
if (-not (Test-Path (Join-Path $tess "tessdata\eng.traineddata"))) {
    Write-Error "Missing $tess\tessdata\eng.traineddata - see third_party\tesseract\README.md"
}

# 2. Build deps: the pipeline's runtime deps + the client's + PyInstaller.
python -m pip install --quiet -r (Join-Path $repo "server\requirements.txt")
python -m pip install --quiet -r (Join-Path $repo "client\requirements.txt")
python -m pip install --quiet pyinstaller

# 3. One-file build.
Push-Location $repo
try {
    python -m PyInstaller demo.spec --noconfirm
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Built: $repo\dist\TextReaderDemo.exe"
Write-Host "Verify with: dist\TextReaderDemo.exe --selftest   (needs internet)"
Write-Host "Ship it as a zip together with README.demo.ar.md (the one-page Arabic README)."
