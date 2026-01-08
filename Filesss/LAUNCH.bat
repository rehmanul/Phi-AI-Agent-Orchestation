@echo off
title Risk Management System - Quick Launch
color 0A
mode con: cols=70 lines=25

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║     RISK MANAGEMENT SYSTEM - QUICK LAUNCH                 ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Progress indicators
set "step=1"
set "total=5"

echo [%step%/%total%] Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python not found!
    echo    Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo    ✓ Python found

node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Node.js not found!
    echo    Please install Node.js 18+ from nodejs.org
    pause
    exit /b 1
)
echo    ✓ Node.js found

set /a step+=1
echo [%step%/%total%] Checking backend dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo    Installing Python packages...
    pip install -r requirements.txt --quiet
)
echo    ✓ Backend ready

set /a step+=1
echo [%step%/%total%] Starting backend server...
start "Risk Management Backend" cmd /k "cd /d %~dp0 && title Backend Server ^(Port 8002^) && color 0B && echo. && echo ╔════════════════════════════════════════════╗ && echo ║   RISK MANAGEMENT - BACKEND SERVER          ║ && echo ╚════════════════════════════════════════════╝ && echo. && echo Running on: http://localhost:8002 && echo API Docs:  http://localhost:8002/docs && echo. && python -m api.main"
echo    ✓ Backend starting...
timeout /t 3 /nobreak >nul

set /a step+=1
echo [%step%/%total%] Starting frontend server...
cd frontend
if not exist "node_modules" (
    echo    Installing frontend packages (first time only)...
    call npm install --silent
)
start "Risk Management Frontend" cmd /k "cd /d %~dp0frontend && title Frontend Server ^(Port 3000^) && color 0C && echo. && echo ╔════════════════════════════════════════════╗ && echo ║   RISK MANAGEMENT - FRONTEND SERVER         ║ && echo ╚════════════════════════════════════════════╝ && echo. && echo Running on: http://localhost:3000 && echo. && npm run dev"
echo    ✓ Frontend starting...
timeout /t 5 /nobreak >nul

set /a step+=1
echo [%step%/%total%] Opening browser...
start http://localhost:3000
echo    ✓ Browser opening...

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                    ✅ SYSTEM STARTED!                      ║
echo ╠═══════════════════════════════════════════════════════════╣
echo ║  Backend:  http://localhost:8002                          ║
echo ║  Frontend: http://localhost:3000                          ║
echo ║  API Docs: http://localhost:8002/docs                     ║
echo ╠═══════════════════════════════════════════════════════════╣
echo ║  Two windows opened:                                      ║
echo ║    • Backend server  (green window)                       ║
echo ║    • Frontend server (red window)                         ║
echo ║                                                            ║
echo ║  Browser should open automatically.                       ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Press any key to close this window...
echo (Servers will keep running in their own windows)
pause >nul
