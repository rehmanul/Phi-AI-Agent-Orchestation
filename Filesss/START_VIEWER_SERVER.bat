@echo off
REM Start FastAPI server with artifact viewer
echo Starting Agent Orchestrator API with Artifact Viewer...
echo.
echo Artifact Viewer will be available at:
echo   http://localhost:8000/
echo.
echo API Documentation:
echo   http://localhost:8000/docs
echo.
echo Opening browser in 3 seconds...
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"

REM Wait a moment, then open browser
timeout /t 3 /nobreak >nul
start http://localhost:8000/

REM Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
