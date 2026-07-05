@echo off
setlocal enabledelayedexpansion
title TextReader
pushd "%~dp0"

echo.
echo ^|=========================================================^|
echo ^| _____         _     ____                _               ^|
echo ^|^|_   _^|____  _^| ^|_  ^|  _ \ ___  __ _  __^| ^| ___ _ __     ^|
echo ^|  ^| ^|/ _ \ \/ / __^| ^| ^|_) / _ \/ _` ^|/ _` ^|/ _ \ '__^|    ^|
echo ^|  ^| ^|  __/^>  ^<^| ^|_  ^|  _ ^<  __/ (_^| ^| (_^| ^|  __/         ^|
echo ^|  ^|_^\___/_/\_^\__^| ^|_^| \_\___^\__,_^\__,_^\___^|_^|            ^|
echo ^|                                                         ^|
echo ^|        Screen region -^> OCR -^> Arabic voice            ^|
echo ^|=========================================================^|
echo.

echo Starting backend (Docker)...
docker compose up --build -d
if errorlevel 1 (
    echo.
    echo Failed to start the backend. Is Docker Desktop installed and running?
    pause
    exit /b 1
)

echo Waiting for backend to become healthy...
set tries=0
:wait_health
curl -sf http://localhost:8000/health >nul 2>&1
if not errorlevel 1 goto health_ok
set /a tries+=1
if !tries! GEQ 30 (
    echo.
    echo Backend did not become healthy in time. Check: docker compose logs
    pause
    exit /b 1
)
timeout /t 1 >nul
goto wait_health

:health_ok
echo Backend is up.
echo.
echo Hotkeys ^(rebindable via Ctrl+Shift+S^):
echo   Ctrl+Shift+C  select screen region
echo   Ctrl+Shift+S  open settings
echo   Esc           cancel selection
echo   Ctrl+Shift+Q  quit
echo.

cd client
python reader_client.py
cd ..

popd
pause
