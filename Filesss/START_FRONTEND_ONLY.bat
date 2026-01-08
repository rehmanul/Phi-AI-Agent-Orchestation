@echo off
title Risk Management System - Frontend Only
color 0C

echo.
echo ============================================================
echo   RISK MANAGEMENT SYSTEM - FRONTEND SERVER
echo ============================================================
echo.

cd /d "%~dp0frontend"

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [INFO] Starting Frontend Server...
echo [INFO] Frontend will run on: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
