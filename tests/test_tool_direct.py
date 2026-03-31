import asyncio
import os
from google.cloud import bigquery
from toolbox.main import get_population_insights

async def main():
    os.environ["GOOGLE_CLOUD_PROJECT"] = "genai-apac-2026-491004"
    print("Testing 90210...")
    result1 = await get_population_insights("90210")
    print(f"Result for 90210: {result1}")
    
if __name__ == "__main__":
    asyncio.run(main())
