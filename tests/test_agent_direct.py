import asyncio
import os
from agent.app import geo_pulse_agent, session_service
from google.adk.runners import Runner
from google.genai import types

async def main():
    os.environ["GOOGLE_CLOUD_PROJECT"] = "genai-apac-2026-491004"
    os.environ["GOOGLE_CLOUD_REGION"] = "us-central1"
    os.environ["TOOLBOX_URL"] = "http://localhost:8080"
    
    runner = Runner(
        app_name="GeoPulse",
        agent=geo_pulse_agent,
        session_service=session_service
    )
    
    session_id = "test_123"
    await session_service.create_session(app_name="GeoPulse", user_id="user", session_id=session_id)
    
    message = types.Content(role="user", parts=[types.Part.from_text(text="Analyze 90210")])
    events = runner.run_async(user_id="user", session_id=session_id, new_message=message)
    
    with open("agent_events.log", "w", encoding="utf-8") as f:
        async for event in events:
            f.write(str(event) + "\n")

if __name__ == "__main__":
    asyncio.run(main())
