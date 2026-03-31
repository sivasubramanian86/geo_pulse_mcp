@echo off
setlocal
cd /d "%~dp0.."

:: --- Configuration ---
set GOOGLE_CLOUD_PROJECT=genai-apac-2026-491004
set GOOGLE_CLOUD_REGION=us-central1
set TOOLBOX_URL=http://localhost:8080
set AGENT_URL=http://localhost:8081
set FRONTEND_PORT=8082
set GOOGLE_GENAI_USE_VERTEXAI=true

:: Prefer the new Python 3.12 environment
if exist "venv_312\Scripts\python.exe" (
    set VENV_PATH=venv_312\Scripts
) else (
    echo [ERROR] Virtual environment 'venv_312' not found in root.
    pause
    exit /b 1
)

echo [1/4] Cleaning up existing ports (8080, 8081, 8082)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do taskkill /F /T /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8081 ^| findstr LISTENING') do taskkill /F /T /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8082 ^| findstr LISTENING') do taskkill /F /T /PID %%a 2>nul

echo [2/4] Starting MCP Toolbox (Port 8080)...
start /B cmd /c ""%VENV_PATH%\python.exe" -m uvicorn toolbox.main:app --port 8080 --reload"
timeout /t 5 /nobreak >nul

echo [3/4] Starting Agent Proxy (Port 8081)...
start /B cmd /c ""%VENV_PATH%\python.exe" agent/app.py"
timeout /t 5 /nobreak >nul

echo [4/4] Starting Frontend (Port 8082)...
start "" http://localhost:8082
start /B cmd /c "cd frontend && "..\%VENV_PATH%\python.exe" -m http.server 8082"

echo.
echo GeoPulse-MCP is running!
echo Frontend: http://localhost:8082
echo Agent API: http://localhost:8081
echo Toolbox:  http://localhost:8080/sse
echo.
echo Press Ctrl+C in this terminal to stop (or run the cleanup section manually).
pause
