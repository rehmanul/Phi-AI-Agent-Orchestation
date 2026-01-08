@echo off
echo ========================================
echo Investment Sales BD System Launcher
echo ========================================
echo.

echo Checking for existing processes on ports 8001 and 3001...
echo.

REM Check and kill process on port 8001 (Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001.*LISTENING"') do (
    echo Found process %%a on port 8001, attempting to kill...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Warning: Could not kill process on port 8001. You may need to close it manually.
    ) else (
        echo Successfully freed port 8001.
    )
)

REM Check and kill process on port 3001 (Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3001.*LISTENING"') do (
    echo Found process %%a on port 3001, attempting to kill...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Warning: Could not kill process on port 3001. Trying alternative port...
        echo Frontend will auto-select next available port.
    ) else (
        echo Successfully freed port 3001.
    )
)

echo.
echo Waiting 2 seconds for ports to be released...
timeout /t 2 /nobreak >nul

echo.
echo Starting Backend API on port 8001...
start "BD Backend" cmd /k "cd /d %~dp0 && python -m api.main"

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend on port 3001...
echo (If port 3001 is still in use, Next.js will automatically use the next available port)
start "BD Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo Searching for frontend server...
REM Try to find which port the frontend is actually running on
set FRONTEND_PORT=3001
set MAX_ATTEMPTS=10
set ATTEMPT=0

:find_port
set /a ATTEMPT+=1
if %ATTEMPT% GTR %MAX_ATTEMPTS% goto :open_browser

REM Check if this port is listening and has a Node process
netstat -an | findstr ":%FRONTEND_PORT%.*LISTENING" >nul 2>&1
if errorlevel 1 (
    REM Port not listening, try next
    set /a FRONTEND_PORT+=1
    goto :find_port
)

REM Port is listening, verify it's a Node process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%.*LISTENING"') do (
    tasklist /FI "PID eq %%a" 2>nul | findstr /I "node.exe" >nul 2>&1
    if not errorlevel 1 (
        echo Found frontend server on port %FRONTEND_PORT%
        goto :open_browser
    )
)

REM Not a Node process, try next port
set /a FRONTEND_PORT+=1
goto :find_port

:open_browser
echo.
echo Opening browser to http://localhost:%FRONTEND_PORT%...
start http://localhost:%FRONTEND_PORT%

echo.
echo ========================================
echo System startup initiated!
echo ========================================
echo.
echo Backend API:  http://localhost:8001
echo API Docs:     http://localhost:8001/docs
echo Frontend:     http://localhost:%FRONTEND_PORT%
echo.
echo Browser opened automatically to the detected frontend port.
echo.
echo The backend and frontend windows will stay open.
echo Close them when you're done using the system.
echo.
pause
