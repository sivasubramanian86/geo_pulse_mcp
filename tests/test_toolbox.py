import pytest
from toolbox.main import mcp

@pytest.mark.asyncio
async def test_bigquery_census_data_tool():
    # The tool name in main.py is 'get_population_insights'
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_population_insights" in tool_names

@pytest.mark.asyncio
async def test_mcp_initialization():
    assert mcp.name == "GeoPulse-Toolbox"
