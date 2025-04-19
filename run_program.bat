@echo off
title TextReader v0.0.5
cd /d "%~dp0"

echo.
echo ^|=========================================================^|
echo ^| _____         _     ____                _               ^|
echo ^|^|_   _^|____  _^| ^|_  ^|  _ \ ___  __ _  __^| ^| ___ _ __     ^|
echo ^|  ^| ^|/ _ \ \/ / __^| ^| ^|_) / _ \/ _` ^|/ _` ^|/ _ \ '__^|    ^|
echo ^|  ^| ^|  __/^>  ^<^| ^|_  ^|  _ ^<  __/ (_^| ^| (_^| ^|  __/         ^|
echo ^|  ^|_^\___/_/\_^\__^| ^|_^| \_\___^\__,_^\__,_^\___^|_^|            ^|
echo ^|                                                         ^|
echo ^|          Screen Reader with OCR ^& TTS  v0.0.5           ^|
echo ^|=========================================================^|
echo.
echo.
echo Press Ctrl+Shift+C to select text
echo Press Ctrl+Shift+V to read
echo Press Ctrl+Shift+L to toggle language
echo.

python main.py
pause