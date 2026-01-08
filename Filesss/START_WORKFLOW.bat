@echo off
echo ============================================================
echo Agentic Coding Development Workflow Launcher
echo ============================================================
echo.

cd /d "%~dp0"

echo [INFO] Running workflow...
python run_workflow.py

echo.
echo [INFO] Generating HTML viewer...
python generate_html_viewer.py

echo.
echo [INFO] Starting web server and opening browser...
echo [INFO] Server will try multiple ports until it finds an available one...
python start_server.py

echo.
echo [DONE] Server stopped.
pause
