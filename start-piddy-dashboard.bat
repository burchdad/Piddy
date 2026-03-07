@echo off
REM Piddy Dashboard Full Stack Startup Script for Windows
REM Robust version with logging and error handling

setlocal enabledelayedexpansion
cd /d "%~dp0"

title Piddy Dashboard

echo.
echo ===============================================
echo 🎯 PIDDY DASHBOARD STARTUP
echo ===============================================
echo.

REM Check for Python
echo [CHECK] Looking for Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Install from: https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo [OK] %PYTHON_VER%

REM Check for Node.js
echo [CHECK] Looking for Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Install from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
echo [OK] Node %NODE_VER%

REM Check for npm
echo [CHECK] Looking for npm...
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found!
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VER=%%i
echo [OK] npm %NPM_VER%

echo.
echo ===============================================
echo [1/3] Backend Setup
echo ===============================================
echo.

REM Setup Python virtual environment
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

REM Activate venv and install requirements
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

echo [*] Installing requirements...
pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    echo Check that requirements.txt exists
    pause
    exit /b 1
)

echo [OK] Backend dependencies ready

echo.
echo ===============================================
echo [2/3] Frontend Setup
echo ===============================================
echo.

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo [*] Installing frontend dependencies...
    cd frontend
    call npm install --silent
    if errorlevel 1 (
        echo [ERROR] Failed to install npm packages
        cd ..
        pause
        exit /b 1
    )
    
    echo [*] Building frontend...
    call npm run build
    if errorlevel 1 (
        echo [ERROR] Failed to build frontend
        cd ..
        pause
        exit /b 1
    )
    cd ..
) else (
    echo [OK] Frontend dependencies cached
)

REM Check if dist folder exists
if not exist "frontend\dist" (
    echo [*] Building frontend...
    cd frontend
    call npm run build
    cd ..
)

echo [OK] Frontend ready

echo.
echo ===============================================
echo [3/3] Starting Services
echo ===============================================
echo.

echo [*] Starting Backend on port 8000...
start "Piddy Backend - API Server" cmd /c "title Piddy Backend && cd /d %CD% && call venv\Scripts\activate.bat && echo. && echo Starting Piddy Backend API... && echo. && python -m src.main && pause"
timeout /t 2

echo [*] Starting Frontend on port 3000...
start "Piddy Frontend - Dashboard" cmd /c "title Piddy Frontend && cd /d %CD%\frontend\dist && echo. && echo Starting Piddy Frontend Server... && echo Serving files from: %CD% && echo. && python -m http.server 3000 && pause"
timeout /t 2

echo.
echo ===============================================
echo SUCCESS - All Services Started!
echo ===============================================
echo.

echo Dashboard is available at:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.

echo Opening dashboard in your browser...
timeout /t 3
start http://localhost:3000

echo.
echo ✅ Piddy Dashboard is RUNNING!
echo.
echo Two console windows opened:
echo   1. Piddy Backend - Shows API logs
echo   2. Piddy Frontend - Shows web server logs
echo.
echo To stop: Close the console windows
echo.
pause

endlocal
