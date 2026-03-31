import pytest
from unittest.mock import MagicMock
from agent.app import geo_pulse_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

def test_agent_initialization():
    # Corrected name based on app.py
    assert geo_pulse_agent.name == "GeoPulseAdvisor"
    assert "location intelligence" in geo_pulse_agent.description.lower()

def test_runner_instantiation():
    session_service = InMemorySessionService()
    # ADK 2026 Runner requires app_name when providing agent
    runner = Runner(
        app_name="GeoPulseTestApp",
        agent=geo_pulse_agent, 
        session_service=session_service
    )
    assert runner is not None
