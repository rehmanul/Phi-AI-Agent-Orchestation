@echo off
title Risk Management System - Stopper
color 0E

echo.
echo ============================================================
echo   RISK MANAGEMENT SYSTEM - STOPPING SERVERS
echo ============================================================
echo.

echo [INFO] Stopping processes on ports 8002 and 3000...
echo.

REM Kill processes on port 8002 (Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    echo [INFO] Stopping backend process (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill processes on port 3000 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo [INFO] Stopping frontend process (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill Node.js processes (Next.js dev server)
taskkill /F /IM node.exe >nul 2>&1

echo.
echo [SUCCESS] All servers stopped.
echo.
pause
