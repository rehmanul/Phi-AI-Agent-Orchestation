@echo off
title Risk Management System - Backend Only
color 0B

echo.
echo ============================================================
echo   RISK MANAGEMENT SYSTEM - BACKEND SERVER
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Starting Backend Server...
echo [INFO] Backend will run on: http://localhost:8002
echo [INFO] API Docs will be at: http://localhost:8002/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m api.main

pause
