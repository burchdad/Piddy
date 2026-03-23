@echo off
title Piddy - AI Backend Developer Agent
echo ============================================
echo   PIDDY - AI Backend Developer Agent
echo   Self-contained Local Runtime
echo ============================================
echo.

:: Set Piddy root
set PIDDY_ROOT=%~dp0
set PIDDY_ROOT=%PIDDY_ROOT:~0,-1%

:: Use embedded runtimes
set PYTHON=%PIDDY_ROOT%\runtime\python\python.exe
set NODE=%PIDDY_ROOT%\runtime\node\node.exe
set NPM=%PIDDY_ROOT%\runtime\node\npm.cmd

:: Add Piddy root to PYTHONPATH so src/ imports work
set PYTHONPATH=%PIDDY_ROOT%;%PYTHONPATH%

:: Verify runtimes exist
if not exist "%PYTHON%" (
    echo [ERROR] Embedded Python not found at %PYTHON%
    echo Run setup first.
    pause
    exit /b 1
)
if not exist "%NODE%" (
    echo [ERROR] Embedded Node.js not found at %NODE%
    echo Run setup first.
    pause
    exit /b 1
)

echo [OK] Embedded Python: & "%PYTHON%" --version
echo [OK] Embedded Node.js: & "%NODE%" --version
echo.

:: Check .env exists
if not exist "%PIDDY_ROOT%\.env" (
    echo [WARN] No .env file found. Copy .env.example to .env and add your API key.
    pause
    exit /b 1
)

echo Starting Piddy Backend (auto port)...
cd /d "%PIDDY_ROOT%"
start "Piddy Backend" cmd /k ""%PYTHON%" "%PIDDY_ROOT%\src\dashboard_api.py" 2>&1"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /noprefix >nul

echo Starting Piddy Frontend (port 3000)...
cd /d "%PIDDY_ROOT%\frontend"
start "Piddy Frontend" cmd /k "set PATH=%PIDDY_ROOT%\runtime\node;%%PATH%% && "%NPM%" run dev"

echo.
echo ============================================
echo   Piddy is starting up!
echo   Backend:  http://localhost (auto port)
echo   Frontend: http://localhost:3000
echo ============================================
echo.
echo Press any key to exit this launcher...
pause >nul
