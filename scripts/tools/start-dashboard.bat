@echo off
REM Piddy Dashboard Full Stack Startup Script for Windows
REM This batch script starts all necessary services for the Piddy Dashboard

setlocal enabledelayedexpansion

title Piddy Dashboard Startup

echo.
echo ===============================================
echo [*] Piddy Dashboard Startup Script
echo ===============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python is installed

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
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
echo [1] Starting Piddy Core...
echo ===============================================
echo.

start "Piddy Core" /MIN python src/main.py
if errorlevel 1 (
    echo [ERROR] Failed to start Piddy Core
    pause
    exit /b 1
)

echo [*] Piddy Core is starting...
timeout /t 3 /nobreak

echo.
echo ===============================================
echo [2] Starting Dashboard API...
echo ===============================================
echo.

start "Dashboard API" /MIN python src/dashboard_api.py
if errorlevel 1 (
    echo [ERROR] Failed to start Dashboard API
    pause
    exit /b 1
)

echo [*] Dashboard API is starting...
timeout /t 2 /nobreak

echo.
echo ===============================================
echo [3] Starting Dashboard Frontend...
echo ===============================================
echo.

REM Check if frontend node_modules exist
if not exist "frontend\node_modules" (
    echo [*] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

start "Dashboard Frontend" /MIN cmd /c "cd frontend && npm run dev"
if errorlevel 1 (
    echo [ERROR] Failed to start Dashboard Frontend
    pause
    exit /b 1
)

echo [*] Frontend is starting...
timeout /t 3 /nobreak

echo.
echo ===============================================
echo [SUCCESS] All Services Started!
echo ===============================================
echo.

echo [*] Service URLs:
echo     Frontend:      http://localhost:3000
echo     Dashboard API: http://localhost:8000
echo     Piddy Core:    http://localhost:8000
echo.

echo [*] Services are running in background windows
echo [*] To view logs, check the respective window consoles
echo [*] To stop services, close the respective windows or use Task Manager
echo.

echo [*] Opening Dashboard in browser...
timeout /t 2 /nobreak

start http://localhost:3000

echo.
echo [*] Dashboard startup complete!
echo [*] You can minimize this window - all services will continue running
echo [*] Press any key to return to command prompt...
echo.

pause

endlocal
