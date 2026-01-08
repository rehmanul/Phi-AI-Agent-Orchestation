@echo off
REM Simple batch file to find frontend port by checking if port is listening
REM This is a fallback if PowerShell script doesn't work

set START_PORT=3001
set MAX_PORT=3010
set FOUND_PORT=

for /L %%p in (%START_PORT%,1,%MAX_PORT%) do (
    netstat -an | findstr ":%%p.*LISTENING" >nul 2>&1
    if errorlevel 1 (
        REM Port is not in use, continue
    ) else (
        REM Port is listening - this might be our frontend
        echo %%p
        goto :found
    )
)

:found
if "%FOUND_PORT%"=="" set FOUND_PORT=3001
echo %FOUND_PORT%
