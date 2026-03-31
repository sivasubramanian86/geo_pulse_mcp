#!/bin/bash

# Configuration
export GOOGLE_CLOUD_PROJECT="genai-apac-2026-491004"
export GOOGLE_CLOUD_REGION="us-central1"
export TOOLBOX_URL="http://localhost:8080"
export AGENT_URL="http://localhost:8081"
export FRONTEND_PORT="8082"
export GOOGLE_GENAI_USE_VERTEXAI="true"

# Navigate to root
cd "$(dirname "$0")/.."

# Check for venv
if [ -f "venv_312/bin/python" ]; then
    PYTHON_BIN="venv_312/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_BIN="venv/bin/python"
else
    echo "[ERROR] Virtual environment not found."
    exit 1
fi

echo "[1/4] Killing existing processes on 8080, 8081, 8082..."
lsof -ti:8080,8081,8082 | xargs kill -9 2>/dev/null

echo "[2/4] Starting MCP Toolbox (Port 8080)..."
$PYTHON_BIN -m uvicorn toolbox.main:app --port 8080 &
sleep 5

echo "[3/4] Starting Agent Proxy (Port 8081)..."
$PYTHON_BIN agent/app.py &
sleep 5

echo "[4/4] Starting Frontend (Port 8082)..."
cd frontend && ../$PYTHON_BIN -m http.server 8082 &
cd ..

echo "GeoPulse-MCP is running!"
echo "Frontend: http://localhost:8082"
echo "Agent API: http://localhost:8081"
echo "Toolbox:  http://localhost:8080/sse"
echo ""
echo "Press Ctrl+C to stop all background processes (if not handled by trap, use pkill python)."
wait
