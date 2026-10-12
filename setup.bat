@echo off
echo.
echo ═══════════════════════════════════════════════════════
echo          AUDITOR AI — Quick Setup Script
echo ═══════════════════════════════════════════════════════
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Download from: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found.

REM Check if .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Creating .env from .env.example...
        copy .env.example .env
        echo [WARNING] Please edit .env with your actual API keys before running!
    ) else (
        echo [WARNING] No .env file found. Create one from .env.example.
    )
) else (
    echo [OK] .env file found.
)

REM Install Backend Dependencies
echo.
echo [STEP 1/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Backend dependency installation failed!
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed.
cd ..

REM Install Frontend Dependencies
echo.
echo [STEP 2/4] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo [ERROR] Frontend dependency installation failed!
    pause
    exit /b 1
)
echo [OK] Frontend dependencies installed.
cd ..

echo.
echo ═══════════════════════════════════════════════════════
echo          SETUP COMPLETE!
echo ═══════════════════════════════════════════════════════
echo.
echo To start the application:
echo.
echo   1. Open Terminal 1 (Backend):
echo      cd backend
echo      uvicorn main:app --reload --port 8000
echo.
echo   2. Open Terminal 2 (Frontend):
echo      cd frontend
echo      npm run dev
echo.
echo   3. Open http://localhost:5173 in your browser
echo.
pause
