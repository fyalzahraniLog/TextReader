@echo off
echo TextReader v0.0.5 - Dependency Installer
echo ---------------------------------------
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Note: Tesseract OCR must be installed from
echo https://github.com/UB-Mannheim/tesseract/wiki
echo.
pause