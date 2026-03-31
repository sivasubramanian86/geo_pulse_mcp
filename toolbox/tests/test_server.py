import sys
import os
import pytest

# Add parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import mcp

@pytest.mark.asyncio
async def test_tool_registration():
    """Verify the population tool is correctly registered in MCP."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_population_insights" in tool_names

def test_app_generation():
    """Verify we can generate a Starlette app for Uvicorn/Cloud Run."""
    from starlette.applications import Starlette
    # sse_app is a method in this version, so call it
    app = mcp.sse_app()
    assert isinstance(app, Starlette)
