@echo off
setlocal
cd /d "%~dp0.."

:: --- Configuration ---
set PROJECT_ID=genai-apac-2026-491004
set REGION=asia-southeast1

echo [1/3] Deploying GeoPulse-Toolbox (SSE MCP Server)...
cmd.exe /c "gcloud.cmd run deploy geopulse-toolbox --source toolbox/ --project %PROJECT_ID% --region %REGION% --allow-unauthenticated"
for /f "tokens=*" %%i in ('gcloud.cmd run services describe geopulse-toolbox --project %PROJECT_ID% --region %REGION% --format^="value(status.url)"') do set TOOLBOX_URL=%%i

echo [2/3] Deploying GeoPulse-Agent (ADK Orchestrator)...
cmd.exe /c "gcloud.cmd run deploy geopulse-agent --source agent/ --project %PROJECT_ID% --region %REGION% --set-env-vars TOOLBOX_URL=%TOOLBOX_URL% --allow-unauthenticated"
for /f "tokens=*" %%i in ('gcloud.cmd run services describe geopulse-agent --project %PROJECT_ID% --region %REGION% --format^="value(status.url)"') do set AGENT_URL=%%i

echo [3/3] Deploying GeoPulse-Dashboard (Nginx Proxy Frontend)...
cmd.exe /c "gcloud.cmd run deploy geopulse-dashboard --source frontend/ --project %PROJECT_ID% --region %REGION% --set-env-vars AGENT_URL=%AGENT_URL% --allow-unauthenticated"

echo.
echo [COMPLETE] All GeoPulse services deployed successfully!
echo Dashboard URL: https://geopulse-dashboard-967518492968.asia-southeast1.run.app
pause
