#!/bin/bash
set -e

# Configuration
PROJECT_ID="genai-apac-2026-491004"
REGION="asia-southeast1"

echo "[1/3] Deploying GeoPulse-Toolbox (SSE MCP Server)..."
gcloud run deploy geopulse-toolbox --source toolbox/ --project $PROJECT_ID --region $REGION --allow-unauthenticated
TOOLBOX_URL=$(gcloud run services describe geopulse-toolbox --project $PROJECT_ID --region $REGION --format="value(status.url)")

echo "[2/3] Deploying GeoPulse-Agent (ADK Orchestrator)..."
echo "Toolbox URL: $TOOLBOX_URL"
gcloud run deploy geopulse-agent --source agent/ --project $PROJECT_ID --region $REGION --set-env-vars TOOLBOX_URL=$TOOLBOX_URL --allow-unauthenticated
AGENT_URL=$(gcloud run services describe geopulse-agent --project $PROJECT_ID --region $REGION --format="value(status.url)")

echo "[3/3] Deploying GeoPulse-Dashboard (Nginx Proxy Frontend)..."
echo "Agent URL: $AGENT_URL"
gcloud run deploy geopulse-dashboard --source frontend/ --project $PROJECT_ID --region $REGION --set-env-vars AGENT_URL=$AGENT_URL --allow-unauthenticated

echo ""
echo "[COMPLETE] All GeoPulse services deployed successfully!"
echo "Dashboard URL: $AGENT_URL" # Note: Dashboard url is separate
