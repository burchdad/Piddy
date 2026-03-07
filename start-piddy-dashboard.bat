@echo off
REM Piddy Dashboard Full Stack Startup Script for Windows
REM This batch script starts all necessary services for the Piddy Dashboard

setlocal enabledelayedexpansion

title Piddy Dashboard - Startup

echo.
echo ===============================================
echo.
echo 🎯 PIDDY DASHBOARD STARTUP
echo.
echo ===============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python is installed

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js is installed

REM Check for npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] npm is installed

echo.
echo ===============================================
echo [1/3] Starting Piddy Backend (Port 8000)
echo ===============================================
echo.

REM Check if virtual env exists
if not exist "venv\" (
    echo [*] Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [*] Installing Python dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo [*] Starting backend server on port 8000...
start "Piddy Backend" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python -m src.main"
timeout /t 3 /nobreak

echo.
echo ===============================================
echo [2/3] Starting Piddy Frontend (Port 3000)
echo ===============================================
echo.

REM Check if frontend node_modules exist
if not exist "frontend\node_modules\" (
    echo [*] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo [*] Building frontend...
    cd frontend
    call npm run build
    cd ..
)

echo [*] Starting frontend server on port 3000...
start "Piddy Frontend" cmd /k "cd /d %CD%\frontend\dist && python -m http.server 3000"
timeout /t 2 /nobreak

echo.
echo ===============================================
echo [3/3] Opening Dashboard
echo ===============================================
echo.

REM Wait a moment for services to start
timeout /t 2 /nobreak

echo [OK] All services started!
echo.
echo Dashboard URLs:
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.

echo [*] Opening dashboard in browser...
start http://localhost:3000

echo.
echo ===============================================
echo 🎯 PIDDY DASHBOARD IS RUNNING
echo ===============================================
echo.
echo [*] Backend console window shows API server logs
echo [*] Frontend console window shows static file server logs
echo.
echo [IMPORTANT] Keep this window open! Services run in the other windows.
echo [IMPORTANT] Close other windows to stop services.
echo.
echo Press any key to close this window...
pause

endlocal
