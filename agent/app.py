"""
GeoPulse-Agent: ADK-powered Orchestrator for Location Intelligence.

This module implements a Google ADK Agent that utilizes Vertex AI (Gemini 2.5 Flash)
and connects to a Remote MCP Toolbox to provide site-selection analysis.
"""

import os
import uuid
import asyncio
import traceback
from typing import Optional, Any

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.cloud import aiplatform

# --- Configuration ---

# Load Toolbox URL from external environment (Cloud Run Service URL)
TOOLBOX_URL: str = os.getenv("TOOLBOX_URL", "http://localhost:8080")
# Model selection: Using Latest Stable Gemini 2.5 Flash (Verified in us-central1)
MODEL_ID: str = "gemini-2.5-flash"
GCP_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "genai-apac-2026-491004")
GCP_LOCATION: str = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# Force google-genai SDK (used by ADK) to use Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = GCP_PROJECT
os.environ["GOOGLE_CLOUD_LOCATION"] = GCP_LOCATION

# --- Agent Definition ---

def create_geopulse_agent() -> Agent:
    """
    Initializes the GeoPulse Strategic Agent.
    """
    aiplatform.init(project=GCP_PROJECT, location=GCP_LOCATION)

    connection_params = SseConnectionParams(url=f"{TOOLBOX_URL}/sse")
    toolbox_toolset = McpToolset(connection_params=connection_params)

    return Agent(
        name="GeoPulseAdvisor",
        model=MODEL_ID, 
        tools=[toolbox_toolset],
        description="A specialist in location intelligence and demographic analysis.",
        instruction="""
            You are a Senior Strategic Advisor at GeoPulse Intelligence.
            Your mission is to provide rigorous, data-driven site-selection advice.
            
            When a user provides a ZIP code or location:
            1. **Data Ingestion**: Fetch demographics using the 'get_population_insights' tool. **IMPORTANT: Always pass the ZIP code as a quoted string (e.g., "90210")** to avoid type-mismatch errors.
            2. **Deep Analysis**: Analyze population density, age distributions, and gender splits.
            3. **Business Strategy**: identify specific business types that thrive in these demographics.
            4. **Synthesis**: Produce a professional report with:
                - [OVERVIEW] of the location.
                - [CORE INSIGHTS] from the data.
                - [STRATEGIC RECOMMENDATION] (at least 3 pros/cons).
            
            Maintain a formal, executive summary tone throughout.
        """
    )

# Global Agent Instance
geo_pulse_agent = create_geopulse_agent()
session_service = InMemorySessionService()

# --- Execution & Local API Server ---

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware

    # Initialize Local Proxy App for Testing Frontend
    app = FastAPI(title="GeoPulse Agent Proxy")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def health_check():
        return {"status": "ok", "service": "GeoPulse Agent Proxy"}

    @app.post("/api/analyze")
    async def analyze(request: Request):
        try:
            data = await request.json()
            # Handle both 'prompt' (frontend) and 'input' (legacy)
            prompt = data.get("prompt") or data.get("input")
            
            if not prompt:
                raise HTTPException(status_code=400, detail="Missing prompt")

            # Toolbox URL is already wired via the global geo_pulse_agent

            import uuid
            session_id = data.get("session_id") or str(uuid.uuid4())
            user_id = data.get("user_id", "default_user")

            # Get or create an ADK session using the robust async pattern in 1.28.0
            session = await session_service.get_session(
                app_name="GeoPulse",
                user_id=user_id,
                session_id=session_id
            )
            if not session:
                session = await session_service.create_session(
                    app_name="GeoPulse",
                    user_id=user_id,
                    session_id=session_id
                )

            print(f"Executing reasoning loop for prompt: {prompt}")
            
            # The Runner handles the message orchestration with tool support
            runner = Runner(
                app_name="GeoPulse",
                agent=geo_pulse_agent,
                session_service=session_service
            )

            # Use content type for 1.28.0 structure
            from google.genai import types
            message_content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

            # ADK 1.28.0 handles the internal async resolution of tools natively
            events = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message_content
            )
            
            final_text = ""
            async for event in events:
                print(f"AGENT_EVENT_DUMP: {event}")
                if hasattr(event, 'text') and event.text:
                    final_text += event.text
                elif hasattr(event, 'content') and hasattr(event.content, 'text') and event.content.text:
                    final_text += event.content.text
                elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_text += part.text

            return {"analysis": final_text.strip() or "Analysis completed (no text returned)."}

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"!!! CRITICAL AGENT ERROR:\n{error_trace}")
            return {
                "error": str(e), 
                "analysis": f"The agent encountered a technical error: {str(e)}.",
                "trace": error_trace
            }

    # Start the local server
    port = int(os.getenv("PORT", 8081))
    print(f"GeoPulse Agent Proxy starting on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
