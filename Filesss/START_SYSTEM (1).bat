@echo off
title Risk Management System - Launcher
color 0A

echo.
echo ============================================================
echo   RISK MANAGEMENT SYSTEM - STARTING
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo [1/4] Checking Python dependencies...
cd /d "%~dp0"
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FastAPI not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [2/4] Starting Backend Server...
start "Risk Management Backend" cmd /k "cd /d %~dp0 && echo Starting Backend on port 8002... && python -m api.main"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Frontend Server...
cd frontend
if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies...
    call npm install
)
start "Risk Management Frontend" cmd /k "cd /d %~dp0frontend && echo Starting Frontend on port 3000... && npm run dev"
timeout /t 5 /nobreak >nul

echo [4/4] Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo ============================================================
echo   SYSTEM STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8002/docs
echo.
echo Two windows have opened:
echo   - Backend server (port 8002)
echo   - Frontend server (port 3000)
echo.
echo Browser should open automatically.
echo.
echo Press any key to close this window (servers will keep running)...
pause >nul
