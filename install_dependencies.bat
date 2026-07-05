@echo off
title TextReader - Install Dependencies
pushd "%~dp0"

echo TextReader - Dependency Installer
echo ---------------------------------
echo.
echo Installing client dependencies (host Python)...
python -m pip install --upgrade pip
pip install -r client\requirements.txt

echo.
echo The backend (OCR/translate/TTS) runs in Docker and installs its own
echo dependencies on first build. Make sure Docker Desktop is installed and
echo running before using run_program.bat:
echo https://www.docker.com/products/docker-desktop/
echo.
popd
pause
