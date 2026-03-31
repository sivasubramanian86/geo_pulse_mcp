"""
GeoPulse-Toolbox: MCP Server for Location Intelligence.

This module implements a FastMCP server that exposes BigQuery-backed 
demographic insights as tools for AI agents.
"""

import os
import uvicorn
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery

# --- Configuration & Initialization ---

# Initialize FastMCP Server
mcp = FastMCP("GeoPulse-Toolbox")

# --- FastMCP to Starlette SSE Plumbing ---
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.routing import Route, Mount

sse = SseServerTransport("/messages/")

async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )

from starlette.responses import JSONResponse

async def health_check(request):
    return JSONResponse({"status": "ok", "service": "GeoPulse-Toolbox (MCP Server)"})

# Starlette App definition
app = Starlette(
    routes=[
        Route("/", endpoint=health_check),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

# Initialize BigQuery Client
bq_client = bigquery.Client()

# --- MCP Tools ---

@mcp.tool()
async def get_population_insights(zip_code: Any) -> str:
    """
    Fetches demographic data for a given ZIP code using BigQuery Public Datasets.
    
    Args:
        zip_code (Any): The 5-digit US ZIP code to analyze (Accepts string or int).
        
    Returns:
        str: A formatted string containing population and median age details.
    """
    # Coerce to string to accommodate LLMs that provide numbers instead of strings
    zip_code_str = str(zip_code).strip()
    
    if not zip_code_str.isdigit() or len(zip_code_str) != 5:
        return f"Error: Invalid ZIP code format ('{zip_code_str}'). Please provide a 5-digit number."

    query = f"""
        SELECT 
            SUM(IF(gender IS NULL AND minimum_age IS NULL, population, 0)) AS population,
            SUM(IF(gender = 'male' AND minimum_age IS NULL, population, 0)) AS male_pop,
            SUM(IF(gender = 'female' AND minimum_age IS NULL, population, 0)) AS female_pop,
            'N/A' as median_age
        FROM `bigquery-public-data.census_bureau_usa.population_by_zip_2010`
        WHERE zipcode = '{zip_code_str}'
    """
    print(f"[TOOLBOX DEBUG] Executing SQL: {query}")
    
    try:
        query_job = bq_client.query(query)
        results = query_job.result()
        
        rows = list(results)
        print(f"[TOOLBOX DEBUG] Rows found: {len(rows)}")
        if not rows or rows[0].population is None:
            return f"No demographic data found for ZIP {zip_code} in the 2010 Census dataset."
            
        row = rows[0]
        return (
            f"**Demographic Report for ZIP {zip_code}:**\n"
            f"- Total Population: {int(row.population):,}\n"
            f"- Median Age: {row.median_age}\n"
            f"- Gender Distribution: {int(row.male_pop):,} Male / {int(row.female_pop):,} Female."
        )
    except Exception as e:
        import traceback
        with open("error_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Exception occurred for ZIP {zip_code}:\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n---\n")
        return f"Error querying BigQuery: {str(e)}"

# --- Server Lifecycle ---

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"Starting GeoPulse MCP Toolbox (SSE) on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
