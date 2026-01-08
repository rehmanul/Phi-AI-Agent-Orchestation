@echo off
echo ============================================================
echo Agentic Coding Workflow - HTML Viewer Launcher
echo ============================================================
echo.

cd /d "%~dp0"

echo [INFO] Checking for existing HTML viewer...
if not exist "output\latest_viewer.html" (
    echo [INFO] HTML viewer not found. Generating...
    python generate_html_viewer.py
)

echo.
echo [INFO] Starting web server...
echo [INFO] Server will try ports 8000, 8001, 8002... until it finds an available one
echo [INFO] Press Ctrl+C to stop the server
echo.

python start_server.py

pause
