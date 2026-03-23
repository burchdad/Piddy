@echo off
REM Piddy Slack Quick Start - Windows

echo.
echo 🚀 Piddy Slack Integration Setup
echo =================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)

echo ✅ Python found: 
python --version
echo.

REM Check virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo ✅ Virtual environment ready
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✅ Virtual environment activated
echo.

REM Check dependencies
pip list | find "fastapi" >nul
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt -q
)

echo ✅ Dependencies installed
echo.

REM Check .env file
if not exist ".env" (
    echo ⚠️ .env file not found!
    echo.
    echo Please create .env with:
    echo.
    echo # Required for Slack
    echo SLACK_BOT_TOKEN=xoxb-your-token
    echo SLACK_APP_TOKEN=xapp-1-your-token
    echo SLACK_SIGNING_SECRET=your-secret
    echo.
    echo # Required for Claude
    echo ANTHROPIC_API_KEY=sk-ant-your-key
    echo.
    echo Then run this script again.
    exit /b 1
)

echo ✅ Configuration loaded
echo.

REM Check SLACK_BOT_TOKEN
findstr /r "^SLACK_BOT_TOKEN=" .env >nul
if errorlevel 1 (
    echo ❌ Missing SLACK_BOT_TOKEN in .env
    exit /b 1
)
echo ✅ SLACK_BOT_TOKEN configured

REM Check SLACK_APP_TOKEN
findstr /r "^SLACK_APP_TOKEN=" .env >nul
if errorlevel 1 (
    echo ❌ Missing SLACK_APP_TOKEN in .env
    exit /b 1
)
echo ✅ SLACK_APP_TOKEN configured

REM Check ANTHROPIC_API_KEY
findstr /r "^ANTHROPIC_API_KEY=" .env >nul
if errorlevel 1 (
    echo ❌ Missing ANTHROPIC_API_KEY in .env
    exit /b 1
)
echo ✅ ANTHROPIC_API_KEY configured

echo.
echo 🎉 All checks passed!
echo.
echo Starting Piddy with Slack integration...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Start Piddy
python -m src.main
