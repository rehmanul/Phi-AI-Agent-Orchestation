@echo off
REM Find the first port that has a Next.js/Node server listening
REM Checks ports 3001-3010 for listening servers

set START_PORT=3001
set MAX_PORT=3010
set FOUND_PORT=

for /L %%p in (%START_PORT%,1,%MAX_PORT%) do (
    netstat -an | findstr ":%%p.*LISTENING" >nul 2>&1
    if not errorlevel 1 (
        REM Check if it's a Node/Next.js process by checking process name
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p.*LISTENING"') do (
            tasklist /FI "PID eq %%a" 2>nul | findstr /I "node.exe" >nul 2>&1
            if not errorlevel 1 (
                set FOUND_PORT=%%p
                echo %%p
                goto :end
            )
        )
    )
)

REM If no port found, return default
if "%FOUND_PORT%"=="" (
    echo %START_PORT%
) else (
    echo %FOUND_PORT%
)

:end
